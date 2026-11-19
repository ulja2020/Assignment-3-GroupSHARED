from pathlib import Path
import io,re
from xml.sax.saxutils import escape
from pypdf import PdfReader,PdfWriter
from pypdf.generic import DictionaryObject,NameObject,ArrayObject,FloatObject,NumberObject
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Preformatted,KeepTogether
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]/'Assignment-3/drafts/draft-A'
for name,file in [('Report','arial.ttf'),('ReportBold','arialbd.ttf'),('ReportItalic','ariali.ttf'),('Mono','consola.ttf')]:
 pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Report',normal='Report',bold='ReportBold',italic='ReportItalic')
INK=colors.HexColor('#172b45');MUTED=colors.HexColor('#486581')
body=ParagraphStyle('body',fontName='Report',fontSize=10,leading=14,textColor=INK,spaceAfter=9)
head=ParagraphStyle('head',parent=body,fontName='ReportBold',fontSize=14,leading=19,spaceAfter=12)
sub=ParagraphStyle('sub',parent=body,fontName='ReportBold',fontSize=12,leading=16,spaceBefore=6,spaceAfter=8,keepWithNext=True)
minor=ParagraphStyle('minor',parent=sub,fontSize=10.5,leading=14)
mono=ParagraphStyle('mono',fontName='Mono',fontSize=8,leading=12,textColor=INK,spaceAfter=12)
readme=(ROOT/'Readme.md').read_text(encoding='utf-8')
section=readme.split('## Execution Instructions\n',1)[1].split('## Task I.1',1)[0].strip()
assert '**' not in section

def inline(t):
 return re.sub(r'`([^`]+)`',r'<font name="Mono">\1</font>',escape(t)).replace('\n',' ')

def appendix(part,start):
 buffer=io.BytesIO();story=[Paragraph('Execution Instructions',head)]
 for block in re.split(r'\n\s*\n',section):
  if block.startswith('```'):
   content='\n'.join(block.splitlines()[1:-1])
   # Keep the complete sequence together and retain its literal line breaks.
   story.append(KeepTogether([Preformatted(content,mono)]))
  elif block.startswith('#### '):story.append(Paragraph(inline(block[5:]),minor))
  elif block.startswith('### '):story.append(Paragraph(inline(block[4:]),sub))
  else:story.append(Paragraph(inline(block),body))
 def footer(c,d):
  c.setFont('Report',8);c.setFillColor(MUTED)
  c.drawString(42,23,'Assignment 3 - Part '+part)
  c.drawRightString(A4[0]-42,23,str(start+d.page-2))
 doc=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=45)
 doc.build(story,onFirstPage=footer,onLaterPages=footer);buffer.seek(0);return PdfReader(buffer)

for filename,part in [('Part_I_SVM_framed.pdf','I'),('Part_II_CNN.pdf','II')]:
 reader=PdfReader(ROOT/filename);start=len(reader.pages);extra=appendix(part,start)
 writer=PdfWriter();writer.clone_document_from_reader(reader)
 for page in extra.pages:writer.add_page(page)
 writer.add_outline_item('Execution Instructions',start)
 # Add one appendix entry to the existing contents, retaining all task links.
 overlay=io.BytesIO();from reportlab.pdfgen.canvas import Canvas
 c=Canvas(overlay,pagesize=A4);c.setFont('ReportBold',11);c.setFillColor(INK)
 entry_y = 190 if part == 'I' else A4[1] - 253
 entry_x = 54 if part == 'I' else 42
 c.drawString(entry_x,entry_y,'Execution Instructions');c.drawRightString(A4[0]-entry_x,entry_y,str(start-1));c.save();overlay.seek(0)
 writer.pages[1].merge_page(PdfReader(overlay).pages[0])
 annotation=DictionaryObject({NameObject('/Type'):NameObject('/Annot'),NameObject('/Subtype'):NameObject('/Link'),
  NameObject('/Rect'):ArrayObject([FloatObject(v) for v in [entry_x,entry_y-6,A4[0]-entry_x,entry_y+15]]),
  NameObject('/Border'):ArrayObject([NumberObject(0)]*3),
  NameObject('/Dest'):ArrayObject([writer.pages[start].indirect_reference,NameObject('/Fit')])})
 writer.add_annotation(1,annotation)
 output=ROOT/filename.replace('.pdf','_updated.pdf')
 with output.open('wb') as f:writer.write(f)
 with pdfplumber.open(ROOT/filename) as old,pdfplumber.open(output) as new:
  assert all(old.pages[i].extract_text()==new.pages[i].extract_text() for i in range(2,start))
  assert all(sorted((round(p.width),round(p.height)))==[595,842] for p in new.pages)
  full='\n'.join(p.extract_text() or '' for p in new.pages[start:])
  norm=lambda t: re.sub(r'\s+','',t.replace('`',''))
  for block in re.split(r'\n\s*\n',section):
   content='\n'.join(block.splitlines()[1:-1]) if block.startswith('```') else block.lstrip('# ')
   assert norm(content) in norm(full),content[:100]
  assert norm('CNN training (and evaluation) results') in norm(full)
  print(filename,':',start,'->',len(new.pages),'pages; preserved body and verified complete execution instructions.',flush=True)

