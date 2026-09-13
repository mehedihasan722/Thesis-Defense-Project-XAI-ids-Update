"""Dataset-free repository checks for CI."""
from pathlib import Path
from urllib.parse import urlparse,unquote
import json,re
ROOT=Path(__file__).resolve().parents[1]

def main():
    config=json.loads((ROOT/'study/config.json').read_text(encoding='utf-8-sig'))
    pins=json.loads((ROOT/'study/model_revisions.json').read_text(encoding='utf-8-sig'))
    assert set(config['llms'])==set(pins),'Model configuration and immutable pins differ'
    assert all(re.fullmatch(r'[0-9a-f]{40}',sha) for sha in pins.values())
    checked=0
    for path in (ROOT/'results/study').rglob('*.md'):
        for target in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8-sig')):
            if urlparse(target).scheme in ['http','https','data']:continue
            asset=(path.parent/unquote(target.split('#')[0].strip('<>'))).resolve()
            assert asset.is_relative_to(ROOT),f'Figure outside repository: {path}: {target}'
            assert asset.is_file(),f'Missing figure: {path}: {target}'
            checked+=1
    print(f'Checked {checked} local figure references and {len(pins)} immutable model revisions')
if __name__=='__main__':main()
