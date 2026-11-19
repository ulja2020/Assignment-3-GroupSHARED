from pathlib import Path
import tempfile,shutil,json,os,sys,time,hashlib,base64,importlib.util
r=Path('Assignment-3/drafts/draft-A').resolve(); t=Path(tempfile.mkdtemp(prefix='part_ii_clean_rebuild_',dir=Path('tmp').resolve()))
for name in ['Part_I_SVM.ipynb','Part_II_CNN.ipynb','signal_preparation.py','refresh_part_i_images.py','refresh_part_ii_images.py']:shutil.copy2(r/name,t/name)
shutil.copytree(r/'public_dataset',t/'public_dataset')
for folder in ['data','figures','figures_of_data']:(t/folder).mkdir()
for csv in (r/'data').glob('I[2345]_*.csv'):shutil.copy2(csv,t/'data'/csv.name)
assert not list((t/'data').glob('II*'))
print('Clean Part II test:',t,flush=True)
os.chdir(t);sys.path.insert(0,str(t));n=json.loads((t/'Part_II_CNN.ipynb').read_text(encoding='utf-8'));scope={'__name__':'__main__'}
for i,c in enumerate(n['cells']):
 if c['cell_type']=='code':
  start=time.time();exec(compile(''.join(c['source']),f'cell_{i}','exec'),scope)
  print('PASS cell',i,'seconds',round(time.time()-start,1),flush=True)
for folder,pattern in [('data','II*.csv'),('figures_of_data','II*.png'),('figures','II*.png')]:
 expected={p.name for p in (r/folder).glob(pattern)};actual={p.name for p in (t/folder).glob(pattern)}
 assert expected==actual,(folder,expected-actual,actual-expected)
 print('REBUILT',folder,len(actual),flush=True)
# Test the actual Part II refresh entry point in a separate process.
import subprocess
before=json.loads((t/'Part_II_CNN.ipynb').read_text(encoding='utf-8'))
fingerprints={str(p.relative_to(t)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['data','models'] for p in (t/folder).iterdir() if p.is_file()}
subprocess.run([sys.executable,str(t/'refresh_part_ii_images.py')],check=True)
after=json.loads((t/'Part_II_CNN.ipynb').read_text(encoding='utf-8'));count=0
for a,b in zip(before['cells'],after['cells']):
 assert a['source']==b['source'] and a.get('outputs')==b.get('outputs')
 for name,payload in b.get('attachments',{}).items():
  assert base64.b64decode(payload['image/png'])==(t/b['metadata']['image_source_directory']/name).read_bytes();count+=1
assert count==12
assert all(hashlib.sha256((t/name).read_bytes()).hexdigest()==h for name,h in fingerprints.items())
print('VERIFIED 12 refreshed attachments; cell sources, outputs, data and model hashes unchanged.',flush=True)
# Missing-image failure leaves the saved notebook unchanged.
first=next((t/'figures').glob('II*.png'));first.rename(first.with_suffix('.png.held'))
notebook_hash=hashlib.sha256((t/'Part_II_CNN.ipynb').read_bytes()).hexdigest()
result=subprocess.run([sys.executable,str(t/'refresh_part_ii_images.py')],capture_output=True)
assert result.returncode!=0 and hashlib.sha256((t/'Part_II_CNN.ipynb').read_bytes()).hexdigest()==notebook_hash
first.with_suffix('.png.held').rename(first)
print('VERIFIED missing-image failure preserves notebook.',flush=True)
(r.parents[2]/'tmp/part_ii_rebuild_location.txt').write_text(str(t),encoding='utf-8')
