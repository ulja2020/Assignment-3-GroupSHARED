import csv
import io
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, NumberObject
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1] / 'Assignment-3/drafts/draft-A'
SOURCE = ROOT / 'Part_II_CNN.pdf'
notebook = json.loads((ROOT / 'Part_II_CNN.ipynb').read_text(encoding='utf-8'))
reader = PdfReader(SOURCE)
assert len(reader.pages) == 11, 'Check the source PDF before appending II.3.'
for name, file in [('Report', 'arial.ttf'), ('ReportBold', 'arialbd.ttf'),
                   ('ReportItalic', 'ariali.ttf'), ('Mono', 'consola.ttf'), ('MonoBold', 'consolab.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/' + file))
pdfmetrics.registerFontFamily('Report', normal='Report', bold='ReportBold', italic='ReportItalic', boldItalic='ReportItalic')
INK, MUTED = colors.HexColor('#172b45'), colors.HexColor('#486581')
BODY = ParagraphStyle('body', fontName='Report', fontSize=10, leading=14, textColor=INK)
FRAME = (.73, .76, .79)


def inline(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', escape(text))
    text = re.sub(r'`([^`]+)`', r'<font name="Mono">\1</font>', text)
    sources = {'II.4-1': 'https://engineering.case.edu/bearingdatacenter/apparatus-and-procedures',
        'II.4-2': 'https://engineering.case.edu/bearingdatacenter/12k-drive-end-bearing-fault-data',
        'II.3-1': 'https://keras.io/api/optimizers/adam/',
        'II.3-2': 'https://keras.io/api/losses/probabilistic_losses/',
        'II.3-3': 'https://keras.io/guides/writing_your_own_callbacks/',
        'II.3-4': 'https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html',
        'II.3-5': 'https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html'}
    text = re.sub(r'II\.[34]-\d', lambda m: f'<link href="{sources[m[0]]}" color="#31688e">{m[0]}</link>', text)
    return text.replace('\n', ' ')


def read_table(filename):
    with (ROOT / 'data' / filename).open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames), list(reader)


