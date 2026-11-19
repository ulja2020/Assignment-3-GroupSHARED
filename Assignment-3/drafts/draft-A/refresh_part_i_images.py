"""Refresh saved Part I markdown attachments after rebuilding its external PNGs.

Save and close Part_I_SVM.ipynb before running this script, then reopen it.
No model, numerical results or code outputs are modified.
"""

import base64
import json
import os
from pathlib import Path


def refresh(notebook_path):
    notebook_path = Path(notebook_path)
    notebook = json.loads(notebook_path.read_text(encoding='utf-8'))
    updates = []
    for cell in notebook['cells']:
        for filename in cell.get('attachments', {}):
            folder = cell['metadata']['image_source_directory']
            source = notebook_path.parent / folder / filename
            # Read all images before writing: a missing file leaves the notebook intact.
            updates.append((cell, filename, base64.b64encode(source.read_bytes()).decode('ascii')))
    for cell, filename, payload in updates:
        cell['attachments'][filename] = {'image/png': payload}
    temporary = notebook_path.with_suffix('.ipynb.refreshing')
    temporary.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    os.replace(temporary, notebook_path)
    return len(updates)


if __name__ == '__main__':
    destination = Path(__file__).resolve().parent / 'Part_I_SVM.ipynb'
    print(f'Refreshed {refresh(destination)} embedded images. Reopen {destination.name}.')
