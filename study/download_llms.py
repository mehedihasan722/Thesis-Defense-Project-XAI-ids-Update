"""Download public model files, recording immutable model revisions."""
import os,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['HF_HUB_DISABLE_XET']='1'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING']='1'
from huggingface_hub import snapshot_download
cfg=json.loads((ROOT/'study/config.json').read_text(encoding='utf-8-sig'))
pins=json.loads((ROOT/'study/model_revisions.json').read_text(encoding='utf-8-sig'))
output=ROOT/'results/study/llm_downloads.json'
records=json.loads(output.read_text()) if output.exists() else {}
for model in cfg['llms']:
    revision=pins[model]
    if model in records and Path(records[model]['path']).exists():
        assert records[model]['revision']==revision,'Cached model differs from pinned revision'
        continue
    print('Downloading',model,revision,flush=True)
    path=snapshot_download(model,revision=revision,local_dir=str(ROOT/'.hf-study/models'/model.replace('/','--')),cache_dir=str(ROOT/'.hf-study/hub'),allow_patterns=['*.json','*.safetensors','*.model','*.txt','README.md','LICENSE'],max_workers=2)
    records[model]={'revision':revision,'path':path,'source':'https://huggingface.co/'+model}
    output.write_text(json.dumps(records,indent=2));print('Complete',model,flush=True)

