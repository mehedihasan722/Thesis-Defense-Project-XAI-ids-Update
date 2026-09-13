"""Post-run masking checks for valid LLM explanations, retaining coverage failures."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd,torch,joblib
from transformers import AutoTokenizer,AutoModelForCausalLM
from study.summarize_llm import parse_features
from study.representation import log_values
from study.llm_evaluate import vector
from study.llm_tokens import label_tokens,append_prefix
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'results/study'

def main():
    torch.set_num_threads(2)
    features=json.loads((ROOT/'data/study/manifest.json').read_text())['features']
    downloads=json.loads((BASE/'llm_downloads.json').read_text());all_rows=[];coverage=[]
    for manifest in (BASE/'llm').glob('*/full/manifest.json'):
        meta=json.loads(manifest.read_text())
        if meta['status']!='complete':continue
        cases=[json.loads(l) for l in (manifest.parent/'cases.jsonl').read_text().splitlines()]
        out=manifest.parent/'masking.jsonl';rows=[json.loads(l) for l in out.read_text().splitlines()] if out.exists() else []
        seen={(r['source'],r['target'],r['row'],r['kind']) for r in rows}
        llm=None;tokenizer=None
        for source in ['unsw','ids2018']:
            train=pd.read_parquet(ROOT/f'data/study/{source}/seed42/train.parquet');baseline=np.median(log_values(train.sample(10000,random_state=42)[features].to_numpy()),axis=0)
            detector=joblib.load(BASE/f'{source}/binary/seed42/XGBoost/predictor.joblib')
            for target in ['unsw','ids2018']:
                test=pd.read_parquet(ROOT/f'data/study/{target}/seed42/test.parquet').set_index('_row')
                selected=[r for r in cases if r['source']==source and r['target']==target and 'own_explanation' in r]
                for kind in ['own','detector']:
                    valid=0
                    for r in selected:
                        names,ok=parse_features(r[kind+'_explanation'],features)
                        if not ok:continue
                        valid+=1;key=(source,target,r['row'],kind)
                        if key in seen:continue
                        z=log_values(test.loc[r['row'],features].to_numpy(dtype=float));indices=[features.index(n) for n in names]
                        masked=z.copy();masked[indices]=baseline[indices];vectors=[z,masked];random_sets=[]
                        for seed in [101,202,303]:
                            chosen=np.random.RandomState((r['row']+seed)%2**32).choice(len(features),len(indices),replace=False);rand=z.copy();rand[chosen]=baseline[chosen];vectors.append(rand);random_sets.append(chosen.tolist())
                        if kind=='detector':
                            label=r['detector_label'];scores=detector.predict_encoded(np.array(vectors))[:,label]
                        else:
                            if llm is None:
                                path=downloads[meta['model']]['path'];tokenizer=AutoTokenizer.from_pretrained(path,local_files_only=True,trust_remote_code=False)
                                llm=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,trust_remote_code=False,torch_dtype=torch.float32).eval()
                                label_prefix,ids=label_tokens(tokenizer)
                            label=r['predicted_label'];scores=[]
                            prefix=r['prompt'].rsplit('Flow:',1)[0]+'Flow: '
                            for values in vectors:
                                prompt=prefix+vector(values)+' Label:';tokens=tokenizer.apply_chat_template([{'role':'user','content':prompt}],add_generation_prompt=True,return_tensors='pt')
                                tokens=append_prefix(tokens,label_prefix)
                                assert tokens.shape[1]<=min(int(getattr(llm.config,'max_position_embeddings',2048)),8192)
                                with torch.inference_mode():score=llm(input_ids=tokens,logits_to_keep=1).logits[0,-1,ids].softmax(dim=0).numpy()
                                scores.append(float(score[label]))
                            assert abs(scores[0]-r['scores'][label])<1e-4,'Original LLM score failed replay'
                        record=dict(model=meta['model'],source=source,target=target,row=r['row'],kind=kind,features=names,random_indices=random_sets,original_score=float(scores[0]),named_drop=float(scores[0]-scores[1]),random_drop=float(scores[0]-np.mean(scores[2:])))
                        record['advantage']=record['named_drop']-record['random_drop'];rows.append(record)
                        temporary=out.with_suffix('.tmp');temporary.write_text(''.join(json.dumps(x)+'\n' for x in rows));temporary.replace(out)
                    coverage.append(dict(model=meta['model'],source=source,target=target,kind=kind,total=len(selected),valid=valid))
        all_rows.extend(rows)
        if llm is not None:del llm
    if all_rows:pd.DataFrame(all_rows).to_csv(BASE/'llm/explanation_masking.csv',index=False)
    pd.DataFrame(coverage).to_csv(BASE/'llm/masking_coverage.csv',index=False)
    lines=['# Explanation masking checks','','Only valid JSON explanations with 1–3 exact feature names enter masking evaluation. Invalid outputs remain failures in the coverage denominator; conditional masking scores do not describe invalid cases. A selected set is compared with three random sets of equal size, using a fixed source-training-background median. Original predicted class is fixed. LLM original scores must replay within 1e-4.','', 'Named-feature removal advantage is a perturbation sensitivity proxy, not causal validity. Detector explanations are checked against the frozen XGBoost; own explanations against the generating LLM. These scores use different models and are not interchangeable.','', '| Model | Source | Target | Kind | Valid / total |','| --- | --- | --- | --- | --- |']
    for r in coverage:lines.append(f"| {r['model']} | {r['source']} | {r['target']} | {r['kind']} | {r['valid']} / {r['total']} |")
    if all_rows:
        summary=pd.DataFrame(all_rows).groupby(['model','source','target','kind']).agg(n=('advantage','size'),mean_advantage=('advantage','mean'),mean_named_drop=('named_drop','mean'),mean_random_drop=('random_drop','mean')).reset_index()
        summary.to_csv(BASE/'llm/masking_summary.csv',index=False)
        lines.extend(['','## Conditional masking results','','These means apply only to valid explanations. After excluding invalid outputs, the retained subset need not be class-balanced. Do not compare these conditional means without the coverage table.','', '| Model | Source | Target | Kind | Valid cases | Named-minus-random advantage |','| --- | --- | --- | --- | --- | --- |'])
        for r in summary.to_dict('records'):lines.append(f"| {r['model']} | {r['source']} | {r['target']} | {r['kind']} | {r['n']} | {r['mean_advantage']:.6f} |")
    (BASE/'llm/MASKING_ANALYSIS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
if __name__=='__main__':main()


