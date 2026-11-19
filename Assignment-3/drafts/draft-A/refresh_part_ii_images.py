"""Refresh Part II attachments after saving and closing the notebook.

Uses the shared attachment-refresh function in refresh_part_i_images.py.
This command updates embedded images only; it does not train or evaluate a model.
"""
from pathlib import Path
from refresh_part_i_images import refresh


if __name__ == '__main__':
    destination = Path(__file__).resolve().parent / 'Part_II_CNN.ipynb'
    print(f'Refreshed {refresh(destination)} embedded images. Reopen {destination.name}.')
