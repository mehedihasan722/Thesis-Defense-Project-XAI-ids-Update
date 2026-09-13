"""Matched-case LLM classification and explanation-format/grounding summaries."""
from pathlib import Path
import json,re
import numpy as np,pandas as pd
from study.train import metrics,MODELS
ROOT=Path(__file__).resolve().parents[1]
def parse_features(text,allowed):
    try:
        clean=text.strip()
        if clean.startswith('```'):clean=re.sub(r'^```(?:json)?\s*|\s*```$','',clean)
        obj=json.loads(clean);features=obj['features']
        if not isinstance(features,list) or not 1<=len(features)<=3:return [],False
        if not all(isinstance(f,str) and f in allowed for f in features) or len(set(features))!=len(features):return [],False
        if not isinstance(obj.get('explanation'),str) or not obj['explanation'].strip():return [],False
        return features,True
    except (ValueError,KeyError,TypeError):return [],False

def main():
    features=json.loads((ROOT/'data/study/manifest.json').read_text())['features'];rows=[];explanations=[]
    for manifest in (ROOT/'results/study/llm').glob('*/full/manifest.json'):
        meta=json.loads(manifest.read_text())
        if meta['status']!='complete':continue
        records=[json.loads(l) for l in (manifest.parent/'cases.jsonl').read_text().splitlines()]
        for source in ['unsw','ids2018']:
            for target in ['unsw','ids2018']:
                subset=[r for r in records if r['source']==source and r['target']==target]
                assert len(subset)==100
                y=np.array([r['true_label'] for r in subset]);p=np.array([r['scores'] for r in subset]);values,_,_=metrics(y,p,['Benign','Attack'])
                rows.append(dict(model=meta['model'],source=source,target=target,cohort='balanced100',**values))
                ids=[r['row'] for r in subset]
                for model in MODELS:
                    path=ROOT/f'results/study/{source}/binary/seed42/{model}/predictions_{target}.parquet'
                    pred=pd.read_parquet(path).set_index('_row').loc[ids]
                    assert np.array_equal(pred.true,y)
                    values,_,_=metrics(y,pred[['p_0','p_1']].to_numpy(),['Benign','Attack'])
                    rows.append(dict(model=model,source=source,target=target,cohort='balanced100',**values))
                for kind in ['own','detector']:
                    cases=[r for r in subset if kind+'_explanation' in r];valid=0;grounded=0
                    for r in cases:
                        names,ok=parse_features(r[kind+'_explanation'],features);valid+=int(ok)
                        if kind=='detector':grounded+=int(ok and set(names)<=set(r['detector_evidence']))
                    explanations.append(dict(model=meta['model'],source=source,target=target,kind=kind,n=len(cases),valid_json_with_allowed_features=valid,evidence_feature_grounded=grounded if kind=='detector' else None))
    if not rows:print('No completed full LLM runs yet');return
    out=ROOT/'results/study/llm';d=pd.DataFrame(rows).drop_duplicates(subset=["model","source","target","cohort"]);d.to_csv(out/'matched_metrics.csv',index=False);pd.DataFrame(explanations).to_csv(out/'explanation_checks.csv',index=False)
    lines=['# Matched-case LLM comparisons','','Only complete 100-case runs are included. Each target cohort has 50 benign and 50 attack unique feature groups; these metrics are not comparable to population-prevalence 80000-case results. LLM scores normalize two label-token likelihoods and are not calibrated attack probabilities.','', '| Model | Source | Target | Macro-F1 | False alarm rate |','| --- | --- | --- | --- | --- |']
    for r in d.to_dict('records'):lines.append(f"| {r['model']} | {r['source']} | {r['target']} | {r['macro_f1']:.6f} | {r['false_alarm_rate']:.6f} |")
    lines.extend(['','Explanation checks count valid JSON with 1-3 exact feature names and nonempty explanation text. Detector grounding checks only whether named features appear in supplied evidence; it does not validate every prose claim, usefulness or causal correctness. All raw outputs and failures remain in per-model cases.jsonl.'])
    (out/'ANALYSIS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
if __name__=='__main__':main()

