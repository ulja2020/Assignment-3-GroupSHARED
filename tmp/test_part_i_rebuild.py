from pathlib import Path
import tempfile,shutil,json,os,time
original=Path('Assignment-3/drafts/draft-A').resolve()
test=Path(tempfile.mkdtemp(prefix='part_i_clean_rebuild_', dir=Path('tmp').resolve()))
for name in ['Part_I_SVM.ipynb','signal_preparation.py']:shutil.copy2(original/name,test/name)
shutil.copytree(original/'public_dataset',test/'public_dataset')
print('TEST DIRECTORY',test,flush=True)
os.chdir(test)
import sys
sys.path.insert(0,str(test))
n=json.loads((test/'Part_I_SVM.ipynb').read_text(encoding='utf-8'));scope={'__name__':'__main__'}
for i,c in enumerate(n['cells']):
 if c['cell_type']=='code':
  start=time.time();exec(compile(''.join(c['source']),f'cell_{i}','exec'),scope)
  print('PASS',i,'seconds',round(time.time()-start,1),flush=True)
expected_csv={p.name for p in (original/'data').glob('I[2345]_*.csv')}
expected_tables={p.name for p in (original/'figures_of_data').glob('I[2345]_*.png')}
expected_figures={p.name for p in (original/'figures').glob('I[2345]_*.png')}
assert expected_csv=={p.name for p in (test/'data').glob('*.csv')}
assert expected_tables=={p.name for p in (test/'figures_of_data').glob('*.png')}
assert expected_figures=={p.name for p in (test/'figures').glob('*.png')}
import pandas as pd
for name in expected_csv:
 a=pd.read_csv(original/'data'/name);b=pd.read_csv(test/'data'/name)
 pd.testing.assert_frame_equal(a,b,check_exact=False,rtol=1e-10,atol=1e-12)
print('VERIFIED',len(expected_csv),'CSVs',len(expected_tables),'table PNGs',len(expected_figures),'plots; all CSV values match.',flush=True)
Path('C:/Users/claud/Assignment-3-GroupSHARED/tmp/part_i_rebuild_location.txt').write_text(str(test))

