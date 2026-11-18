from pathlib import Path
import csv,re,os,json
import pdfplumber
from pypdf import PdfReader
r=Path('Assignment-3/drafts/draft-A')
with pdfplumber.open(r/'Part_II_CNN.pdf') as old, pdfplumber.open(r/'Part_II_CNN_updated.pdf') as new:
 assert len(new.pages)==14
 assert all(old.pages[i].extract_text()==new.pages[i].extract_text() for i in range(2,11))
 assert all(sorted((round(p.width),round(p.height)))==[595,842] for p in new.pages)
 text='\n'.join(p.extract_text() or '' for p in new.pages)
 assert text.count('See notebook code cell ')==8
 norm=lambda t: re.sub(r'\s+','',t).replace('**','').replace('`','')
 n=json.loads((r/'Part_II_CNN.ipynb').read_text())
 body=norm('\n'.join(p.extract_text() or '' for p in new.pages[11:]))
 for i in [37,39,41,43]:
  for paragraph in ''.join(n['cells'][i]['source']).split('\n\n'):
   assert norm(paragraph.lstrip('# ')) in body,paragraph[:80]
 with (r/'data/II4_recording_errors.csv').open() as f:
  for row in csv.DictReader(f):
   for value in row.values(): assert norm(value) in norm(new.pages[11].extract_text())
 frames=[x for p in new.pages for x in p.rects if x.get('stroke') and x.get('stroking_color') and tuple(round(v,2) for v in x['stroking_color'])==(.73,.76,.79)]
 assert len(frames)==12,len(frames)
pdf=PdfReader(r/'Part_II_CNN_updated.pdf'); links=[a.get_object() for a in pdf.pages[1]['/Annots']]
assert [pdf.get_page_number(a['/Dest'][0].get_object()) for a in links]==[2,3,7,11]
os.replace(r/'Part_II_CNN_updated.pdf',r/'Part_II_CNN.pdf')
p=r/'Readme.md'; s=p.read_text(encoding='utf-8').replace('eleven A4','fourteen A4').replace('Tasks II.1-II.3; CSV-backed','Tasks II.1-II.4; CSV-backed').replace('now covers II.1-II.3 in fourteen','now covers II.1-II.4 in fourteen').replace('covers Tasks II.1-II.3 in fourteen','covers Tasks II.1-II.4 in fourteen')
s=s.replace('The PDF currently covers II.1-II.3; this update adds II.4 to the notebook and README.', 'The PDF now covers II.1-II.4 in fourteen A4 pages, including the recording table, error-rate figure and full interpretation. The linked contents and date-free cover reflect II.4.')
s+='| 2026-11-18 | ChatGPT/Codex with Python and PDF rendering | Update the Part II PDF to include II.4. | Existing II.1-II.3 body pages, formatting, grey frames and code references. | Added three II.4 pages; verified all II.4 prose and 80 table values, eight code references, twelve frames and four contents destinations; visually reviewed the new pages. |\n'
p.write_text(s,encoding='utf-8')
print('Updated PDF: 14 A4 pages. Verified preserved earlier body, all II.4 prose, 80 table values, 12 frames, 4 contents links.')
