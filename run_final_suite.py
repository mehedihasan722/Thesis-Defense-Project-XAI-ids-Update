"""Resumable, logged thesis experiment suite. No historical seed-42 retraining."""
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results/final'
OUT.mkdir(exist_ok=True)
LOGS = OUT / 'logs'
LOGS.mkdir(exist_ok=True)


def main():
    jobs = [('prepare', ['prepare_final_evaluation.py'])]
    models = ['DecisionTree', 'XGBoost', 'RandomForest', 'SoftVotingEnsemble']
    for model in models:
        extra = ['--skip-shap'] if model == 'SoftVotingEnsemble' else []
        for mask in ['mean', 'median']:
            jobs.append((f'rq2_{model}_{mask}', ['run_rq2_faithfulness.py', '--model', model,
                '--n-instances', '500', '--num-samples', '5000', '--masking', mask,
                '--lime-seeds', '101', '202', '303', *extra]))
        jobs.append((f'rq4_{model}', ['run_rq4_agreement.py', '--model', model,
            '--n-instances', '300', '--num-samples', '5000', *extra]))
    jobs.append(('rq1_SoftVotingEnsemble', ['run_rq1_stability.py', '--model', 'SoftVotingEnsemble',
        '--n-instances', '1000', '--num-samples', '5000']))
    for seed in [7, 1337]:
        jobs.append((f'baselines_seed{seed}', ['run_baselines.py', '--task', 'multiclass',
                                            '--no-svm', '--seed', str(seed)]))
    status_path = OUT / 'suite_status.json'
    status = json.loads(status_path.read_text()) if status_path.exists() else {}
    env = dict(os.environ, PYTHONUNBUFFERED='1', PYTHONIOENCODING='utf-8',
               OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', OMP_NUM_THREADS='4')
    for name, args in jobs:
        if status.get(name, {}).get('status') == 'complete':
            continue
        entry = {'status': 'running', 'command': [sys.executable, *args],
                 'started': datetime.now(timezone.utc).isoformat()}
        status[name] = entry
        status_path.write_text(json.dumps(status, indent=2))
        before = set((ROOT / 'results/tables/runs').glob('*'))
        print('START', name, flush=True)
        with (LOGS / f'{name}.log').open('w', encoding='utf-8') as log:
            proc = subprocess.run([sys.executable, *args], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        after = set((ROOT / 'results/tables/runs').glob('*'))
        entry.update(status='complete' if proc.returncode == 0 else 'failed',
                     returncode=proc.returncode, ended=datetime.now(timezone.utc).isoformat(),
                     run_dirs=[str(p.relative_to(ROOT)) for p in sorted(after - before)])
        status_path.write_text(json.dumps(status, indent=2))
        print(entry['status'].upper(), name, flush=True)
        if proc.returncode:
            raise SystemExit(f'{name} failed; inspect {LOGS / (name + ".log")}')


if __name__ == '__main__':
    main()