class Appendix:
    def __init__(self):
        self.buffer = io.BytesIO()
        self.canvas = Canvas(self.buffer, pagesize=A4)
        self.top = 42

    def footer(self):
        c = self.canvas
        c.setFont('Report', 8)
        c.setFillColor(MUTED)
        c.drawString(42, 23, 'Assignment 3 - Part II')
        c.drawRightString(c._pagesize[0] - 42, 23, str(c.getPageNumber() + 9))

    def new_page(self, size=A4):
        self.footer()
        self.canvas.showPage()
        self.canvas.setPageSize(size)
        self.top = 42

    def text(self, text, heading=False, x=42, width=None, top=None):
        width = width or self.canvas._pagesize[0] - 84
        style = ParagraphStyle('heading', parent=BODY, fontName='ReportBold',
            fontSize=14 if heading == 'major' else 12, leading=19 if heading == 'major' else 16) if heading else BODY
        paragraph = Paragraph(inline(text), style)
        _, height = paragraph.wrap(width, 2000)
        actual_top = self.top if top is None else top
        if top is None and actual_top + height > self.canvas._pagesize[1] - 45:
            self.new_page(self.canvas._pagesize)
            actual_top = self.top
        paragraph.drawOn(self.canvas, x, self.canvas._pagesize[1] - actual_top - height)
        if top is None:
            self.top = actual_top + height + 10
        return actual_top + height + 10

    def markdown(self, cell):
        for part in ''.join(cell['source']).split('\n\n'):
            if part.startswith('## '):
                self.text(part[3:], 'major')
            elif part.startswith('### '):
                if self.top + 65 > self.canvas._pagesize[1] - 45:
                    self.new_page(self.canvas._pagesize)
                self.text(part[4:], True)
            elif part:
                self.text(part)

    def reference(self, number):
        if self.top + 22 > self.canvas._pagesize[1] - 45:
            self.new_page(self.canvas._pagesize)
        self.canvas.setFont('ReportItalic', 9)
        self.canvas.setFillColor(MUTED)
        self.canvas.drawString(42, self.canvas._pagesize[1] - self.top - 9,
            f'See notebook code cell {number} (execution label: In [{number}]).')
        self.top += 22

    def table(self, filename, title, source_cell, widths, size=8):
        columns, rows = read_table(filename)
        values = [columns] + [[row[column] for column in columns] for row in rows]
        rendered = []
        for index, row in enumerate(values):
            style = ParagraphStyle('cell', fontName='MonoBold' if index == 0 else 'Mono', fontSize=size,
                leading=size + 2, textColor=colors.white if index == 0 else INK, wordWrap='CJK')
            rendered.append([Paragraph(escape(value).replace('_', '_<br/>') if index == 0 and
                pdfmetrics.stringWidth(value, 'MonoBold', size) > width - 8 else escape(value), style)
                for value, width in zip(row, widths)])
        table = Table(rendered, colWidths=widths, hAlign='LEFT', repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#203b54')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#edf4f8')]),
            ('GRID', (0, 0), (-1, -1), .35, colors.HexColor('#d6dfe5')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        table_width, height = table.wrap(self.canvas._pagesize[0] - 84, 2000)
        assert self.top + 35 + height < self.canvas._pagesize[1] - 45
        heading_top = self.top
        c = self.canvas
        c.setFillColor(INK)
        c.setFont('MonoBold', 10)
        c.drawString(42, c._pagesize[1] - self.top - 10, title)
        c.setFont('Mono', 8)
        c.setFillColor(MUTED)
        c.drawString(42, c._pagesize[1] - self.top - 24, f'Nb code cell 8 | Source: Nb code cell {source_cell}')
        self.top += 35
        table.drawOn(c, 42, c._pagesize[1] - self.top - height)
        c.setStrokeColorRGB(*FRAME)
        c.setLineWidth(.6)
        c.rect(38, c._pagesize[1] - self.top - height - 4, table_width + 8,
               self.top + height + 4 - heading_top + 5, stroke=1, fill=0)
        self.top += height + 20

    def figure(self, filename, width, top=None, left=42):
        image = ImageReader(str(ROOT / 'figures' / filename))
        image_width, image_height = image.getSize()
        draw_height = width * image_height / image_width
        top = self.top if top is None else top
        assert top + draw_height < self.canvas._pagesize[1] - 45
        c = self.canvas
        c.drawImage(image, left, c._pagesize[1] - top - draw_height, width, draw_height)
        c.setStrokeColorRGB(*FRAME)
        c.setLineWidth(.6)
        c.rect(left - 4, c._pagesize[1] - top - draw_height - 4, width + 8, draw_height + 8, stroke=1, fill=0)
        self.top = top + draw_height + 15


appendix = Appendix()
appendix.markdown(notebook['cells'][37])
appendix.reference(8)
appendix.markdown(notebook['cells'][39])
appendix.table('II4_recording_errors.csv', 'Task II.4 - Errors by test recording', 8,
               [45, 65, 65, 40, 40, 40, 65, A4[0] - 444], 7)
appendix.new_page(landscape(A4))
appendix.markdown(notebook['cells'][41])
appendix.figure('II4_recording_errors.png', 600, left=120)
appendix.new_page()
appendix.markdown(notebook['cells'][43])
appendix.footer()
appendix.canvas.save()
appendix.buffer.seek(0)
new_pages = PdfReader(appendix.buffer)
writer = PdfWriter()
writer.clone_document_from_reader(reader)
for page in new_pages.pages:
    writer.add_page(page)
writer.add_outline_item('Task II.4 - Model Behavior', 11)

# Refresh the common date-free cover and the contents page without reflowing II.1-II.2.
buffer = io.BytesIO()
c = Canvas(buffer, pagesize=A4)
c.setFillColor(INK)
for text, font, size, y in [('MOD550', 'Report', 11, 756.8898), ('Assignment 3', 'ReportBold', 34, 649.8898),
    ('Part II', 'Report', 20, 605.8898), ('Deep Learning for', 'ReportBold', 23, 553.8898),
    ('Engineering Applications', 'ReportBold', 23, 521.8898), ('Tasks II.1-II.4', 'Report', 11, 460.8898)]:
    c.setFont(font, size)
    c.drawString(54, y, text)
c.save()
buffer.seek(0)
writer.pages[0].replace_contents(None)
writer.pages[0].merge_page(PdfReader(buffer).pages[0])
buffer = io.BytesIO()
c = Canvas(buffer, pagesize=A4)
c.setFillColor(INK)
c.setFont('ReportBold', 24)
c.drawString(42, A4[1] - 70, 'Table of contents')
links = []
for top, title, target in [(125, 'Task II.1 - Engineering Problem and Dataset', 2),
                          (157, 'Task II.2 - Data Preparation and Implementation', 3),
                          (189, 'Task II.3 - Training and Evaluation', 7),
                          (221, 'Task II.4 - Model Behavior', 11)]:
    c.setFont('ReportBold', 11)
    c.drawString(42, A4[1] - top, title)
    c.drawRightString(A4[0] - 42, A4[1] - top, str(target - 1))
    links.append((target, [42, A4[1] - top - 8, A4[0] - 42, A4[1] - top + 13]))
c.setFont('Report', 9)
c.setFillColor(MUTED)
c.drawString(42, 65, 'Page numbers refer to the numbered report pages that follow.')
c.drawRightString(A4[0] - 42, 23, 'ii')
c.save()
buffer.seek(0)
writer.pages[1].replace_contents(None)
writer.pages[1].pop(NameObject('/Annots'), None)
writer.pages[1].merge_page(PdfReader(buffer).pages[0])
for target, rect in links:
    annotation = DictionaryObject({NameObject('/Type'): NameObject('/Annot'),
        NameObject('/Subtype'): NameObject('/Link'), NameObject('/Rect'): ArrayObject([NumberObject(x) for x in rect]),
        NameObject('/Border'): ArrayObject([NumberObject(0)] * 3),
        NameObject('/Dest'): ArrayObject([writer.pages[target].indirect_reference, NameObject('/Fit')])})
    writer.add_annotation(1, annotation)
output = ROOT / 'Part_II_CNN_updated.pdf'
with output.open('wb') as stream:
    writer.write(stream)
with pdfplumber.open(output) as document:
    text = '\n'.join(page.extract_text() or '' for page in document.pages)
    assert text.count('See notebook code cell ') == 8
    assert all(sorted((round(page.width), round(page.height))) == [595, 842] for page in document.pages)
    assert 'MAE and RMSE' in text and 'recording 172 contributes 40' in text
    print('Prepared', len(document.pages), 'A4 pages; eight code references and all II.4 sections.', flush=True)
