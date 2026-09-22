"""Structural checks to accompany (not replace) visual PDF inspection."""
from pathlib import Path
import hashlib, json, re
import pdfplumber
ROOT=Path(__file__).resolve().parent
path=ROOT/'output/pdf/thesis_xai_ids.pdf'
with pdfplumber.open(path) as pdf:
    texts=[page.extract_text() or '' for page in pdf.pages]
    for page in pdf.pages:
        assert abs(page.width-594.96)<.1 and abs(page.height-842.04)<.1, 'Page size differs from reference'
        assert page.chars, 'Unexpected blank page'
        assert all(c['x0']>=0 and c['x1']<=page.width+.5 and c['top']>=0 and c['bottom']<=page.height+.5 for c in page.chars), 'Text outside page'
    combined='\n'.join(texts)
    assert '{{' not in combined and '[pending]' not in combined.lower(), 'Unresolved result placeholder'
    required=['DECLARATION',"SUPERVISOR'S DECLARATION",'DECLARATION OF THESIS AND COPYRIGHT','ACKNOWLEDGEMENT','ABSTRACT','CONTENTS','LIST OF TABLES','LIST OF FIGURES','LIST OF ABBREVIATIONS']
    for title in required: assert title in combined, title
    chapter_pages={}
    for number in ['I','II','III','IV','V']:
        matches=[i for i,t in enumerate(texts) if t.startswith('CHAPTER '+number+'\n')]
        assert len(matches)==1,(number,matches)
        chapter_pages[number]=matches[0]+1
    body_start=chapter_pages['I']
    for i,text in enumerate(texts[body_start-1:],body_start):
        assert text.splitlines()[-1]==str(i-body_start+1), ('Body page number',i)
    fonts=sorted({c['fontname'] for page in pdf.pages for c in page.chars})
    assert any('TimesNewRoman' in f for f in fonts),fonts
    report={'pdf':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':len(pdf.pages),'page_size_points':[594.96,842.04],'chapter_physical_pages':chapter_pages,'fonts':fonts,'checks':'A4 size, required front matter, five chapter starts, Arabic body numbering, page bounds, no unresolved placeholders','visual_review':'Required separately on rendered pages'}
(ROOT/'results/study/report').mkdir(parents=True,exist_ok=True)
(ROOT/'results/study/report/pdf_structure_check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
