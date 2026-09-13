"""Render the thesis using the supplied IIUC reference layout."""
from pathlib import Path
import re, hashlib
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from PIL import Image as PILImage
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'thesis/manuscript.md'
W,H=594.96,842.04
LEFT,RIGHT=107.8,72
WIDTH=W-LEFT-RIGHT

def roman(n):
    out=''
    for value, symbol in [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
        while n>=value: out+=symbol; n-=value
    return out

class ThesisDoc(BaseDocTemplate):
    def beforeDocument(self): self.body_start=None
    def afterFlowable(self, f):
        if not isinstance(f,Paragraph): return
        text=f.getPlainText()
        if getattr(f,'starts_body',False): self.body_start=self.page
        label=self.page-self.body_start+1 if self.body_start else -self.page
        kind=getattr(f,'entry_kind',None)
        if kind:
            key='h'+hashlib.sha256(text.encode()).hexdigest()[:18]
            self.canv.bookmarkPage(key)
            self.notify(kind,(getattr(f,'entry_level',0),getattr(f,'entry_text',text),label,key))

def inline(s):
    s=escape(s.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-'))
    s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    return re.sub(r'`(.*?)`',r'<font size="10">\1</font>',s)

def main():
    for name,file in [('TNR','times.ttf'),('TNR-Bold','timesbd.ttf'),('TNR-Italic','timesi.ttf'),('TNR-BoldItalic','timesbi.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
    pdfmetrics.registerFontFamily('TNR',normal='TNR',bold='TNR-Bold',italic='TNR-Italic',boldItalic='TNR-BoldItalic')
    body=ParagraphStyle('Body',fontName='TNR',fontSize=12,leading=20.7,alignment=TA_JUSTIFY,spaceAfter=10)
    center=ParagraphStyle('Center',parent=body,alignment=TA_CENTER)
    heading=ParagraphStyle('Heading',parent=center,fontName='TNR-Bold',fontSize=14,leading=20.7,spaceAfter=26,keepWithNext=True)
    sub=ParagraphStyle('Sub',parent=body,fontName='TNR-Bold',spaceBefore=12,spaceAfter=9,keepWithNext=True)
    caption=ParagraphStyle('Caption',parent=center,fontName='TNR-Bold',fontSize=11,leading=14,spaceBefore=8,spaceAfter=8)
    cell=ParagraphStyle('Cell',parent=body,fontSize=9.5,leading=12,alignment=0,spaceAfter=0,splitLongWords=True)
    def p(text,style=body,kind=None,level=0):
        obj=Paragraph(inline(text),style)
        if kind: obj.entry_kind=kind; obj.entry_level=level
        return obj
    def table(rows,widths=None):
        n=len(rows[0])
        if widths is None:
            widths=[WIDTH/n]*n
            if n==2: widths=[WIDTH*.36,WIDTH*.64]
            if n==3: widths=[WIDTH*.28,WIDTH*.48,WIDTH*.24]
        data=[[p(('**'+c+'**') if i==0 else c,cell) for c in row] for i,row in enumerate(rows)]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee')),('GRID',(0,0),(-1,-1),.5,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        return t
    out=ROOT/'output/pdf/thesis_xai_ids.pdf'; out.parent.mkdir(parents=True,exist_ok=True)
    doc=ThesisDoc(str(out),pagesize=(W,H),leftMargin=LEFT,rightMargin=RIGHT,topMargin=82,bottomMargin=72,title='Evaluating the Reliability of Explainable AI in Ensemble-Based Intrusion Detection Systems',author='Mehedi Hasan and Sazzadul Islam')
    def footer(canvas,d):
        if d.page==1:return
        canvas.saveState(); canvas.setFont('TNR',12)
        canvas.drawCentredString(LEFT+WIDTH/2,48,str(d.page-d.body_start+1) if d.body_start else roman(d.page)); canvas.restoreState()
    doc.addPageTemplates(PageTemplate(id='thesis',frames=[Frame(LEFT,72,WIDTH,H-154,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPageEnd=footer))
    title='EVALUATING THE RELIABILITY OF<br/>EXPLAINABLE AI IN ENSEMBLE-BASED<br/>INTRUSION DETECTION SYSTEMS'
    title_style=ParagraphStyle('Title',parent=center,fontName='TNR-Bold',fontSize=16,leading=23)
    story=[Spacer(1,35),Paragraph(title,title_style),Spacer(1,28),p('Thesis Submitted in Fulfilment for the Degree of<br/>Bachelor of Science (B.Sc.) in Computer Science and<br/>Engineering (CSE)',center)]
    # Explicit line breaks are markup only in these authored cover paragraphs.
    story[-1]=Paragraph('Thesis Submitted in Fulfilment for the Degree of<br/>Bachelor of Science (B.Sc.) in Computer Science and<br/>Engineering (CSE)',center)
    story += [Spacer(1,12),p('by',center),p('Mehedi Hasan (C213061)',center),p('Sazzadul Islam (C213066R)',center),Spacer(1,20),Image(str(ROOT/'thesis/assets/iiuc_logo.jpg'),85,85),Spacer(1,22)]
    for text in ['DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING','INTERNATIONAL ISLAMIC UNIVERSITY CHITTAGONG (IIUC)','Chittagong, Bangladesh']:
        story.append(p(text,ParagraphStyle('Institution',parent=center,fontSize=11,leading=16)))
    def front(title,paragraphs):
        story.extend([PageBreak(),p(title,heading,'TOCEntry')])
        story.extend(p(x) for x in paragraphs)
    front('DECLARATION',[
        'Declaration form for author review and signature.',
        'The authors should confirm the originality of this thesis, the acknowledgement of all sources, and compliance with the university requirements before signing this declaration.',
        'Thesis: Evaluating the Reliability of Explainable AI in Ensemble-Based Intrusion Detection Systems.',
        'Mehedi Hasan (C213061)', 'Signature: ____________________    Date: ______________',
        'Sazzadul Islam (C213066R)', 'Signature: ____________________    Date: ______________'])
    front("SUPERVISOR'S DECLARATION",[
        'Reserved for the supervisor to review and certify the scope, quality and suitability of the revised thesis for submission.',
        'Supervisor: Mr. Md. Mahiuddin', 'Associate Professor, Department of CSE', 'International Islamic University Chittagong',
        'Approval / comments: __________________________________', '____________________________________________________',
        'Signature: ____________________    Date: ______________'])
    front('DECLARATION OF THESIS AND COPYRIGHT',[
        'THESIS TITLE: Evaluating the Reliability of Explainable AI in Ensemble-Based Intrusion Detection Systems.',
        'The authors and supervisor should complete the required university declaration and select the applicable archive and copyright permissions before submission.'])
    story += [table([['No.','Author','Student ID','Signature'],['1','Mehedi Hasan','C213061',''],['2','Sazzadul Islam','C213066R','']],[30,150,85,WIDTH-265]),Spacer(1,24),table([['Name of supervisor','Signature'],['Md. Mahiuddin, Associate Professor, Department of CSE, IIUC','']],[WIDTH*.72,WIDTH*.28]),Spacer(1,24),p('Archive / publication permission: ____________________'),p('Date: ____________________')]
    front('ACKNOWLEDGEMENT',[
        'Praise be to Almighty Allah. We thank our supervisor, Mr. Md. Mahiuddin, and the Department of Computer Science and Engineering at International Islamic University Chittagong.',
        'We acknowledge the creators of UNSW-NB15 and the standardised NetFlow dataset, and the maintainers of scikit-learn, LIME, SHAP and XGBoost for the resources used in this study.',
        'We thank our families for their support throughout our studies.'])
    lines=SOURCE.read_text(encoding='utf-8').splitlines()
    start=next(i for i,x in enumerate(lines) if x.lower()=='# abstract')
    i=start
    inserted=False
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('# '):
            text=line[2:]
            if text=='CHAPTER I' and not inserted:
                for label,kind in [('CONTENTS','TOCEntry'),('LIST OF TABLES','TableEntry'),('LIST OF FIGURES','FigureEntry')]:
                    story.extend([PageBreak(),p(label,heading,'TOCEntry' if kind!='TOCEntry' else None)])
                    listing=TableOfContents(notifyKind=kind,dotsMinLevel=0,formatter=lambda n: roman(-n) if n<0 else str(n),tableStyle=TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
                    listing.levelStyles=[ParagraphStyle('TOC0',fontName='TNR',fontSize=12,leading=18,spaceBefore=4),ParagraphStyle('TOC1',fontName='TNR',fontSize=11,leading=16,leftIndent=14,spaceBefore=2),ParagraphStyle('TOC2',fontName='TNR',fontSize=10.5,leading=15,leftIndent=28,spaceBefore=1)]
                    story.append(listing)
                front('LIST OF ABBREVIATIONS',[])
                story.append(table([['Abbreviation','Meaning'],['AI','Artificial intelligence'],['IDS','Intrusion detection system'],['XAI','Explainable artificial intelligence'],['LIME','Local interpretable model-agnostic explanations'],['SHAP','SHapley Additive exPlanations'],['DT','Decision tree'],['RF','Random forest'],['XGB','Extreme gradient boosting'],['FAR','False alarm rate'],['RQ','Research question'],['TOPSIS','Technique for order preference by similarity to ideal solution']]))
                inserted=True
            story.append(PageBreak())
            obj=p(text.upper(),heading,'TOCEntry')
            if text.startswith('CHAPTER '):
                i+=1; subtitle=lines[i].strip(); obj.entry_text=text+' - '+subtitle
                obj.starts_body=text=='CHAPTER I'
                obj.style=ParagraphStyle('Chapter',parent=heading,spaceAfter=11)
                story.extend([obj,p(subtitle,heading)])
            else:story.append(obj)
        elif line.startswith('##'):
            level=2 if line.startswith('### ') else 1
            text=line.lstrip('# ').strip()
            story.append(p(text.upper() if level==1 else text,sub,'TOCEntry',level))
        elif line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+',x) for x in cells):rows.append(cells)
                i+=1
            story.extend([table(rows),Spacer(1,10)]);continue
        elif line.startswith('!['):
            match=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line); cap,path=match.groups(); path=(SOURCE.parent/path).resolve()
            with PILImage.open(path) as im: iw,ih=im.size
            scale=min(WIDTH/iw,460/ih)
            story.append(KeepTogether([Image(str(path),iw*scale,ih*scale),p(cap,caption,'FigureEntry'),Spacer(1,10)]))
        else:
            parts=[line]
            while i+1<len(lines) and lines[i+1].strip() and not lines[i+1].startswith(('#','|','![')):
                i+=1;parts.append(lines[i].strip())
            text=' '.join(parts)
            iscap=bool(re.match(r'Table [\dB]',text))
            obj=p(text,caption if iscap else body,'TableEntry' if iscap else None)
            if iscap:obj.keepWithNext=True
            story.append(obj)
        i+=1
    doc.multiBuild(story)
    print(out)

if __name__=='__main__':main()
