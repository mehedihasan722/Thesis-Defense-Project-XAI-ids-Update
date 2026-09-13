"""Independent validation of completed detector evidence and across-seed summaries."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from sklearn.metrics import f1_score,confusion_matrix
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'results/study'

def main():
    audits=[]
    for done in BASE.glob('*/*/seed*/*/complete.json'):
        meta=json.loads(done.read_text());classes=meta['classes']
        for path in done.parent.glob('metrics_*.json'):
            stored=json.loads(path.read_text());target=stored['target'];pred=pd.read_parquet(done.parent/f'predictions_{target}.parquet')
            p=pred[[f'p_{i}' for i in range(len(classes))]].to_numpy();y=pred.true.to_numpy();labels=p.argmax(axis=1)
            assert np.isfinite(p).all() and (p>=0).all() and (p<=1).all()
            assert np.allclose(p.sum(axis=1),1,atol=1e-5)
            assert pred._row.is_unique and len(pred)==stored['n']
            source_test=pd.read_parquet(ROOT/f'data/study/{target}/seed{meta["seed"]}/test.parquet',columns=['_row','label','attack'])
            expected=source_test.label.to_numpy() if meta['task']=='binary' else pd.Categorical(source_test.attack,categories=classes).codes
            assert np.array_equal(source_test._row,pred._row) and np.array_equal(expected,y)
            score=f1_score(y,labels,labels=np.arange(len(classes)),average='macro',zero_division=0)
            assert abs(score-stored['macro_f1'])<1e-10
            expected_cm=confusion_matrix(y,labels,labels=np.arange(len(classes)))
            saved_cm=pd.read_csv(done.parent/f'confusion_{target}.csv',index_col=0).to_numpy()
            assert np.array_equal(expected_cm,saved_cm)
            audits.append(dict(source=meta['dataset'],target=target,task=meta['task'],seed=meta['seed'],model=meta['model'],n=len(y),macro_f1_error=abs(score-stored['macro_f1']),maximum_probability_sum_error=float(abs(p.sum(axis=1)-1).max()),passed=True))
    out=BASE/'validation';out.mkdir(exist_ok=True);pd.DataFrame(audits).to_csv(out/'prediction_audit.csv',index=False)
    (out/'ANALYSIS.md').write_text(f'# Independent detector evidence validation\n\nChecked {len(audits)} completed evaluation cells. Probabilities are finite and normalized; row IDs are unique and exactly aligned with prepared test labels; stored macro-F1 and confusion matrices reproduce. This checks saved evidence consistency, not external validity or causal explanation correctness.\n',encoding='utf-8')
    d=pd.read_csv(BASE/'completed_metrics.csv')
    rows=[]
    for key,g in d.groupby(['task','source','target','model']):
        assert g.seed.is_unique
        row=dict(zip(['task','source','target','model'],key));row['n_seeds']=len(g);row['seeds']=','.join(map(str,sorted(g.seed)))
        for metric in ['macro_f1','balanced_accuracy','false_alarm_rate']:
            row[metric+'_mean']=g[metric].mean();row[metric+'_sd']=g[metric].std(ddof=1) if len(g)>1 else None
        rows.append(row)
    summary=pd.DataFrame(rows);summary.to_csv(BASE/'across_seed_summary.csv',index=False)
    lines=['# Across-seed detector results','','Mean and sample standard deviation across completed training/split seeds. Three seeds are planned; rows with fewer seeds are explicitly incomplete. These are descriptive variations, not population confidence intervals. Binary transfer uses the same frozen source model; native multiclass taxonomies differ across datasets.','', '| Task | Source | Target | Model | Seeds | Macro-F1 mean | SD |','| --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:lines.append(f"| {r['task']} | {r['source']} | {r['target']} | {r['model']} | {r['n_seeds']} | {r['macro_f1_mean']:.6f} | {r['macro_f1_sd'] if r['macro_f1_sd'] is None else format(r['macro_f1_sd'],'.6f')} |")
    lines.extend(['','## Scope','','Reported training uses 200000 sampled rows per source/seed. Extremely rare attack categories may be absent from training or test; per-class files and the data manifest retain that support information. Timing is not a controlled benchmark and interrupted neural fits can have segment-only timing.','', '![Seed-42 transfer heatmap](figures/01_detection_transfer.png)','', 'The heatmap shows seed 42 only; use the table above for across-seed variation.'])
    (BASE/'ACROSS_SEEDS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Validated {len(audits)} completed evaluation cells; summarized {len(rows)} model/direction/task groups')
if __name__=='__main__':main()
