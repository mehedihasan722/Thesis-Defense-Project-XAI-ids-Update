"""Replay saved original probabilities; do not claim unavailable masking ranks."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd,joblib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))

def main():
    meta=json.loads((ROOT/'results/models/split_multiclass_seed42.json').read_text())
    features=meta['feature_names']
    data=pd.read_parquet(ROOT/'data/processed/unsw_clean.parquet',columns=features)
    out=ROOT/'results/study/audit';rows=[]
    for name in ['DecisionTree','RandomForest','XGBoost']:
        path=ROOT/f'results/models/{name}_multiclass_seed42.joblib'
        model=joblib.load(path)
        old=pd.read_csv(ROOT/f'results/tables/rq2_faithfulness_{name}_multiclass.csv')
        cases=old.groupby('instance',as_index=False).p_original.first()
        x=data.loc[cases.instance,features]
        p=model.predict_proba(x)
        cases['replayed_probability']=p.max(axis=1)
        cases['replayed_class']=np.asarray(model.classes_)[p.argmax(axis=1)]
        cases['absolute_error']=abs(cases.p_original-cases.replayed_probability)
        cases.to_csv(out/f'{name}_original_probability_replay.csv',index=False)
        rows.append(dict(model=name,n=len(cases),max_error=float(cases.absolute_error.max()),mismatch_over_1e_6=int((cases.absolute_error>1e-6).sum()),model_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    pd.DataFrame(rows).to_csv(out/'original_probability_replay.csv',index=False)
    text=['# Historical prediction replay','', 'Replayed the original maximum class probability for every unique case in the three original RQ2 files using the currently available historical checkpoints. A matching original probability does not validate masked predictions: historical feature rankings were not stored in those CSVs. Full masking replay requires regenerating explanations under the exact historical configuration, whose provenance is incomplete.','', '| Model | Cases | Maximum absolute error | Errors above 1e-6 |','| --- | --- | --- | --- |']
    for r in rows:text.append(f"| {r['model']} | {r['n']} | {r['max_error']:.9g} | {r['mismatch_over_1e_6']} |")
    (out/'REPLAY.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(pd.DataFrame(rows).to_string(index=False))
if __name__=='__main__':main()
