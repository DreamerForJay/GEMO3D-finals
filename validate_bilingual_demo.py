import math,json,csv,hashlib
import numpy as np,cv2
import build_bilingual_demo as b
rows=list(csv.DictReader((b.OUT/'yaw_geometry.csv').open()));errors=[]
# Independent closed-form extrema: top and bottom Y are positive, so far roof / near bottom support.
for r in rows:
 a=math.radians(float(r['yaw_deg']));halfz=abs(b.L/2*math.sin(a))+abs(b.W/2*math.cos(a))
 top=b.FY*(b.Y-b.H)/(b.Z+halfz);bottom=b.FY*b.Y/(b.Z-halfz);h=bottom-top
 assert abs(h-float(r['h2d_px']))<1e-9
 assert abs(b.FY*b.H/h-float(r['z_pinhole_m']))<1e-9
 assert abs(float(r['ratio'])*float(r['z_pinhole_m'])-b.Z)<1e-9
 assert float(r['z_true_m'])==10
for n,h in json.loads((b.OUT/'manifest.json').read_text())['sha256'].items():assert hashlib.sha256((b.OUT/n).read_bytes()).hexdigest()==h
checks=[]
for p in sorted(b.OUT.glob('*.mp4')):
 cap=cv2.VideoCapture(str(p));fps=cap.get(cv2.CAP_PROP_FPS);n=0
 while True:
  ok,im=cap.read()
  if not ok:break
  n+=1
 cap.release();expected=360 if p.name.startswith('yaw_') else 300
 assert n==expected and fps==30,(p,n,fps)
 assert p.stat().st_size<25_000_000
 checks.append(dict(file=p.name,frames=n,shape=im.shape if im is not None else None))
assert len(checks)==28
for n in ['per_frame.csv','summary.json']:assert (b.OUT/n).read_bytes()==(b.b.OUT/n).read_bytes()
for name in b.b.SPECS:
 for f in ['000000','000110','000198']:
  v,ms=b.b.SPECS[name]
  for m in ms:
   zh=np.array(b.panel(f,m,v,'zh'))[142:];en=np.array(b.panel(f,m,v,'en'))[142:];assert np.array_equal(zh,en)
b.b.savej(b.OUT/'validation.json',{'status':'passed','decoded_videos':checks,'synthetic_geometry':'360 samples checked against independent analytic extrema; Z*r identity verified','controlled_metrics':'byte-identical CSV/JSON to clean version','languages':'underlying RGB overlays identical on first/middle/last samples','sha256':'all listed artifacts verified'})
print('PASS 28 videos; analytic yaw validation; unchanged controlled metrics')
