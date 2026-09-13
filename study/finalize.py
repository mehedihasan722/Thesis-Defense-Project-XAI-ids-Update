"""Finish the authorized study after training/LLM jobs exit; verify and publish."""
from pathlib import Path
import json,subprocess,sys,traceback
from datetime import datetime,timezone
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'results/study';STATUS=BASE/'finalization_status.json'
def main():
    state={'status':'running','started':datetime.now(timezone.utc).isoformat()}
    def run(name,args):
        state['step']=name;STATUS.write_text(json.dumps(state,indent=2))
        with (BASE/'logs'/f'finalize_{name}.log').open('w',encoding='utf-8') as f:subprocess.run(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
    try:
        models=json.loads((ROOT/'study/config.json').read_text())['llms']
        for model in models:
            folder=BASE/'llm'/model.replace('/','--')/'full'
            assert json.loads((folder/'manifest.json').read_text())['status']=='complete',f'Incomplete LLM: {model}'
            cases=[json.loads(l) for l in (folder/'cases.jsonl').read_text().splitlines()]
            assert len(cases)==400 and len({(r['source'],r['target'],r['row']) for r in cases})==400
            for source in ['unsw','ids2018']:
                for target in ['unsw','ids2018']:
                    selected=[r for r in cases if r['source']==source and r['target']==target]
                    assert len(selected)==100 and sum('own_explanation' in r for r in selected)==20
        for name in ['summarize','validate_results','summarize_xai','summarize_llm','llm_masking']:
            run(name,[sys.executable,'-m','study.'+name])
        audit=pd.read_csv(BASE/'validation/prediction_audit.csv');assert len(audit)==126 and audit.passed.all()
        seeds=pd.read_csv(BASE/'across_seed_summary.csv');assert len(seeds)==42 and (seeds.n_seeds==3).all()
        assert len(pd.read_csv(BASE/'llm/masking_coverage.csv'))==24
        run('tests',[sys.executable,'-m','unittest','study.test_study','study.test_xai','study.test_calibration','study.test_llm','study.test_uncertainty','study.test_llm_tokens','-v'])
        run('historical_tests',[str(ROOT/'.venv/Scripts/python.exe'),'-m','unittest','discover','-s','tests','-v'])
        run('figures',[sys.executable,'-m','study.make_figures'])
        (ROOT/'PROGRESS.md').write_text('# Completed executable study\n\nAll 84 detector configurations and 126 evaluation cells are complete and independently checked. All 14 RQ3 model pilots, source-only calibration, training-only imbalance comparison and three full local LLM runs with classification and explanations are complete. Valid LLM explanations have named-versus-random masking checks; invalid outputs remain in coverage denominators.\n\nResults, tables and embedded figures are in results/study/RESULTS.md, ACROSS_SEEDS.md and the xai/, llm/, calibration/, imbalance/ and shift/ analysis files. The thesis report remains unchanged.\n\nLimitations remain scientific, not hidden: small explanation cohorts, three small CPU LLMs, rounded flow serialization, masking distribution shifts and no temporal/analyst validation. Historical original probabilities replay, but exact old masks cannot be replayed because original rankings were not saved. Do not interpret inverse stability/faithfulness relationships as proof of falsification.\n',encoding='utf-8')
        subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT,check=True)
        remote=subprocess.check_output(['git','remote','get-url','update'],cwd=ROOT,text=True).strip()
        assert remote=='https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update.git'
        assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='main'
        paths=['PROGRESS.md','results/study/RESULTS.md','results/study/ACROSS_SEEDS.md','results/study/completed_metrics.csv','results/study/across_seed_summary.csv','results/study/unsw','results/study/ids2018','results/study/xai','results/study/llm','results/study/figures','results/study/validation']
        subprocess.run(['git','add','--',*paths],cwd=ROOT,check=True)
        if subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode:
            body=ROOT/'tmp/git/final-study.txt';body.write_text('📊 Complete verified detector and local LLM study evidence\n\nPublish all 126 detector evaluation cells, three-seed summaries, 14 RQ3 pilots and three local LLM classification/explanation runs. Preserve invalid explanations, random-controlled masking checks and matched-case comparisons. Refresh embedded figures and document limitations without modifying the thesis report.\n\nValidation: independent probability/label/metric checks pass for all cells; fifteen new study tests and ten historical tests pass; required LLM case and explanation counts verified.\n',encoding='utf-8')
            run('commit',['git','commit','-F',str(body)])
        run('push',['git','push','update','main'])
        state.update(status='complete',ended=datetime.now(timezone.utc).isoformat(),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip());STATUS.write_text(json.dumps(state,indent=2))
    except Exception:
        state.update(status='failed',error=traceback.format_exc(),ended=datetime.now(timezone.utc).isoformat());STATUS.write_text(json.dumps(state,indent=2));raise
if __name__=='__main__':main()

