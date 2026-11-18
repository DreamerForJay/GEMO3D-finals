"""Decode all clips, check provenance, metric IoU and projected footprint geometry."""
import json,hashlib,csv
import numpy as np,cv2
import build_clean_demo as b
from evaluate_controlled_suite import bev_iou
checks=[];max_iou_delta=0.;max_pixel_iou_delta=0.
for f in b.IDS:
 for m in b.METHODS:
  r=b.MATCH.get((m,f))
  if not r:continue
  p=b.PREDS[m][f][int(r['pred_id'])];g=b.GT[f][int(r['gt_id'])]
  delta=abs(bev_iou(p,g)-r['bev_iou']);max_iou_delta=max(max_iou_delta,delta);assert delta<1e-6
  # Independent metric plane polygon clipping vs projected pixel overlap.
  u=b.project(p,f).astype(np.float32);v=b.project(g,f).astype(np.float32)
  a=cv2.contourArea(u);c=cv2.contourArea(v);i,_=cv2.intersectConvexConvex(u,v)
  diff=abs(i/(a+c-i)-r['bev_iou']);max_pixel_iou_delta=max(max_pixel_iou_delta,diff)
  # Near-nadir source camera; small perspective deviations allowed, never used as metric.
  assert diff<0.001,(m,f,diff)
for n,(view,ms) in b.SPECS.items():
 cap=cv2.VideoCapture(str(b.OUT/f'{n}.mp4'));count=0;shape=None;fps=cap.get(cv2.CAP_PROP_FPS)
 while True:
  ok,frame=cap.read()
  if not ok:break
  count+=1;shape=frame.shape[:2]
 cap.release();assert count==300 and abs(fps-30)<.01
 expected=(420*len(ms),1242) if view=='front' else (684,640*len(ms))
 assert shape==expected,(n,shape,expected)
 assert (b.OUT/f'{n}.mp4').stat().st_size<25_000_000
 checks.append({'video':n,'decoded_frames':count,'fps':fps,'shape':shape})
manifest=json.loads((b.OUT/'manifest.json').read_text())
for n,h in manifest['sha256'].items():assert hashlib.sha256((b.OUT/n).read_bytes()).hexdigest()==h
mapping=list(csv.DictReader((b.OUT/'frame_mapping.csv').open()))
assert len(mapping)==300 and set(r['source_frame'] for r in mapping)==set(b.IDS)
for s in json.loads((b.OUT/'summary.json').read_text()):assert s==b.stats(s['method'],b.IDS)
b.savej(b.OUT/'validation.json',{'status':'passed','videos':checks,'max_metric_iou_difference':max_iou_delta,'max_pixel_vs_metric_iou_difference':max_pixel_iou_delta,'mapping':'all 199 image IDs retained','hashes':'all manifest assets verified','summary':'recomputed controlled pairs','projection_visual_audit':['000000','000110','000170']})
print('PASS',len(checks),'videos; max IoU delta',max_iou_delta,'pixel approximation delta',max_pixel_iou_delta)
