"""Run the full new classical/neural training matrix with per-model recovery."""
from pathlib import Path
import json,subprocess,sys,os
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/study';LOG=OUT/'logs';LOG.mkdir(parents=True,exist_ok=True)
CFG=json.loads((ROOT/'study/config.json').read_text(encoding='utf-8-sig'))
status_path=OUT/'training_status.json'
status=json.loads(status_path.read_text()) if status_path.exists() else {}
env=dict(os.environ,PYTHONUNBUFFERED='1',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4')
for seed in CFG['seeds']:
    for task in ['binary','multiclass']:
        for dataset in ['unsw','ids2018']:
            key=f'{dataset}_{task}_{seed}'
            if status.get(key,{}).get('status')=='complete':continue
            command=[sys.executable,'-m','study.train','--dataset',dataset,'--task',task,'--seed',str(seed)]
            entry={'status':'running','started':datetime.now(timezone.utc).isoformat(),'command':command};status[key]=entry
            status_path.write_text(json.dumps(status,indent=2));print('START',key,flush=True)
            with (LOG/f'{key}.log').open('w',encoding='utf-8') as f:
                result=subprocess.run(command,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
            entry.update(status='complete' if result.returncode==0 else 'failed',returncode=result.returncode,ended=datetime.now(timezone.utc).isoformat());status_path.write_text(json.dumps(status,indent=2));print(entry['status'],key,flush=True)
            if result.returncode:raise SystemExit('Inspect '+str(LOG/f'{key}.log'))
