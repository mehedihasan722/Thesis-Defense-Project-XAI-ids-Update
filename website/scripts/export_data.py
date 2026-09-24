"""Export frozen research evidence for the website; never run model inference."""
from pathlib import Path
from zipfile import ZipFile
import csv, hashlib, json, shutil, re
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
WEB=ROOT/'website'
PUBLIC=WEB/'public'
inputs={}
def read_csv(relative):
    p=ROOT/relative
    inputs[relative]=hashlib.sha256(p.read_bytes()).hexdigest()
    with p.open(encoding='utf-8-sig',newline='') as stream:
        rows=list(csv.DictReader(stream))
    for row in rows:
        for k,v in row.items():
            try: row[k]=float(v) if v else None
            except ValueError: pass
    return rows

def main():
    data={
      'detection':read_csv('results/study/across_seed_summary.csv'),
      'xai':read_csv('results/study/xai/aggregate.csv'),
      'llm':read_csv('results/study/llm/masking_coverage.csv'),
      'audit':{m:read_csv(f'results/study/audit/{m}_matched.csv') for m in ['DecisionTree','RandomForest','XGBoost']},
    }
    catalog=ROOT/'results/study/preserved_report/figure_catalog.json'
    inputs[str(catalog.relative_to(ROOT)).replace(chr(92),'/')]=hashlib.sha256(catalog.read_bytes()).hexdigest()
    figures=json.loads(catalog.read_text(encoding='utf-8'))
    for f in figures:
        f['path']='figures/'+f['file'];f['protocol']='Expanded study'
        source=ROOT/'results/study/preserved_report/figures'/f['file']
        f['source']=str(source.relative_to(ROOT)).replace(chr(92),'/')
        destination=PUBLIC/f['path'];destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
    original=ROOT/'thesis/reference/original_thesis.docx'
    with ZipFile(original) as z: xml=ET.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    captions={}
    for p in xml.findall('.//w:body/w:p',ns):
        text=''.join(t.text or '' for t in p.findall('.//w:t',ns))
        m=re.match(r'Figure (\d+\.\d+):?\s+(.*)',text)
        if m and '\t' not in text: captions[m[1]]=m[2]
    mapping={'1.1':'fig_1_1_trust_gap','2.1':'fig_2_1_prior_art_positioning','3.1':'fig_3_1_system_architecture','3.2':'fig_3_5_preprocessing_pipeline','3.3':'fig_3_4_experimental_design','3.4':'fig_3_2_rq1_protocol','3.5':'fig_3_3_rq2_protocol'}
    historical=sorted((ROOT/'results/figures').glob('[0-9][0-9]_*.png'))
    mapping.update({f'4.{i}':p.stem for i,p in enumerate(historical,1)})
    old=[]
    for number,name in mapping.items():
        source=ROOT/'results/figures'/f'{name}.png'
        destination=PUBLIC/'figures'/f'{name}.png';shutil.copyfile(source,destination)
        old.append({'number':number,'file':source.name,'path':'figures/'+source.name,'caption':captions.get(number,name.replace('_',' ')),'section':'historical','protocol':'Original study','source':str(source.relative_to(ROOT)).replace(chr(92),'/')})
    data['figures']=old+figures
    data['provenance']={'inputs':inputs,'report':'Original-preserving revision 33c62c0','experiment_configs':84,'evaluation_cells':126,'llm_classifications':1200,'llm_explanations':480}
    out=WEB/'src/data/study.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,separators=(',',':'),allow_nan=False),encoding='utf-8')
    shutil.copyfile(ROOT/'output/pdf/thesis_xai_ids_preserved.pdf',PUBLIC/'thesis.pdf')
    (PUBLIC/'evidence-manifest.json').write_text(json.dumps(data['provenance'],indent=2),encoding='utf-8')
    print(f"Exported {len(data['detection'])} detector groups, {len(data['xai'])} XAI groups, {len(data['figures'])} figures; no inference.")
if __name__=='__main__': main()
