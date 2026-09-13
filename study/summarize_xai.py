"""RQ3 aggregation with class-stratified, instance-level bootstrap intervals."""
from pathlib import Path
import json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'results/study'

def stratified_bootstrap(values,labels,repeats=5000,seed=42):
    values=np.asarray(values);labels=np.asarray(labels);rng=np.random.RandomState(seed);draws=[]
    for label in np.unique(labels):
        group=values[labels==label];draws.append(group[rng.randint(0,len(group),size=(repeats,len(group)))])
    means=np.concatenate(draws,axis=1).mean(axis=1)
    return np.quantile(means,[.025,.975]).tolist()

def main():
    rows=[]
    for manifest in (BASE/'xai').glob('*/*/manifest.json'):
        meta=json.loads(manifest.read_text())
        if meta['status']!='complete':continue
        cases=[json.loads(l) for l in (manifest.parent/'cases.jsonl').read_text().splitlines()]
        for target in ['unsw','ids2018']:
            selected=[r for r in cases if r['target']==target]
            assert len(selected)==20 and len({r['group'] for r in selected})==20
            labels=[r['true_label'] for r in selected]
            advantage=np.array([np.mean([np.mean(run['removal_drop'])-np.mean(run['random_removal_drop']) for run in r['runs']]) for r in selected])
            stability=np.array([r['jaccard5'] for r in selected]);low,high=stratified_bootstrap(advantage,labels)
            rows.append(dict(source=meta['source'],target=target,model=meta['model'],training_seed=42,n=20,lime_seeds=3,advantage_mean=float(advantage.mean()),ci95_low=low,ci95_high=high,jaccard5_mean=float(stability.mean())))
    d=pd.DataFrame(rows);d.to_csv(BASE/'xai/aggregate.csv',index=False)
    lines=['# RQ3 explanation-transfer analysis','','Each row uses 20 balanced unique feature groups and a frozen seed-42 detector. LIME runs are first averaged within each instance. Percentile bootstrap intervals resample the 10 benign and 10 attack groups separately (5000 repeats), preserving the balanced cohort. They are conditional on this model and small cohort, not across-training-seed uncertainty or causal confidence intervals.','', '| Source | Target | Model | Jaccard@5 | LIME minus random drop | 95% bootstrap interval |','| --- | --- | --- | --- | --- | --- |']
    for r in rows:lines.append(f"| {r['source']} | {r['target']} | {r['model']} | {r['jaccard5_mean']:.4f} | {r['advantage_mean']:.4f} | [{r['ci95_low']:.4f}, {r['ci95_high']:.4f}] |")
    lines.extend(['','## Interpretation','','Positive advantage means LIME-ranked masks reduce the original predicted-class score more than matched-size random masks, under the fixed source-median baseline. A confidence interval crossing zero does not establish superiority. Negative values and inverse stability relationships are preserved, not treated as errors to be removed. The 14-model comparison is exploratory; intervals are not multiplicity-adjusted.','', 'Ranking absolute LIME weights can select both supporting and opposing evidence. Source-median replacements can leave the observed flow distribution. These limitations constrain the term faithfulness: this is a masking sensitivity proxy, not ground-truth explanation correctness.','', '![RQ3 domain shifts](../figures/03_explanation_transfer.png)','', 'Arrows connect different domain cohorts, not paired instances.'])
    (BASE/'xai/ANALYSIS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print(f'Summarized {len(rows)} RQ3 domain evaluations')
if __name__=='__main__':main()
