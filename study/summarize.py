"""Publish only completed-model measurements as an explicitly partial Markdown table."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
    rows=[]
    for done in (ROOT/'results/study').glob('*/*/seed*/*/complete.json'):
        for path in done.parent.glob('metrics_*.json'):
            rows.append(json.loads(path.read_text()))
    out=ROOT/'results/study';d=pd.DataFrame(rows)
    if d.empty:return
    d=d.sort_values(['task','source','seed','model','target'])
    d.to_csv(out/'completed_metrics.csv',index=False)
    lines=['# Expanded study: measured results','',f'Partial snapshot: {len(rows)} completed evaluation cells. Planned classical/neural matrix: 84 fitted configurations, 126 evaluation cells. LLM and explanation-transfer results are not included until executed. No thesis report is generated.','', 'Training uses capped samples after global encoded-feature group partitioning. Source-only preprocessing; frozen binary models are evaluated within and across datasets. Multiclass taxonomies remain dataset-specific. One seed is not a final multi-seed estimate.','', '| Task | Source | Target | Seed | Model | N | Macro-F1 | Balanced accuracy | False alarm rate |','| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in d.to_dict('records'):
        lines.append(f"| {r['task']} | {r['source']} | {r['target']} | {r['seed']} | {r['model']} | {r['n']} | {r['macro_f1']:.6f} | {r['balanced_accuracy']:.6f} | {r['false_alarm_rate']:.6f} |")
    lines.extend(['','## Analysis boundaries','','Cross-dataset degradation measures the combined effect of domain differences under this protocol; it does not identify its cause. Explanation transfer requires separate stability, feature-ranking and random-controlled masking evaluations. Historical stability/faithfulness audit is in audit/ANALYSIS.md.','', '## Reproduction','','Run `.venv-study/Scripts/python.exe -m study.run_training`, then `.venv-study/Scripts/python.exe -m study.summarize`. Only folders with complete.json contribute. Partial model outputs are excluded.'])
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Saved {len(rows)} completed evaluation cells')
if __name__=='__main__':main()
