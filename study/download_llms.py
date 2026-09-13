"""Download public model files, recording immutable model revisions."""
import os,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['HF_HUB_DISABLE_XET']='1'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING']='1'
from huggingface_hub import HfApi,snapshot_download
cfg=json.loads((ROOT/'study/config.json').read_text(encoding='utf-8-sig'))
output=ROOT/'results/study/llm_downloads.json'
records=json.loads(output.read_text()) if output.exists() else {}
for model in cfg['llms']:
    if model in records and Path(records[model]['path']).exists():continue
    info=HfApi().model_info(model)
    print('Downloading',model,info.sha,flush=True)
    path=snapshot_download(model,revision=info.sha,local_dir=str(ROOT/'.hf-study/models'/model.replace('/','--')),cache_dir=str(ROOT/'.hf-study/hub'),allow_patterns=['*.json','*.safetensors','*.model','*.txt','README.md','LICENSE'],max_workers=2)
    records[model]={'revision':info.sha,'path':path,'source':'https://huggingface.co/'+model}
    output.write_text(json.dumps(records,indent=2));print('Complete',model,flush=True)
