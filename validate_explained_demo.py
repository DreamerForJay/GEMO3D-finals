"""Full decoding and independent numerical reconciliation, including synthetic orientation intervention."""
import json,csv,hashlib,math
from pathlib import Path
import cv2,numpy as np
from render_sequence_video import corners
from evaluate_controlled_suite import bev_iou
from build_demo_assets import GT,PREDS
OUT=Path(__file__).resolve().parent/'results/explained_demo';report={'videos':[],'measurements':[]}
for path in sorted(OUT.glob('*.mp4')):
 cap=cv2.VideoCapture(str(path));fps=cap.get(cv2.CAP_PROP_FPS);n=0
 while True:
  ok,im=cap.read()
  if not ok:break
  assert im.shape==(1080,1920,3);n+=1
 cap.release();expected=540 if path.stem.endswith('_only') else 360;assert fps==30 and n==expected
 assert path.stat().st_size<25_000_000
 rows=list(csv.DictReader((OUT/(path.stem+'_mapping.csv')).open()));assert len(rows)==n;assert sum(r['phase']=='summary' for r in rows)==60
 if path.stem!='yaw_geometry':
  s=json.loads((OUT/(path.stem+'_summary.json')).read_text());assert set(r['source_frame'] for r in rows if r['phase']=='data')==set(s['frames'])
  data=list(csv.DictReader((OUT/(path.stem+'_per_frame.csv')).open()))
  for r in data:
   if r['matched']=='True':
    pred=PREDS[r['method']][r['frame']][0];gt=GT[r['frame']][0]
    assert abs(float(r['depth_error'])-(pred['z']-gt['z']))<1e-10
    err=math.degrees(abs(math.atan2(math.sin(pred['ry']-gt['ry']),math.cos(pred['ry']-gt['ry']))));assert abs(err-float(r['yaw_error_deg']))<1e-10
   else:assert r['depth_error']=='' and r['yaw_error_deg']==''
  for method in s['methods']:
   ds=[float(r['depth_error']) for r in data if r['method']==method['method'] and r['matched']=='True'];assert len(ds)==method['matches'];assert abs(np.sqrt(np.mean(np.square(ds)))-method['depth_rmse_m'])<1e-10
   report['measurements'].append({'video':path.stem,'method':method['method'],'matches':len(ds),'rmse':method['depth_rmse_m']})
 else:
  assert {r['source_frame'] for r in rows if r['phase']=='data'}=={'000110'};assert {int(r['simulation_sample']) for r in rows if r['phase']=='data'}==set(range(121))
  ds=list(csv.DictReader((OUT/'yaw_geometry_per_frame.csv').open()));g=GT['000110'][0]
  for r in ds:
   p=dict(g,ry=g['ry']+math.radians(float(r['signed_yaw_offset_deg'])));err=np.sqrt(np.mean(np.sum((corners(p)-corners(g))**2,axis=0)));assert abs(err-float(r['corner_rms_displacement_m']))<1e-10;assert abs(bev_iou(p,g)-float(r['bev_iou']))<1e-10;assert float(r['center_error_m'])==0
  assert abs(float(ds[60]['corner_rms_displacement_m']))<1e-10
 report['videos'].append(dict(file=path.name,frames=n,fps=fps,bytes=path.stat().st_size));print('PASS',path.name,n,flush=True)
manifest=json.loads((OUT/'manifest.json').read_text())
for p,meta in manifest['files'].items():assert hashlib.sha256((OUT/p).read_bytes()).hexdigest()==meta['sha256']
report['checksummed_files']=len(manifest['files']);report['status']='passed';(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('VALIDATED',len(report['videos']),'videos')
