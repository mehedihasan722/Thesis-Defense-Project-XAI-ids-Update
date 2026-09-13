"""Source-validation-only temperature calibration; frozen cross-domain tests."""
from pathlib import Path
import json
import numpy as np,pandas as pd,joblib,torch
from scipy.optimize import minimize_scalar
from scipy.special import softmax
ROOT=Path(__file__).resolve().parents[1]
MODELS=['DecisionTree','RandomForest','XGBoost','SoftVoting','ShallowMLP','DeepMLP','FeatureCNN']
def scaled(p,t):return softmax(np.log(np.clip(p,1e-7,1))/t,axis=1)
def scores(y,p):
    attack=p[:,1];brier=float(np.mean((attack-y)**2));ece=0.
    for i in range(15):
        mask=(attack>=i/15)&((attack<(i+1)/15) if i<14 else (attack<=1))
        if mask.any():ece+=float(mask.mean()*abs(attack[mask].mean()-y[mask].mean()))
    return brier,ece

def main():
    torch.set_num_threads(2);rows=[]
    for source in ['unsw','ids2018']:
        for model in MODELS:
            folder=ROOT/f'results/study/{source}/binary/seed42/{model}'
            meta=json.loads((folder/'complete.json').read_text());features=meta['features']
            predictor=joblib.load(folder/'predictor.joblib')
            validation=pd.read_parquet(ROOT/f'data/study/{source}/seed42/validation.parquet')
            y=validation.label.to_numpy();p=predictor.predict_proba(validation[features].to_numpy())
            fit=minimize_scalar(lambda logt: -np.log(np.clip(scaled(p,np.exp(logt))[np.arange(len(y)),y],1e-12,1)).mean(),bounds=(np.log(.05),np.log(20)),method='bounded')
            assert fit.success;temperature=float(np.exp(fit.x))
            for target in ['unsw','ids2018']:
                test=pd.read_parquet(folder/f'predictions_{target}.parquet');yt=test.true.to_numpy();pt=test[['p_0','p_1']].to_numpy()
                for variant,prob in [('raw',pt),('source_calibrated',scaled(pt,temperature))]:
                    brier,ece=scores(yt,prob)
                    rows.append(dict(source=source,target=target,model=model,seed=42,variant=variant,temperature=temperature,brier=brier,ece15=ece,n=len(yt)))
    out=ROOT/'results/study/calibration';out.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(out/'metrics.csv',index=False)
    lines=['# Source-only calibration extension','','Temperature is fit on source validation negative log likelihood only. Target test labels are used solely for evaluation. Lower Brier and 15-bin positive-class ECE are better. This is a seed-42 extension, not target-adapted calibration. Zero probabilities are clipped to 1e-7 before temperature scaling.','', '| Source | Target | Model | Variant | Brier | ECE15 |','| --- | --- | --- | --- | --- | --- |']
    for r in rows:lines.append(f"| {r['source']} | {r['target']} | {r['model']} | {r['variant']} | {r['brier']:.6f} | {r['ece15']:.6f} |")
    (out/'ANALYSIS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print('Saved calibration results',flush=True)
if __name__=='__main__':main()
