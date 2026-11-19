from pathlib import Path
import re,json,os
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,ArrayObject
import pdfplumber
PROJECT=Path('C:/Users/claud/Assignment-3-GroupSHARED/Assignment-3/drafts/draft-A')
PDF_SOURCE=Path('C:/Users/claud/PDFs Assignment 3')
OUTPUT=Path(__file__).resolve().parent
code=(PDF_SOURCE/'scripts/update_ii3_pdf.py').read_text(encoding='utf-8').split('appendix = Appendix()')[0]
code=code.replace("ROOT = Path(__file__).resolve().parents[1] / 'Assignment-3/drafts/draft-A'",'ROOT = PROJECT')
code=code.replace("SOURCE = ROOT / 'Part_II_CNN.pdf'","SOURCE = PDF_SOURCE / 'Part_II_CNN.pdf'")
code=code.replace("assert len(reader.pages) == 7, 'Check the source PDF before appending II.3.'",'')
# Render the source cell reference for each replacement table correctly.
code=code.replace("f'Nb code cell 7 | Source: Nb code cell {source_cell}'", "f'Nb code cell {getattr(self, \"table_cell\", 7)} | Source: Nb code cell {source_cell}'")
ns=dict(PROJECT=PROJECT,PDF_SOURCE=PDF_SOURCE)
exec(compile(code,'renderer','exec'),ns)
ns['BODY'].fontSize=9.5;ns['BODY'].leading=13
notebook=ns['notebook'];A4=ns['A4']

def builder(index):
    a=ns['Appendix']()
    def footer():
        c=a.canvas;c.setFont('Report',8);c.setFillColor(ns['MUTED'])
        c.drawString(42,23,'Assignment 3 - Part II')
        c.drawRightString(c._pagesize[0]-42,23,str(index-1))
    a.footer=footer
    return a

def finish(a):
    a.footer();a.canvas.save();a.buffer.seek(0)
    reader=PdfReader(a.buffer)
    assert len(reader.pages)==1,'Page overflow: review layout before replacing reports.'
    return reader.pages[0]

replacements={}
a=builder(3)
for index,number in [(4,2),(6,3),(8,4)]:
    a.markdown(notebook['cells'][index]);a.reference(number)
replacements[3]=finish(a)
a=builder(5);a.canvas.setPageSize(ns['landscape'](A4));a.table_cell=4
a.text('Task II.2 - Preparation and implementation checks',True)
a.markdown(notebook['cells'][14])
a.table('II2_preprocessing_checks.csv','Task II.2 - Preparation and implementation checks','2-4',
        [190,170,ns['landscape'](A4)[0]-444],7.5)
replacements[5]=finish(a)
a=builder(7)
for index,number in [(19,5),(21,None),(22,6),(24,7)]:
    a.markdown(notebook['cells'][index])
    if number:a.reference(number)
replacements[7]=finish(a)
a=builder(8);a.markdown(notebook['cells'][26])
a.table('II3_training_summary.csv','Task II.3 - Training and checkpoint selection',5,[155,A4[0]-239],8)
a.markdown(notebook['cells'][28]);a.figure('II3_learning_curves.png',A4[0]-92,left=46)
replacements[8]=finish(a)
a=builder(11);a.table_cell=8
a.markdown(notebook['cells'][37]);a.reference(8);a.markdown(notebook['cells'][39])
a.table('II4_recording_errors.csv','Task II.4 - Errors by test recording',8,
        [45,65,65,40,40,40,65,A4[0]-444],7)
replacements[11]=finish(a)

appendix_code=(PDF_SOURCE/'update_reports.py').read_text(encoding='utf-8').split('for filename,part in')[0]
appendix_code=appendix_code.replace("bulletText='\x07'","bulletText='-'")
app={'__file__':str(PDF_SOURCE/'update_reports.py')}
exec(compile(appendix_code,'appendix','exec'),app)
assert re.sub(r'\s+','', ''.join(notebook['cells'][-1]['source'])) == re.sub(r'\s+','', '## Execution Instructions\n'+app['section'])
for filename,part,start in [('Part_I_SVM_framed.pdf','I',28),('Part_II_CNN.pdf','II',14)]:
    original=PdfReader(PDF_SOURCE/filename)
    writer=PdfWriter();writer.clone_document_from_reader(original)
    if part=='II':
        for index,page in replacements.items():
            writer.pages[index].replace_contents(None)
            writer.pages[index].pop(NameObject('/Annots'),None)
            writer.pages[index].merge_page(page)
    while len(writer.pages)>start:writer.remove_page(len(writer.pages)-1)
    for page in app['appendix'](part,start).pages:writer.add_page(page)
    target=ArrayObject([writer.pages[start].indirect_reference,NameObject('/Fit')])
    writer.pages[1]['/Annots'][-1].get_object()[NameObject('/Dest')]=target
    node=writer.get_outline_root().get('/First')
    while node:
        item=node.get_object()
        if item.get('/Title')=='Execution Instructions':
            item.pop(NameObject('/A'),None);item[NameObject('/Dest')]=target
        node=item.get('/Next')
    output=OUTPUT/(filename.replace('.pdf','_updated.pdf') if OUTPUT.resolve()==PDF_SOURCE.resolve() else filename)
    with output.open('wb') as stream:writer.write(stream)
    with pdfplumber.open(PDF_SOURCE/filename) as old,pdfplumber.open(output) as new:
        for i in range(start):
            if part=='II' and i in replacements:continue
            assert old.pages[i].extract_text()==new.pages[i].extract_text(),(filename,i)
        assert all(sorted((round(p.width),round(p.height)))==[595,842] for p in new.pages)
        text='\n'.join(p.extract_text() or '' for p in new.pages)
        assert '.keras' not in text and 'saved copy' not in text
        assert 'in memory' in text
        print(filename,len(new.pages),'pages; unchanged pages and removal of model-archive references verified.',flush=True)

# When run from the external PDF folder, promote only after both reports pass validation.
if OUTPUT.resolve()==PDF_SOURCE.resolve():
    for name in ['Part_I_SVM_framed.pdf','Part_II_CNN.pdf']:
        os.replace(OUTPUT/name.replace('.pdf','_updated.pdf'),OUTPUT/name)
