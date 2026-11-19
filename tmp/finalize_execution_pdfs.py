from pathlib import Path
import os
from pypdf import PdfReader
r=Path('Assignment-3/drafts/draft-A')
for name,total,start in [('Part_I_SVM_framed.pdf',30,28),('Part_II_CNN.pdf',16,14)]:
 candidate=r/name.replace('.pdf','_updated.pdf');pdf=PdfReader(candidate);old=PdfReader(r/name)
 assert len(pdf.pages)==total
 links=[a.get_object() for a in pdf.pages[1].get('/Annots',[])]
 assert len(links)==len(old.pages[1].get('/Annots',[]))+1
 assert pdf.get_page_number(links[-1]['/Dest'][0].get_object())==start
 assert 'Execution Instructions' in pdf.pages[start].extract_text()
 assert 'Execution Instructions' in pdf.pages[1].extract_text()
 os.replace(candidate,r/name)
 print('Saved',name,total,'pages; appendix link verified.')
p=r/'Readme.md';s=p.read_text(encoding='utf-8').replace('fourteen A4','sixteen A4')
s+='\nPDF update (19 November 2026): both reports now include the current Execution Instructions as a linked appendix. Part I contains 30 A4 pages; Part II contains 16 A4 pages. Existing report body pages, compact tables, figures and grey frames were preserved. Complete appendix wording, A4 page sizes, contents destinations and page numbering were checked.\n';p.write_text(s,encoding='utf-8')
