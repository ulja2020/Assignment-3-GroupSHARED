# Analyse saved predictions only: no model loading, inference or training.
from pathlib import Path
import csv
import hashlib
import json
from collections import Counter
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

ROOT = Path.cwd()
if not (ROOT / 'Part_II_CNN.ipynb').is_file():
    raise RuntimeError('Run from the draft-A notebook directory.')


def read_ii4_csv(name):
    with (ROOT / 'data' / name).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


source_paths = [ROOT / 'data' / name for name in
                ['II3_test_predictions.csv', 'II3_class_metrics.csv', 'II2_input_inventory.csv',
                 'I2_recording_inventory.csv', 'II3_run_metadata.json']]
source_paths += [ROOT / 'models/II3_selected_model.keras']
fingerprints = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in source_paths}
predictions = read_ii4_csv('II3_test_predictions.csv')
inputs = {int(row['row_index']): row for row in read_ii4_csv('II2_input_inventory.csv')
          if row['partition'] == 'test'}
recordings = {int(row['recording_id']): row for row in read_ii4_csv('I2_recording_inventory.csv')}
assert len(predictions) == len(inputs) == 400
assert len({int(p['row_index']) for p in predictions}) == 400
assert {int(p['row_index']) for p in predictions} == set(inputs)
for p in predictions:
    original = inputs[int(p['row_index'])]
    assert all(p[k] == original[k] for k in ['recording_id', 'window_index'])
    assert p['actual_class'] == original['condition']
    assert original['load_hp'] == '3'
    assert p['actual_class'] == recordings[int(p['recording_id'])]['condition']

summary = []
for recording_id in sorted({int(p['recording_id']) for p in predictions}):
    rows = [p for p in predictions if int(p['recording_id']) == recording_id]
    meta = recordings[recording_id]
    wrong = Counter(p['predicted_class'] for p in rows if p['predicted_class'] != p['actual_class'])
    errors = sum(wrong.values())
    summary.append(dict(recording_id=recording_id, actual_class=meta['condition'],
                        diameter_inches=meta['diameter_inches'] or 'N/A', load_hp=int(meta['load_hp']),
                        windows=len(rows), errors=errors, error_rate_percent=100 * errors / len(rows),
                        wrong_predictions='; '.join(f'{key}: {value}' for key, value in sorted(wrong.items())) or 'None'))
assert len(summary) == 10 and sum(r['errors'] for r in summary) == 68
assert sum(r['windows'] for r in summary) == 400
assert all(r['diameter_inches'] == '0.014' for r in summary if r['errors'])
assert {r['recording_id']: r['errors'] for r in summary if r['errors']} == {172: 40, 188: 3, 200: 25}
with (ROOT / 'data/II4_recording_errors.csv').open('w', encoding='utf-8', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
    writer.writeheader()
    writer.writerows(summary)

import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont


def wrap_ii4_text(value, font, width):
    """Wrap text to a table column without shortening its contents."""
    result, current = [], ''
    for word in str(value).split():
        proposed = (current + ' ' + word).strip()
        if current and font.getlength(proposed) > width:
            result.append(current)
            current = word
        else:
            current = proposed
    return result + [current]


def render_ii4_table(name, title, widths, source_cell):
    """Render a CSV table, rounding metric displays only; preserve full CSV precision."""
    with (ROOT / 'data' / name).open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        columns, rows = list(reader.fieldnames), list(reader)
    regular = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 15)
    bold = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 15)
    heading = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 18)
    small = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 13)
    metric_columns = {'accuracy', 'macro_precision', 'macro_recall', 'macro_f1', 'precision', 'recall', 'f1'}
    values = [[column.replace('_', ' ') for column in columns]]
    values += [[f'{float(row[column]):.4f}' if column in metric_columns else row[column] for column in columns] for row in rows]
    wrapped = [[wrap_ii4_text(value, bold if i == 0 else regular, width - 16)
                for value, width in zip(row, widths)] for i, row in enumerate(values)]
    heights = [max(map(len, row)) * 20 + 12 for row in wrapped]
    image = Image.new('RGB', (sum(widths) + 32, 94 + sum(heights)), 'white')
    draw = ImageDraw.Draw(image)
    draw.text((16, 12), title, font=heading, fill='#172b45')
    draw.text((16, 44), f'Nb code cell 8 | Source: Nb code cell {source_cell}', font=small, fill='#486581')
    top = 78
    for i, (row, height) in enumerate(zip(wrapped, heights)):
        for j, (lines, width) in enumerate(zip(row, widths)):
            left = 16 + sum(widths[:j])
            draw.rectangle((left, top, left + width, top + height),
                fill='#203b54' if i == 0 else ('white' if i % 2 else '#edf4f8'), outline='#d6dfe5')
            for k, line in enumerate(lines):
                draw.text((left + 8, top + 6 + k * 20), line, font=bold if i == 0 else regular,
                          fill='white' if i == 0 else '#172b45')
        top += height
    image.save(ROOT / 'figures_of_data' / name.replace('.csv', '.png'))



render_ii4_table('II4_recording_errors.csv', 'Task II.4 - Errors by test recording',
                 [105, 145, 145, 90, 85, 80, 180, 205], 8)

plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
fig, ax = plt.subplots(figsize=(10, 6.3), layout='constrained')
labels = [f"{r['recording_id']} | {r['actual_class'].replace('_', ' ')} | "
          + ('normal' if r['diameter_inches'] == 'N/A' else r['diameter_inches'] + ' in') for r in summary]
rates = [r['error_rate_percent'] for r in summary]
ax.barh(range(len(summary)), rates, color='#bd503d', height=.65)
ax.set_yticks(range(len(summary)), labels)
ax.invert_yaxis()
ax.set(xlabel='Misclassified windows (%)', ylabel='Test recording | condition | fault diameter', xlim=(0, 116))
ax.set_xticks([0, 25, 50, 75, 100])
ax.grid(axis='x', alpha=.2)
ax.set_axisbelow(True)
for i, row in enumerate(summary):
    ax.text(row['error_rate_percent'] + 1.5, i,
            f"{row['errors']}/{row['windows']} ({row['error_rate_percent']:g}%)", va='center', fontsize=9)
fig.suptitle('CNN prediction errors by recording (all test recordings: 3 HP)\nTask II.4 | Notebook code cell 8',
             fontfamily='DejaVu Sans', fontsize=12, fontweight='normal', linespacing=1.6)
fig.get_layout_engine().set(h_pad=.16, w_pad=.06)
fig.savefig(ROOT / 'figures/II4_recording_errors.png', dpi=160, bbox_inches='tight', facecolor='white')
plt.close(fig)

# Confirm that analysis left every prediction, input and checkpoint source unchanged.
assert all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
           for name, digest in fingerprints.items())
audit = dict(task='II.4', investigation='B - Prediction Errors', source_sha256=fingerprints,
             test_windows=400, test_recordings=10, errors=68, recordings_with_errors=3,
             inner_outer_confusions=65, model_retrained=False, additional_inference=False,
             checks='Unique and complete test rows; recording/window/class alignment; source hashes unchanged')
(ROOT / 'data/II4_analysis_metadata.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
