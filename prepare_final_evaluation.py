"""Audit the fixed data split, reconstruct the frozen ensemble, and score it."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
import joblib
import numpy as np
import pandas as pd
from models import FrozenSoftVotingClassifier
from evaluation import evaluate, per_class_recall


def main():
    out = ROOT / 'results' / 'final'
    out.mkdir(exist_ok=True)
    model_dir = ROOT / 'results' / 'models'
    meta = json.loads((model_dir / 'split_multiclass_seed42.json').read_text())
    df = pd.read_parquet(ROOT / 'data/processed/unsw_clean.parquet')
    features = meta['feature_names']
    test = df.loc[meta['test_index']]
    train = df.drop(index=meta['test_index'])
    assert len(set(meta['test_index'])) == len(test)
    assert len(test) + len(train) == len(df)
    assert not set(test.index) & set(train.index)
    # Check duplicate feature vectors after identifier removal, not just rows.
    train_hash = pd.util.hash_pandas_object(train[features], index=False)
    test_hash = pd.util.hash_pandas_object(test[features], index=False)
    overlap = test_hash.isin(set(train_hash))
    audit = dict(rows=len(df), features=len(features), train_rows=len(train),
                 test_rows=len(test), seed=42,
                 overlapping_test_feature_vectors=int(overlap.sum()),
                 overlapping_test_fraction=float(overlap.mean()),
                 split='random stratified flow split; not temporal or host-disjoint',
                 class_counts=df['attack'].value_counts().to_dict())
    full_hash = pd.util.hash_pandas_object(df[features], index=False)
    audit['unique_feature_groups'] = int(full_hash.nunique())
    audit['groups_with_multiple_labels'] = int(df.assign(group=full_hash).groupby('group')['attack'].nunique().gt(1).sum())
    audit['label_inconsistencies'] = int(((df['attack'] != 'Benign').astype(int) != df['label']).sum())
    (out / 'data_audit.json').write_text(json.dumps(audit, indent=2))
    print(json.dumps(audit, indent=2), flush=True)
    names = ['DecisionTree', 'RandomForest', 'XGBoost']
    members = {n: joblib.load(model_dir / f'{n}_multiclass_seed42.joblib') for n in names}
    ensemble = FrozenSoftVotingClassifier(members)
    path = model_dir / 'SoftVotingEnsemble_multiclass_seed42.joblib'
    if path.exists():
        old = joblib.load(path)
        np.testing.assert_allclose(old.predict_proba(test[features].iloc[:100]),
                                   ensemble.predict_proba(test[features].iloc[:100]))
    else:
        joblib.dump(ensemble, path)
    codes = pd.Categorical(test['attack'], categories=meta['class_names']).codes
    rows = []
    for name, clf in {**members, 'SoftVotingEnsemble': ensemble}.items():
        probs = clf.predict_proba(test[features])
        pred = probs.argmax(axis=1)
        rows.append(evaluate(codes, pred, probs, np.arange(len(meta['class_names'])),
                             meta['benign_label'], name))
        per_class_recall(codes, pred, meta['class_names']).to_csv(out / f'per_class_{name}.csv', index=False)
        # Explicit sensitivity analysis; this does not retrain without duplicates.
        keep = ~overlap.to_numpy()
        clean = evaluate(codes[keep], pred[keep], probs[keep], np.arange(len(meta['class_names'])),
                         meta['benign_label'], name)
        clean['n_test'] = int(keep.sum())
        pd.DataFrame([clean]).to_csv(out / f'nonoverlap_{name}.csv', index=False)
        print(name, rows[-1]['macro_f1'], flush=True)
    pd.DataFrame(rows).to_csv(out / 'baselines_seed42.csv', index=False)
    (out / 'ensemble.json').write_text(json.dumps({'members': names, 'seed': 42,
        'training': 'existing frozen checkpoints, no refitting', 'model_file': str(path.relative_to(ROOT))}, indent=2))


if __name__ == '__main__':
    main()
