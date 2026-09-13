"""Execute all available seed-42 explanation-transfer jobs sequentially."""
from pathlib import Path
import json,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[1]
MODELS=['DecisionTree','RandomForest','XGBoost','SoftVoting','ShallowMLP','DeepMLP','FeatureCNN']
def main():
    log=ROOT/'results/study/logs';log.mkdir(exist_ok=True)
    for source in ['unsw','ids2018']:
        for model in MODELS:
            done=ROOT/f'results/study/xai/{source}/{model}/manifest.json'
            if done.exists() and json.loads(done.read_text()).get('status')=='complete':continue
            with (log/f'xai_{source}_{model}.log').open('w') as output:
                subprocess.run([sys.executable,'-m','study.xai_transfer','--source',source,'--model',model],cwd=ROOT,env=dict(os.environ,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2'),stdout=output,stderr=subprocess.STDOUT,check=True)
            print('COMPLETE',source,model,flush=True)
if __name__=='__main__':main()
