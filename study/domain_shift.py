"""Descriptive encoded-feature domain shift; no target-driven training changes."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.stats import ks_2samp,wasserstein_distance
from study.representation import log_values
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'results/study'
def main():
    features=json.loads((ROOT/'data/study/manifest.json').read_text())['features'];samples={}
    for dataset in ['unsw','ids2018']:
        frame=pd.read_parquet(ROOT/f'data/study/{dataset}/seed42/test.parquet').sample(20000,random_state=42)
        samples[dataset]=log_values(frame[features].to_numpy())
    rows=[]
    for i,name in enumerate(features):
        a,b=samples['unsw'][:,i],samples['ids2018'][:,i]
        rows.append(dict(feature=name,ks_distance=float(ks_2samp(a,b,method='asymp').statistic),wasserstein_encoded=float(wasserstein_distance(a,b)),unsw_median=float(np.median(a)),ids2018_median=float(np.median(b)),unsw_zero_fraction=float((a==0).mean()),ids2018_zero_fraction=float((b==0).mean())))
    d=pd.DataFrame(rows).sort_values('ks_distance',ascending=False);out=BASE/'shift';out.mkdir(exist_ok=True);d.to_csv(out/'feature_shift.csv',index=False)
    lines=['# Cross-dataset feature shift','','Descriptive comparison of 20000 sampled seed-42 held-out rows per dataset in the shared signed-log encoding. KS distance measures marginal distribution difference (0 identical empirical CDFs, 1 maximal separation). No significance test or causal attribution is claimed; mixtures of attacks and benign traffic differ, and correlated or duplicate rows are not independent observations. This analysis does not tune training or thresholds.','', '| Feature | KS distance | Wasserstein (encoded units) | UNSW median | IDS2018 median |','| --- | --- | --- | --- | --- |']
    for r in d.to_dict('records'):lines.append(f"| {r['feature']} | {r['ks_distance']:.4f} | {r['wasserstein_encoded']:.4f} | {r['unsw_median']:.4f} | {r['ids2018_median']:.4f} |")
    (out/'ANALYSIS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print(d.head(5).to_string(index=False))
if __name__=='__main__':main()
