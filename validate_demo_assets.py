"""Decode every delivered video and independently reconcile CSV summaries/mappings/checksums."""
from pathlib import Path
import csv,json,hashlib,subprocess,re
import cv2,numpy as np,imageio_ffmpeg
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results/demo';report={'videos':[],'metrics':[],'files_checked':0}
for p in sorted(OUT.rglob('*.mp4')):
 cap=cv2.VideoCapture(str(p));n=0;fps=cap.get(cv2.CAP_PROP_FPS);w=cap.get(cv2.CAP_PROP_FRAME_WIDTH);h=cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
 while True:
  ok,im=cap.read()
  if not ok:break
  assert im.shape==(1080,1920,3);n+=1
 cap.release();expected=360 if '_short' in p.stem else 540
 assert n==expected and fps==30 and w==1920 and h==1080,(str(p),n,fps)
 assert p.stat().st_size<=25_000_000
 probe=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-i',str(p)],capture_output=True,text=True).stderr
 assert 'Video: h264' in probe and 'yuv420p' in probe
 prefix=p.stem.replace('_short','');mapping=list(csv.DictReader((p.parent/(prefix+'_frame_mapping.csv')).open()));mapping=[r for r in mapping if r['video']==p.name]
 assert len(mapping)==n and sum(r['phase']=='summary' for r in mapping)==60
 summary=json.loads((p.parent/'summary.json').read_text());assert set(r['source_frame'] for r in mapping if r['phase']=='data')==set(summary['source_frames'])
 report['videos'].append(dict(file=str(p.relative_to(OUT)),frames=n,fps=fps,width=w,height=h,bytes=p.stat().st_size,codec='h264',pixel_format='yuv420p'));print('PASS',p,n,flush=True)
for p in OUT.glob('*/per_frame.csv'):
 summary=json.loads((p.parent/'summary.json').read_text());rows=list(csv.DictReader(p.open()))
 for m in summary['methods']:
  r=[r for r in rows if r['method']==m['method']];matched=[x for x in r if x['status']=='matched'];d=np.array([float(x['depth_error']) for x in matched])
  assert len(matched)==m['matches'];assert sum(x['status']=='missed_gt' for x in r)==m['unmatched_gt'];assert sum(x['status']=='unmatched_prediction' for x in r)==m['unmatched_predictions']
  assert abs(float(np.sqrt(np.mean(d*d)))-m['depth_rmse_m'])<1e-10
  assert all(x['depth_error']=='' for x in r if x['status']!='matched')
  report['metrics'].append(dict(asset=p.parent.name,method=m['method'],matches=len(matched),depth_rmse_m=m['depth_rmse_m']))
for pair in json.loads((OUT/'G-F1/slider_pairs.json').read_text()):
 from PIL import Image
 assert Image.open(OUT/'G-F1'/pair['before']).size==Image.open(OUT/'G-F1'/pair['after']).size==(1600,900)
for step in json.loads((OUT/'G-C1/steps.json').read_text()):assert abs(step['z_corr_m']-step['z_raw_m']*step['ratio'])<1e-9
for name,meta in json.loads((OUT/'manifest.json').read_text())['files'].items():
 p=OUT/name;assert p.stat().st_size==meta['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['sha256'];report['files_checked']+=1
# All local HTML resource links exist (JS dynamic paths validated via steps/pairs above).
for target in re.findall(r'(?:href|src|poster)="([^"]+)"',(OUT/'index.html').read_text()):assert (OUT/target).exists(),target
report['status']='passed';(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('VALIDATION PASSED',len(report['videos']),'videos',report['files_checked'],'checksummed files')
