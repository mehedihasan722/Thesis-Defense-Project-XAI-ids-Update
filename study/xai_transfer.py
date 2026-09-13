"""Auditable seed-42 LIME transfer pilot; full per-case evidence and recovery."""
from pathlib import Path
import argparse,json,hashlib,itertools
import numpy as np,pandas as pd,torch,joblib
from scipy.stats import spearmanr
from lime.lime_tabular import LimeTabularExplainer
from study.representation import log_values
ROOT=Path(__file__).resolve().parents[1]

def cohort(frame,n=20):
    d=frame.drop_duplicates('_group')
    return pd.concat([d[d.label==c].sample(n//2,random_state=42) for c in [0,1]]).sort_values('_row')

def effects(predict,z,ranking,baseline,label,ks=(1,2,3,4,5)):
    original=predict(z[None])[0,label];masked=[];kept=[]
    for k in ks:
        a=z.copy();a[ranking[:k]]=baseline[ranking[:k]];masked.append(a)
        b=baseline.copy();b[ranking[:k]]=z[ranking[:k]];kept.append(b)
    p=predict(np.array(masked+kept))[:,label]
    return (original-p[:len(ks)]).tolist(),(original-p[len(ks):]).tolist()

def main(source,model):
    torch.set_num_threads(2)
    folder=ROOT/f'results/study/{source}/binary/seed42/{model}'
    done=json.loads((folder/'complete.json').read_text())
    predictor=joblib.load(folder/'predictor.joblib');features=done['features']
    train=pd.read_parquet(ROOT/f'data/study/{source}/seed42/train.parquet')
    background=log_values(train.sample(10000,random_state=42)[features].to_numpy())
    baseline=np.median(background,axis=0)
    out=ROOT/f'results/study/xai/{source}/{model}';out.mkdir(parents=True,exist_ok=True)
    signature=hashlib.sha256((Path(__file__).read_text()+done['signature']).encode()).hexdigest()
    manifest=out/'manifest.json'
    if manifest.exists():assert json.loads(manifest.read_text())['signature']==signature,'Changed XAI protocol'
    meta=dict(signature=signature,source=source,model=model,training_seed=42,cases_per_target=20,lime_samples=5000,lime_seeds=[101,202,303],features=features,baseline=baseline.tolist(),baseline_method='median of fixed source training background, 10000 rows',status='running')
    manifest.write_text(json.dumps(meta,indent=2))
    path=out/'cases.jsonl';records=[json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    completed={(r['target'],r['row']) for r in records}
    for target in ['unsw','ids2018']:
        cases=cohort(pd.read_parquet(ROOT/f'data/study/{target}/seed42/test.parquet'))
        for _,case in cases.iterrows():
            row=int(case['_row'])
            if (target,row) in completed:continue
            z=log_values(case[features].to_numpy(dtype=float));label=int(predictor.predict_encoded(z[None]).argmax())
            runs=[]
            for seed in [101,202,303]:
                rng_seed=int((row+seed)%2**32)
                explainer=LimeTabularExplainer(background,feature_names=features,class_names=['Benign','Attack'],discretize_continuous=True,random_state=rng_seed,mode='classification')
                exp=explainer.explain_instance(z,predictor.predict_encoded,labels=(label,),num_features=len(features),num_samples=5000)
                weights=np.zeros(len(features))
                for i,w in exp.as_map()[label]:weights[i]=w
                ranking=np.argsort(-abs(weights),kind='stable').tolist()
                random=np.random.RandomState(rng_seed).permutation(len(features)).tolist()
                drop,gap=effects(predictor.predict_encoded,z,ranking,baseline,label)
                rand_drop,_=effects(predictor.predict_encoded,z,random,baseline,label)
                runs.append(dict(seed=seed,weights=weights.tolist(),ranking=ranking,random_ranking=random,removal_drop=drop,sufficiency_gap=gap,random_removal_drop=rand_drop,local_surrogate_r2=float(exp.score)))
            tops=[set(r['ranking'][:5]) for r in runs]
            stability=float(np.mean([len(a&b)/len(a|b) for a,b in itertools.combinations(tops,2)]))
            record=dict(target=target,row=row,group=str(int(case['_group'])),true_label=int(case.label),predicted_label=label,jaccard5=stability,runs=runs)
            temporary=out/'cases.tmp.jsonl'
            records.append(record)
            temporary.write_text(''.join(json.dumps(r)+'\n' for r in records));temporary.replace(path)
            print(source,model,target,row,'saved',flush=True)
    summaries=[];importance={}
    for target in ['unsw','ids2018']:
        selected=[r for r in records if r['target']==target]
        importance[target]=np.mean([np.abs(run['weights']) for r in selected for run in r['runs']],axis=0)
        advantage=[np.mean([np.mean(run['removal_drop'])-np.mean(run['random_removal_drop']) for run in r['runs']]) for r in selected]
        summaries.append(dict(target=target,n=len(selected),jaccard5=float(np.mean([r['jaccard5'] for r in selected])),paired_random_advantage=float(np.mean(advantage))))
    rho=float(spearmanr(importance['unsw'],importance['ids2018']).statistic)
    pd.DataFrame(summaries).to_csv(out/'summary.csv',index=False)
    text=['# Frozen-model explanation transfer pilot','','| Target | Cases | Jaccard@5 | LIME minus random removal drop |','| --- | --- | --- | --- |']
    for r in summaries:text.append(f"| {r['target']} | {r['n']} | {r['jaccard5']:.6f} | {r['paired_random_advantage']:.6f} |")
    text.extend(['',f'Across-domain mean absolute LIME importance Spearman: {rho:.6f}.','', 'Twenty balanced unique feature groups per domain; one training seed. Different domains contain different instances: rank drift is distributional, not a paired-instance correctness test. Removal drop is higher-is-larger effect; sufficiency gap is lower-is-better retention. Absolute-weight rankings include opposing evidence. Median masking can create unrealistic flows. This pilot does not establish causal explanation validity.'])
    (out/'ANALYSIS.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    meta['status']='complete';manifest.write_text(json.dumps(meta,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',choices=['unsw','ids2018'],required=True);ap.add_argument('--model',required=True);main(**vars(ap.parse_args()))
