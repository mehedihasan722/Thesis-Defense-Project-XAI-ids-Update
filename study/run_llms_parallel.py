"""Explicitly requested concurrent LLM resume; preserve evaluator and checkpoints."""
from pathlib import Path
import json, os, subprocess, sys, time
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'results/study'
def now(): return datetime.now(timezone.utc).isoformat()
def main():
    status_path=BASE/'llm/status.json'
    status=json.loads(status_path.read_text(encoding='utf-8-sig'))
    pending={}; handles=[]; stamp=datetime.now().strftime('%Y%m%d-%H%M%S')
    def save():
        temporary=status_path.with_suffix('.tmp.json')
        temporary.write_text(json.dumps(status,indent=2),encoding='utf-8');temporary.replace(status_path)
    try:
        for model in ['TinyLlama/TinyLlama-1.1B-Chat-v1.0','HuggingFaceTB/SmolLM2-1.7B-Instruct']:
            manifest=BASE/'llm'/model.replace('/','--')/'full/manifest.json'
            if manifest.exists() and json.loads(manifest.read_text())['status']=='complete':
                status[model]=dict(status='complete',verified_at=now());continue
            log=BASE/'logs'/f'parallel_{model.replace("/","--")}_{stamp}.log'
            handle=log.open('w',encoding='utf-8');handles.append(handle)
            p=subprocess.Popen([sys.executable,'-u','-m','study.llm_evaluate','--model',model],cwd=ROOT,env=dict(os.environ,OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2'),stdout=handle,stderr=subprocess.STDOUT)
            pending[model]=p
            status[model]=dict(status='running',started=now(),pid=p.pid,execution='concurrent_user_requested',log=str(log.relative_to(ROOT)))
        save()
        (BASE/'finalization_status.json').write_text(json.dumps(dict(status='waiting_for_llm_runs',supervisor_process_id=os.getpid(),queued_at=now(),next_step='study.finalize',execution='concurrent_user_requested'),indent=2))
        while pending:
            for model,p in list(pending.items()):
                code=p.poll()
                if code is not None:
                    status[model].update(status='complete' if code==0 else 'failed',returncode=code,ended=now());del pending[model];save()
            if pending:time.sleep(5)
        if any(status[m]['status']!='complete' for m in ['TinyLlama/TinyLlama-1.1B-Chat-v1.0','HuggingFaceTB/SmolLM2-1.7B-Instruct']):
            (BASE/'finalization_status.json').write_text(json.dumps(dict(status='blocked_by_failed_llm',checked_at=now())))
            raise SystemExit('At least one LLM failed; inspect per-model logs. Finalization skipped.')
        subprocess.run([sys.executable,'-u','-m','study.finalize'],cwd=ROOT,check=True)
    finally:
        for handle in handles:handle.close()
if __name__=='__main__':main()
