"""Post-hoc sensitivity to source baseline and signed versus absolute ranking."""
from pathlib import Path
import json
import numpy as np,pandas as pd,joblib,torch
from study.representation import log_values
from study.xai_transfer import effects
from study.summarize_xai import stratified_bootstrap
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'results/study'
def main():
    torch.set_num_threads(2);rows=[]
    for manifest in (BASE/'xai').glob('*/*/manifest.json'):
        meta=json.loads(manifest.read_text())
        if meta['status']!='complete':continue
        source,model=meta['source'],meta['model'];features=meta['features']
        predictor=joblib.load(BASE/f'{source}/binary/seed42/{model}/predictor.joblib')
        training=pd.read_parquet(ROOT/f'data/study/{source}/seed42/train.parquet').sample(10000,random_state=42)
        background=log_values(training[features].to_numpy());baselines={'median':np.median(background,axis=0),'mean':background.mean(axis=0)}
        np.testing.assert_allclose(baselines['median'],meta['baseline'])
        cases=[json.loads(l) for l in (manifest.parent/'cases.jsonl').read_text().splitlines()]
        for target in ['unsw','ids2018']:
            test=pd.read_parquet(ROOT/f'data/study/{target}/seed42/test.parquet').set_index('_row')
            for case in [r for r in cases if r['target']==target]:
                z=log_values(test.loc[case['row'],features].to_numpy(dtype=float));assert str(int(test.loc[case['row'],'_group']))==case['group']
                for baseline_name,baseline in baselines.items():
                    for ranking_name in ['absolute','signed_descending']:
                        deltas=[];gaps=[]
                        for run in case['runs']:
                            ranking=run['ranking'] if ranking_name=='absolute' else np.argsort(-np.asarray(run['weights']),kind='stable').tolist()
                            drop,gap=effects(predictor.predict_encoded,z,ranking,baseline,case['predicted_label'])
                            random,_=effects(predictor.predict_encoded,z,run['random_ranking'],baseline,case['predicted_label'])
                            if baseline_name=='median' and ranking_name=='absolute':np.testing.assert_allclose(drop,run['removal_drop'],atol=1e-6)
                            deltas.append(np.mean(drop)-np.mean(random));gaps.append(np.mean(gap))
                        rows.append(dict(source=source,target=target,model=model,row=case['row'],true_label=case['true_label'],baseline=baseline_name,ranking=ranking_name,advantage=float(np.mean(deltas)),sufficiency_gap=float(np.mean(gaps))))
        print(source,model,'sensitivity complete',flush=True)
    out=BASE/'xai/sensitivity';out.mkdir(exist_ok=True);d=pd.DataFrame(rows);d.to_csv(out/'cases.csv',index=False);summary=[]
    for key,g in d.groupby(['source','target','model','baseline','ranking']):
        low,high=stratified_bootstrap(g.advantage,g.true_label);r=dict(zip(['source','target','model','baseline','ranking'],key));r.update(n=len(g),advantage=g.advantage.mean(),ci95_low=low,ci95_high=high,sufficiency_gap=g.sufficiency_gap.mean());summary.append(r)
    pd.DataFrame(summary).to_csv(out/'summary.csv',index=False)
    lines=['# Masking sensitivity analysis','','Post-hoc robustness check prompted by the stability/faithfulness concern. Reuses all original LIME weights, cases and random rankings; no retraining or test-driven model selection. Compare source-background mean versus median and descending signed weights versus absolute magnitude. The original median/absolute removal curves replay within 1e-6.','', 'Signed descending prioritizes positive evidence but can include nonpositive features when fewer than k positive weights exist. This is not a positive-only ranking. All controls mask the same k. Bootstrap intervals resample 20 case groups by class after averaging LIME seeds.','', '| Source | Target | Model | Baseline | Ranking | LIME minus random | 95% interval |','| --- | --- | --- | --- | --- | --- | --- |']
    for r in summary:lines.append(f"| {r['source']} | {r['target']} | {r['model']} | {r['baseline']} | {r['ranking']} | {r['advantage']:.4f} | [{r['ci95_low']:.4f}, {r['ci95_high']:.4f}] |")
    lines.extend(['','These are conditional masking results. Baseline and ranking choices can change measured relevance without changing the underlying classifier or LIME seed stability. Neither choice is a causal ground-truth oracle. Preserve all four variants; do not select only the variant that matches a desired conclusion.'])
    (out/'ANALYSIS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
if __name__=='__main__':main()
