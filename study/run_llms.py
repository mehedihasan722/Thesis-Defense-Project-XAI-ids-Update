"""Sequential full local LLM evaluation, preserving failures and partial evidence."""
from pathlib import Path
import subprocess,sys,json,os
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'results/study/llm';out.mkdir(exist_ok=True)
    status_path=out/'status.json';status=json.loads(status_path.read_text()) if status_path.exists() else {}
    models=json.loads((ROOT/'study/config.json').read_text())['llms']
    for model in models:
        manifest=out/model.replace('/','--')/'full/manifest.json'
        if manifest.exists() and json.loads(manifest.read_text()).get('status')=='complete':continue
        status[model]=dict(status='running',started=datetime.now(timezone.utc).isoformat());status_path.write_text(json.dumps(status,indent=2))
        log=ROOT/'results/study/logs'/('llm_'+model.replace('/','--')+'.log')
        with log.open('w',encoding='utf-8') as f:
            result=subprocess.run([sys.executable,'-m','study.llm_evaluate','--model',model],cwd=ROOT,env=dict(os.environ,OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2'),stdout=f,stderr=subprocess.STDOUT)
        status[model].update(status='complete' if result.returncode==0 else 'failed',returncode=result.returncode,ended=datetime.now(timezone.utc).isoformat());status_path.write_text(json.dumps(status,indent=2));print(model,status[model]['status'],flush=True)
    subprocess.run([sys.executable,'-m','study.summarize_llm'],cwd=ROOT,check=True)
    if any(r['status']=='failed' for r in status.values()):raise SystemExit('One or more LLM runs failed; inspect logs')
if __name__=='__main__':main()
