"""Fetch the requested public dataset without exposing credentials."""
from pathlib import Path
import requests,zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'data/raw/ids2018';folder.mkdir(parents=True,exist_ok=True)
archive=folder/'dataset.zip'
url='https://www.kaggle.com/api/v1/datasets/download/dhoogla/nfcsecicids2018v2'
if not archive.exists():
    with requests.get(url,stream=True,timeout=(30,120)) as response:
        response.raise_for_status()
        total=int(response.headers.get('Content-Length',0)); downloaded=0
        with archive.with_suffix('.partial').open('wb') as f:
            for block in response.iter_content(8*1024*1024):
                f.write(block);downloaded+=len(block)
                print(f'Downloaded {downloaded//1048576} / {total//1048576} MiB',flush=True)
    archive.with_suffix('.partial').replace(archive)
with zipfile.ZipFile(archive) as z:
    for item in z.infolist():
        target=(folder/item.filename).resolve()
        if not target.is_relative_to(folder.resolve()): raise ValueError('Unsafe archive path')
        if not target.exists():z.extract(item,folder)
files=[str(p.relative_to(ROOT)) for p in folder.rglob('*.parquet')]
assert files,'Expected NetFlow v2 parquet files'
(folder/'download_manifest.json').write_text(json.dumps({'url':url,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':files},indent=2))
print(files)
