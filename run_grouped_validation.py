"""Hold out complete identical-feature groups for a leakage sensitivity check."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import LabelEncoder
from models import build_models, FrozenSoftVotingClassifier
from evaluation import evaluate, per_class_recall


def main():
    out = ROOT / 'results/final/grouped'
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(ROOT / 'data/processed/unsw_clean.parquet')
    X = df.drop(columns=['attack', 'label'])
    le = LabelEncoder().fit(df['attack'])
    y = le.transform(df['attack'])
    groups = pd.util.hash_pandas_object(X, index=False).to_numpy()
    # Equal groups are defined by all retained features; no label is used in hashing.
    rows = []
    for seed in [42, 7, 1337]:
        seed_out = out / f'seed{seed}'
        seed_out.mkdir(exist_ok=True)
        if (seed_out / 'complete.json').exists():
            rows.extend(pd.read_csv(seed_out / 'metrics.csv').to_dict('records'))
            continue
        tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed).split(X, y, groups))
        assert not set(groups[tr]) & set(groups[te])
        assert set(np.unique(y[tr])) == set(np.unique(y))
        assert set(np.unique(y[te])) == set(np.unique(y))
        meta = {'seed': seed, 'split': 'GroupShuffleSplit on hash of all retained features',
                'train_rows': len(tr), 'test_rows': len(te), 'train_groups': len(set(groups[tr])),
                'test_groups': len(set(groups[te])), 'overlapping_groups': 0,
                'class_names': le.classes_.tolist(),
                'test_class_counts': df.iloc[te]['attack'].value_counts().to_dict()}
        (seed_out / 'split.json').write_text(json.dumps(meta, indent=2))
        models = build_models('multiclass', len(le.classes_), seed=seed, include_svm=False)
        seed_rows = []
        for name, clf in models.items():
            print('TRAIN', seed, name, len(tr), flush=True)
            t = time.time()
            clf.fit(X.iloc[tr], y[tr])
            elapsed = time.time() - t
            p = clf.predict_proba(X.iloc[te])
            row = evaluate(y[te], p.argmax(axis=1), p, np.arange(len(le.classes_)),
                           int(le.transform(['Benign'])[0]), name)
            row.update(seed=seed, train_time_s=elapsed, n_test=len(te))
            seed_rows.append(row)
            per_class_recall(y[te], p.argmax(axis=1), le.classes_).to_csv(seed_out / f'per_class_{name}.csv', index=False)
            joblib.dump(clf, seed_out / f'{name}.joblib')
            print('DONE', seed, name, row['macro_f1'], flush=True)
        ensemble = FrozenSoftVotingClassifier(models)
        p = ensemble.predict_proba(X.iloc[te])
        row = evaluate(y[te], p.argmax(axis=1), p, np.arange(len(le.classes_)),
                       int(le.transform(['Benign'])[0]), 'SoftVotingEnsemble')
        row.update(seed=seed, train_time_s=sum(r['train_time_s'] for r in seed_rows), n_test=len(te))
        seed_rows.append(row)
        per_class_recall(y[te], p.argmax(axis=1), le.classes_).to_csv(seed_out / 'per_class_SoftVotingEnsemble.csv', index=False)
        pd.DataFrame(seed_rows).to_csv(seed_out / 'metrics.csv', index=False)
        rows.extend(seed_rows)
        (seed_out / 'complete.json').write_text(json.dumps({'status': 'complete'}))
    pd.DataFrame(rows).to_csv(out / 'metrics.csv', index=False)


if __name__ == '__main__':
    main()
