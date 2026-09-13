"""Training-only RF weighting/undersampling ablation with untouched test sets."""
from pathlib import Path
import json,time
import numpy as np,pandas as pd,joblib
from sklearn.base import clone
from imblearn.under_sampling import RandomUnderSampler
from study.representation import log_values
from study.train import metrics
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'results/study/imbalance';out.mkdir(exist_ok=True);rows=[]
    for source in ['unsw','ids2018']:
        base=ROOT/f'results/study/{source}/binary/seed42/RandomForest'
        meta=json.loads((base/'complete.json').read_text());features=meta['features'];trained=joblib.load(base/'predictor.joblib')
        d=pd.read_parquet(ROOT/f'data/study/{source}/seed42/train.parquet');x=log_values(d[features].to_numpy());y=d.label.to_numpy()
        for variant in ['balanced_weights','unweighted','random_undersampling']:
            done=out/f'{source}_{variant}.json'
            if done.exists():rows.extend(json.loads(done.read_text()));continue
            start=time.perf_counter()
            if variant=='balanced_weights':model=trained.model;xt,yt=x,y
            else:
                model=clone(trained.model).set_params(class_weight=None,n_jobs=2)
                xt,yt=RandomUnderSampler(random_state=42).fit_resample(x,y) if variant=='random_undersampling' else (x,y)
                model.fit(xt,yt)
            fit_seconds=time.perf_counter()-start if variant!='balanced_weights' else meta['train_seconds'];values=[]
            for target in ['unsw','ids2018']:
                test=pd.read_parquet(ROOT/f'data/study/{target}/seed42/test.parquet')
                p=model.predict_proba(log_values(test[features].to_numpy()));result,_,_=metrics(test.label.to_numpy(),p,['Benign','Attack'])
                result.update(source=source,target=target,variant=variant,seed=42,train_rows=len(yt),train_class_counts=np.bincount(yt).tolist(),train_seconds=fit_seconds)
                values.append(result)
            done.write_text(json.dumps(values,indent=2));rows.extend(values);print(source,variant,'complete',flush=True)
    pd.DataFrame(rows).to_csv(out/'metrics.csv',index=False)
    lines=['# Training-only imbalance ablation','','Same seed-42 group split and RF hyperparameters; change only class weights or training-row undersampling. Validation and test rows are untouched. Balanced-weight baseline reuses its completed checkpoint. No target-test model selection. Synthetic oversampling is deferred because integer/protocol fields need a justified mixed-feature synthesis policy.','', '| Source | Target | Variant | Train rows | Macro-F1 | False alarm rate |','| --- | --- | --- | --- | --- | --- |']
    for r in rows:lines.append(f"| {r['source']} | {r['target']} | {r['variant']} | {r['train_rows']} | {r['macro_f1']:.6f} | {r['false_alarm_rate']:.6f} |")
    (out/'ANALYSIS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
if __name__=='__main__':main()
