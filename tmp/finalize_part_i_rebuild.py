from pathlib import Path
import json,importlib.util,shutil,base64
r=Path('Assignment-3/drafts/draft-A').resolve()
t=Path(Path('tmp/part_i_rebuild_location.txt').read_text())
shutil.copy2(r/'Part_I_SVM.ipynb',t/'Part_I_SVM.ipynb')
spec=importlib.util.spec_from_file_location('refresh',r/'refresh_part_i_images.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
before=json.loads((t/'Part_I_SVM.ipynb').read_text(encoding='utf-8'))
assert module.refresh(t/'Part_I_SVM.ipynb')==18
after=json.loads((t/'Part_I_SVM.ipynb').read_text(encoding='utf-8'))
for a,b in zip(before['cells'],after['cells']):
 assert a['source']==b['source'] and a.get('outputs')==b.get('outputs')
 for filename,payload in b.get('attachments',{}).items():
  assert base64.b64decode(payload['image/png'])==(t/b['metadata']['image_source_directory']/filename).read_bytes()
for image in (t/'figures_of_data').glob('I[23]_*.png'):
 shutil.copy2(image,r/'figures_of_data'/image.name)
assert module.refresh(r/'Part_I_SVM.ipynb')==18
p=r/'Readme.md';s=p.read_text(encoding='utf-8');s+='\nValidation: executed every Part I code cell in an isolated directory initially containing only the notebook, shared preparation module and original source cache. Recreated all 17 CSVs, 17 table PNGs and eight plots. All CSV values matched the existing results (floating-point tolerance 1e-10 relative, 1e-12 absolute). Verified all 18 refreshed attachments exactly match their source PNGs and that refreshing preserves cell source and saved outputs.\n';p.write_text(s,encoding='utf-8')
print('Clean rebuild and attachment refresh passed; numerical artifacts preserved.')
