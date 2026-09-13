"""Immutable run directories and small, explicit experiment statistics."""
from datetime import datetime, timezone
import json
import platform
import hashlib
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
from uuid import uuid4

import numpy as np


def file_sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def start_run(root, experiment, model, seed, parameters):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder = Path(root) / 'runs' / f'{experiment}_{model}_seed{seed}_{stamp}_{uuid4().hex[:8]}'
    folder.mkdir(parents=True, exist_ok=False)
    manifest = dict(experiment=experiment, model=model, seed=seed,
                    created_utc=stamp, python=platform.python_version(),
                    parameters=parameters, status='started')
    manifest['packages'] = {}
    for package in ('numpy', 'pandas', 'scipy', 'scikit-learn', 'lime', 'shap', 'xgboost'):
        try:
            manifest['packages'][package] = version(package)
        except PackageNotFoundError:
            manifest['packages'][package] = None
    project = Path(__file__).resolve().parents[1]
    sources = list(project.glob('*.py')) + list((project / 'src').glob('*.py'))
    manifest['source_sha256'] = {
        str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sources
    }
    if 'task' in parameters:
        model_dir = project / 'results' / 'models'
        inputs = [model_dir / f'{model}_{parameters["task"]}_seed{seed}.joblib',
                  model_dir / f'split_{parameters["task"]}_seed{seed}.json',
                  project / 'data' / 'processed' / 'unsw_clean.parquet']
        manifest['input_sha256'] = {
            str(p.relative_to(project)): file_sha256(p)
            for p in inputs if p.exists()
        }
    (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return folder


def finish_run(folder):
    path = folder / 'manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    manifest['status'] = 'complete'
    path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')


def bootstrap_mean_ci(values, seed=42, repeats=2000):
    """Percentile interval over independent instance-level values."""
    values = np.asarray(values, dtype=float)
    if not len(values) or not np.isfinite(values).all():
        raise ValueError('Bootstrap requires finite, nonempty values')
    rng = np.random.default_rng(seed)
    means = [rng.choice(values, size=len(values), replace=True).mean()
             for _ in range(repeats)]
    return tuple(float(v) for v in np.quantile(means, [0.025, 0.975]))
