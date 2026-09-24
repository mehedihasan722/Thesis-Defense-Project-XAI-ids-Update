"""Extend the original Word package without rebuilding its existing content."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from copy import deepcopy
import hashlib
import json
import re
from lxml import etree as E
from docx import Document
from docx.shared import Inches

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'thesis/reference/original_thesis.docx'
OUT=ROOT/'output/docx/thesis_xai_ids_preserved.docx'
AUDIT=ROOT/'results/study/preserved_report'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS={'w':W,'r':R}
def q(s):return '{'+W+'}'+s
def txt(el):return ''.join(t.text or '' for t in el.iter(q('t')))

def main():
    original=Document(SOURCE)
    with ZipFile(SOURCE) as z: parts={n:z.read(n) for n in z.namelist()}
    root=E.fromstring(parts['word/document.xml']);body=root.find(q('body'))
    ps=list(body.findall(q('p')))
    styles={s.name:s.style_id for s in original.styles}
    def para(text,style='10 Normal01-FirstParagraph'):
        p=E.Element(q('p'));pr=E.SubElement(p,q('pPr'));E.SubElement(pr,q('pStyle')).set(q('val'),styles[style])
        r=E.SubElement(p,q('r'));t=E.SubElement(r,q('t'));t.text=text;t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        return p
    def heading(text):return para(text,'09b Level02')
    def insert(index,elements):
        anchor=ps[index]
        for el in elements:anchor.addprevious(el)
    # All historical prose and graphics remain; short notes delimit their scope.
    note='The original study is retained in this revision, including its numerical tables, figures, references and appendices. The added experiments use a corrected feature-group-disjoint protocol and are reported separately. RQ1 remains stability, RQ2 faithfulness, RQ3 transferability and RQ4 cross-explainer agreement; the LLM comparison is an additional evaluation, not a renaming of RQ4. References to an unexecuted RQ3 describe the original scope; the extension now completes frozen detection and LIME transfer in both directions.'
    insert(51,[para('Expanded-study update','09b Level02'),para(note),para('The extension adds NF-CSE-CIC-IDS2018-v2, shallow and deep neural networks, a feature CNN and three local language models. It completes 84 detector configurations and 126 evaluation cells. Best three-seed binary macro-F1 is 0.9750 on UNSW and 0.9852 on IDS2018, but all detector families deteriorate under frozen cross-dataset evaluation. The LLMs predict a constant class under the tested protocol, giving macro-F1 0.3333 on balanced cohorts. These negative results are retained.')])
    insert(255,[heading('1.5.1  Extension of the original scope'),para(note)])
    insert(427,[para('Historical and expanded evidence','09b Level02'),para('Sections 4.2.1–4.2.9 and Figures 4.1–4.11 preserve the original study. Sections 4.2.10 onward add the completed group-disjoint study and audit. Historical random-split performance is not a current leakage-controlled estimate: the audit found 88.97% exact-input overlap in the old random-split evaluation. Cross-model stability ordering must not be interpreted as a general law or evidence of fabricated results.')])
    insert(493,[para('Audit clarification','09b Level02'),para('The following original discussion is preserved for provenance. The completed matched-case audit later in this chapter qualifies its cross-model interpretation: within each of the three audited tree models, stability correlates positively with LIME-minus-random removal effects. Neither direction alone establishes causation. The old aggregate masking calculations were reproduced to numerical tolerance, but original feature rankings were not saved, so the exact historical masks cannot be replayed.')])
    md=(ROOT/'thesis/manuscript.md').read_text(encoding='utf-8')
    def chapter(a,b):return md.split(a,1)[1].split(b,1)[0].strip()
    refmap={1:15,2:3,3:4,4:37,5:25,6:38,7:39,8:40,9:41,10:42}
    def clean(t):
        t=t.replace('[8-10]', '[40, 41, 42]').replace('exact inventory in Appendix A', 'inventory in the data manifest')
        t=re.sub(r'\[(\d+)\]',lambda m:'['+str(refmap.get(int(m[1]),int(m[1])))+']',t)
        t=re.sub(r'!\[.*?\]\(.*?\)','',t)
        t=re.sub(r'Figure\s+\d+\.\d+','the separate extension figures',t)
        t=t.replace('RQ4: matched LLM classification','Matched LLM classification extension')
        return t.replace('**','').replace('`','')
    table_n=11
    captured=[]
    def table(rows):
        # Source-derived table layout, with proportional widths and repeatable header.
        template=deepcopy(body.findall(q('tbl'))[3])
        for el in list(template):
            if el.tag in (q('tr'),q('tblGrid')):template.remove(el)
        props=template.find(q('tblPr'))
        width=props.find(q('tblW'))
        if width is not None:width.set(q('w'),'7100');width.set(q('type'),'dxa')
        n=len(rows[0]);grid=E.SubElement(template,q('tblGrid'))
        widths=[int(7100/n)]*n
        for v in widths:E.SubElement(grid,q('gridCol')).set(q('w'),str(v))
        for i,row in enumerate(rows):
            tr=E.SubElement(template,q('tr'));trpr=E.SubElement(tr,q('trPr'))
            if i==0:E.SubElement(trpr,q('tblHeader'))
            for j,cell in enumerate(row):
                tc=E.SubElement(tr,q('tc'));tcpr=E.SubElement(tc,q('tcPr'));ww=E.SubElement(tcpr,q('tcW'));ww.set(q('w'),str(widths[j]));ww.set(q('type'),'dxa')
                p=para(clean(cell));ppr=p.find(q('pPr'))
                if i < len(rows)-1:E.SubElement(ppr,q('keepNext'))
                sp=E.SubElement(ppr,q('spacing'));sp.set(q('after'),'60');sp.set(q('line'),'240');sp.set(q('lineRule'),'auto')
                for r in p.findall(q('r')):
                    rp=E.Element(q('rPr'));E.SubElement(rp,q('sz')).set(q('val'),'18')
                    if i==0:E.SubElement(rp,q('b'))
                    r.insert(0,rp)
                tc.append(p)
        return template
    def markdown(content, prefix, start=1, table_prefix='4'):
        nonlocal table_n
        mapping={}
        for old in re.findall(r'^Table ([A-Z0-9]+\.\d+)\.',content,re.M):
            table_n+=1;mapping[old]=f'{table_prefix}.{table_n}'
        content=re.sub(r'Table ([A-Z0-9]+\.\d+)',lambda m:'Table '+mapping.get(m[1],m[1]),content)
        lines=content.splitlines();els=[];i=0;h=start
        while i<len(lines):
            t=lines[i].strip();i+=1
            if not t or t.startswith('!['):continue
            if t.startswith('## '):
                name=re.sub(r'^## \d+\.\d+\s*','',t)
                els.append(heading(f'{prefix}.{h}  '+clean(name)));h+=1;continue
            if t.startswith('|'):
                rows=[]
                while True:
                    if not re.match(r'^\|[\s:|\-]+\|$',t):rows.append([c.strip() for c in t.strip('|').split('|')])
                    if i>=len(lines) or not lines[i].strip().startswith('|'):break
                    t=lines[i].strip();i+=1
                els.append(table(rows));continue
            if re.match(r'^Table [A-Z0-9]+\.\d+\.',t):
                t=re.sub(r'^(Table [A-Z0-9]+\.\d+)\.',r'\1:',t)
                els.append(para(clean(t),'15b Table-Caption'));continue
            els.append(para(clean(t)))
        captured.append(content)
        return els
    lit=chapter('## 2.4 Language models for intrusion detection and explanation','# CHAPTER III')
    lit=lit.split('## 2.5',1)[0]
    insert(324,[heading('2.7.1  Research gap addressed by the extension'),para('The extension connects repeatability, random-controlled masking and frozen cross-network transfer under a common input representation. It adds neural and LLM comparisons without claiming the first use of LLMs in intrusion detection. The historical literature and positioning remain above; the following discussion extends that scope.')]+markdown(lit,'2.7'))
    methods=chapter('# CHAPTER III','# CHAPTER IV').removeprefix('METHODOLOGY').strip()
    table_n=5
    insert(422,[heading('3.8.1  Expanded study methods'),para('The protocols below govern the new experiments only. They do not retroactively change the original experiments described in Sections 3.1–3.8.')]+markdown(methods,'3.8.1',table_prefix='3'))
    results=chapter('# CHAPTER IV','# CHAPTER V').removeprefix('RESULTS AND DISCUSSION').strip()
    table_n=11
    resultels=markdown(results,'4.2',10)
    # Independent images, relationships and media are added without rewriting original media.
    catalog=json.loads((AUDIT/'figure_catalog.json').read_text())
    catalog.sort(key=lambda x:['detection','transfer','audit','xai','llm'].index(x['section']))
    relroot=E.fromstring(parts['word/_rels/document.xml.rels'])
    ct=E.fromstring(parts['[Content_Types].xml'])
    relns='http://schemas.openxmlformats.org/package/2006/relationships'
    figuregroups={}
    for num,item in enumerate(catalog,12):
        temp=Document();p=temp.add_paragraph();p.add_run().add_picture(str(AUDIT/'figures'/item['file']),width=Inches(5.5))
        el=deepcopy(p._p); elpr=el.find(q('pPr'))
        if elpr is None:elpr=E.Element(q('pPr'));el.insert(0,elpr)
        E.SubElement(elpr,q('jc')).set(q('val'),'center');E.SubElement(elpr,q('keepNext'))
        rid=f'rIdExpandedFigure{num}';target=f'media/expanded_figure_{num}.png'
        for blip in el.xpath('.//*[local-name()="blip"]'):blip.set('{'+R+'}embed',rid)
        for dp in el.xpath('.//*[local-name()="docPr"]'):dp.set('id',str(10000+num));dp.set('name',f'Expanded Figure 4.{num}');dp.set('descr',item['caption'])
        E.SubElement(relroot,'{'+relns+'}Relationship',Id=rid,Type=R+'/image',Target=target)
        parts['word/'+target]=(AUDIT/'figures'/item['file']).read_bytes()
        figuregroups.setdefault(item['section'],[]).extend([el,para(f'Figure 4.{num}: '+item['caption'],'15a Caption-Center')])
        item['number']=f'4.{num}'
    slots={'4.2.12':'detection','4.2.13':'transfer','4.2.14':'audit','4.2.15':'xai','4.2.18':'llm'}
    integrated=[]
    for element in resultels:
        key=txt(element).split(' ',1)[0]
        if key in slots:integrated.extend(figuregroups.pop(slots[key],[]))
        integrated.append(element)
    for group in figuregroups.values():integrated.extend(group)
    insert(530,integrated)
    insert(573,[heading('5.1.1  Conclusions from the expanded study'),para('The expanded evidence qualifies the historical conclusions above. Seven detector families completed three-seed comparisons on two datasets. XGBoost reached mean binary macro-F1 0.9750 on UNSW; random forest reached 0.9852 on IDS2018. Neural models were competitive within datasets but did not eliminate the loss under frozen transfer. RQ3 is now completed for the specified binary detection and LIME protocols. The UNSW-trained random forest retained target-domain Jaccard@5 0.9222 while its LIME-minus-random masking advantage was -0.1338, demonstrating that reproducibility alone does not establish predictive relevance.'),para('The three small local LLMs completed classification and both explanation tasks, but each collapsed to one predicted class under the frozen four-example protocol. These are negative benchmark findings, not a claim about every LLM. The historical audit found no material arithmetic reversal; descriptive within-model stability–advantage correlations were positive. The original RQ4 agreement results remain a separate contribution, and the new neural and LLM comparisons do not supply missing SHAP or TOPSIS experiments.')])
    insert(590,[heading('Completed RQ3 and remaining work'),para('The RQ3 plan retained below describes the original pre-defence scope. Cross-network detection and LIME transfer have now been completed in both directions, as reported in the expanded results. Source-only calibration, training-only class-imbalance controls and masking-definition sensitivity are also completed extensions. Chronological evaluation, independent networks, larger or fine-tuned language models, prompt sensitivity on independent development data, and analyst usefulness remain future work. The original RQ4 agreement experiment remains preserved; no expanded SHAP or TOPSIS comparison is claimed for the neural models.')])
    insert(608,[heading('5.3.4  Future work after the completed extension')]+markdown(chapter('## 5.3 Future work','# References'),'5.3.4'))
    # Append only the six additional references; original 36 stay byte-identical.
    refs=chapter('# References','# Appendix A')
    newrefs=[]
    for line in refs.splitlines():
        m=re.match(r'^\[(\d+)\]',line)
        if m and int(m[1]) in [4,6,7,8,9,10]:newrefs.append(para(clean(line),'24b Reference-Text'))
    insert(649,newrefs)
    app=chapter('# Appendix B: Detailed explanation-transfer results','# Appendix C')
    table_n=0
    appels=[para('Appendix C','08 Chapter-Number'),para('Expanded Study Evidence','09 Heading 0'),para('The original Appendices A and B are retained in full. This appendix adds the new explanation-transfer evidence. The expanded experiment inventory is results/study/completed_metrics.csv; model revisions and configurations are in study/model_revisions.json and study/config.json. Separate figures and their numerical provenance are recorded in results/study/preserved_report/.')]+markdown(app,'C',table_prefix='C')
    for el in appels:body.insert(len(body)-1,el)
    # Replace only manual navigation entries; rebuild them using source styles and page fields.
    for p in ps[52:142]+ps[143:162]+ps[163:182]:
        if p.getparent() is body:body.remove(p)
    oldlabels={}
    for p in ps[144:182]:
        t=txt(p).split('\t')[0]
        # Tabs are XML elements, so use python-docx text for exact original labels.
    for p in original.paragraphs[144:182]:
        label=p.text.split('\t')[0]
        m=re.match(r'(Table|Figure) ([0-9]+\.[0-9]+)',label)
        if m:oldlabels[m[0]]=label
    entries={'contents':[],'figures':[],'tables':[]};bid=20000
    for p in list(body.findall(q('p'))):
        st=p.find('w:pPr/w:pStyle',NS);sid=st.get(q('val')) if st is not None else ''
        t=txt(p);kind=None
        if sid in [styles['09a Level01'],styles['09b Level02'],styles['08 Chapter-Number'],styles['08 Chapter-Number (no break)']] and re.match(r'^(?:\d|[ABC]\.\d|CHAPTER|Appendix)',t):kind='contents'
        if t in ['References','DECLARATION',"Supervisor's Declaration",'Declaration of Thesis and Copyright','Acknowledgement','Abstract','List of Tables','List of Figures','List of Abbreviations']:kind='contents'
        if sid==styles['15a Caption-Center'] and t.startswith('Figure '):kind='figures'
        if sid==styles['15b Table-Caption'] and t.startswith('Table '):kind='tables'
        if not kind:continue
        bid+=1;name=f'ThesisAnchor{bid}';begin=E.Element(q('bookmarkStart'));begin.set(q('id'),str(bid));begin.set(q('name'),name);p.insert(1,begin)
        end=E.SubElement(p,q('bookmarkEnd'));end.set(q('id'),str(bid))
        label=t.split(': ',1)[0]+': '+t.split(': ',1)[1].split('. ')[0] if kind!='contents' and ': ' in t else t
        if kind!='contents':
            match=re.match(r'(Table|Figure) ([A-Z0-9]+\.[0-9]+)',label)
            if match:label=oldlabels.get(match[0],label)
            if len(label)>100:label=label[:97].rsplit(' ',1)[0]+'...'
        if re.match(r'^(CHAPTER|Appendix)',label):
            nextp=p.getnext()
            if nextp is not None:label+='  '+txt(nextp)
        entry=para(label,'12 TOC-Entry')
        entry.remove(entry.find(q('pPr')));entry.insert(0,deepcopy(ps[53].find(q('pPr'))))
        r=E.SubElement(entry,q('r'));E.SubElement(r,q('tab'))
        fld=E.SubElement(entry,q('fldSimple'));fld.set(q('instr'),f' PAGEREF {name} \\h ');rr=E.SubElement(fld,q('r'));E.SubElement(rr,q('t')).text='0'
        entries[kind].append(entry)
    for anchor,kind in [(ps[142],'contents'),(ps[162],'tables'),(ps[182],'figures')]:
        for el in entries[kind]:anchor.addprevious(el)
    # Floating source pictures use paragraph-relative offsets that become unsafe
    # after insertion. Move their unchanged graphics inline beside their captions.
    wp='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
    for paragraph in list(body.findall(q('p'))):
        anchors=list(paragraph.iter('{'+wp+'}anchor'))
        for floating in anchors:
            cursor=paragraph.getnext();caption=None
            while cursor is not None:
                if cursor.tag==q('p') and txt(cursor).startswith('Figure '):
                    st=cursor.find('w:pPr/w:pStyle',NS)
                    if st is not None and st.get(q('val'))==styles['15a Caption-Center']:caption=cursor;break
                cursor=cursor.getnext()
            assert caption is not None
            inline=E.Element('{'+wp+'}inline',distT='0',distB='0',distL='0',distR='0')
            for child in floating:
                if E.QName(child).localname in ['extent','effectExtent','docPr','cNvGraphicFramePr','graphic']:inline.append(deepcopy(child))
            holder=para('', '16 Figure-Holder')
            for r in list(holder.findall(q('r'))):holder.remove(r)
            pr=holder.find(q('pPr'));E.SubElement(pr,q('keepNext')).set(q('val'),'true')
            run=E.SubElement(holder,q('r'));drawing=E.SubElement(run,q('drawing'));drawing.append(inline)
            old_drawing=floating.getparent();old_run=old_drawing.getparent();old_run.remove(old_drawing)
            caption.addprevious(holder)
    # Keep each original and new figure together with its caption.
    for caption in body.findall(q('p')):
        st=caption.find('w:pPr/w:pStyle',NS)
        if st is not None and st.get(q('val'))==styles['15a Caption-Center']:
            previous=caption.getprevious()
            if previous is not None and previous.tag==q('p'):
                pr=previous.find(q('pPr'))
                if pr is None:pr=E.Element(q('pPr'));previous.insert(0,pr)
                keep=pr.find(q('keepNext'))
                if keep is None:keep=E.SubElement(pr,q('keepNext'))
                keep.set(q('val'),'true')
    parts['word/document.xml']=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
    parts['word/_rels/document.xml.rels']=E.tostring(relroot,xml_declaration=True,encoding='UTF-8',standalone=True)
    settings=E.fromstring(parts['word/settings.xml']);u=settings.find(q('updateFields'))
    if u is None:u=E.SubElement(settings,q('updateFields'))
    u.set(q('val'),'true');parts['word/settings.xml']=E.tostring(settings,xml_declaration=True,encoding='UTF-8',standalone=True)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
        for n,b in parts.items():z.writestr(n,b)
    modified={'word/document.xml','word/_rels/document.xml.rels','word/settings.xml'}
    with ZipFile(SOURCE) as z:
        changed=[n for n in z.namelist() if n not in modified and z.read(n)!=parts[n]]
    assert not changed,changed
    # Original body text and tables remain exact, except navigation entries.
    new=Document(OUT);newtext=[p.text for p in new.paragraphs]
    missing=[i for i,p in enumerate(original.paragraphs) if i not in range(52,142) and i not in range(143,162) and i not in range(163,182) and p.text and p.text not in newtext]
    assert not missing,missing
    oldtables=[[c.text for row in t.rows for c in row.cells] for t in original.tables]
    newtables=[[c.text for row in t.rows for c in row.cells] for t in new.tables]
    assert all(t in newtables for t in oldtables)
    report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'original_paragraphs':len(original.paragraphs),'original_tables_preserved':len(oldtables),'original_references_preserved':36,'original_figure_captions_preserved':18,'new_separate_figures':len(catalog),'unmodified_package_parts_verified':True,'missing_original_body_paragraphs':missing,'output':str(OUT),'status':'built; Word field refresh and visual QA pending'}
    (AUDIT/'preservation_check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (AUDIT/'figure_catalog.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
    (AUDIT/'README.md').write_text('# Original thesis preservation\n\nAll 25 original tables, 18 figure captions, 36 references, original drawings and both appendices are retained. New results use a separately labelled protocol. Each new figure has its own PNG, SVG and vector PDF file.\n\n'+ '\n\n'.join(f"## Figure {x['number']}\n\n{x['caption']}\n\n![Figure {x['number']}](figures/{x['file']})" for x in catalog),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
