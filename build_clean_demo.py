"""Minimal, separate RGB/real top-camera comparisons from controlled predictions."""
from pathlib import Path
import json,csv,subprocess,hashlib
import numpy as np,cv2,imageio_ffmpeg
from build_demo_assets import DATA,GT,PS,PREDS,ROWS,IDS,stats,csvout,savej
from render_sequence_video import corners,draw_box
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'results/clean_demo';OUT.mkdir(exist_ok=True)
METHODS={'A':'Pinhole','D':'Rank-1','F_no_tightfit':'Full / no tightfit','F':'Full'}
GREEN=(80,225,65);RED=(65,65,245) # OpenCV BGR
METAS={f:json.loads((DATA/'meta'/f'{f}.json').read_text()) for f in IDS}
MATCH={(r['method'],r['frame']):r for r in ROWS}
def project(o,f):
 # Common horizontal footprint plane: GT bottom Y. BEV metric ignores predicted Y.
 p=corners(o)[:,:4].copy();p[1,:]=GT[f][0]['y']
 s=np.vstack([p[2],p[0],-p[1],np.ones(4)])
 meta=METAS[f];world=np.linalg.inv(np.array(meta['extrinsics']).reshape(4,4))@s
 t=np.array(meta['top_camera']['extrinsics']).reshape(4,4)@world
 assert np.all(t[0]>0)
 k=meta['top_camera']['intrinsics']
 return np.column_stack([k['fx']*t[1]/t[0]+k['cx'],k['fy']*(-t[2])/t[0]+k['cy']])
def poly(a,pts,color,dash=False):
 for u,v in zip(pts,np.roll(pts,-1,axis=0)):
  if dash:
   n=max(2,int(np.linalg.norm(u-v)/9))
   for i in range(0,n,2):cv2.line(a,tuple(np.round(u+(v-u)*i/n).astype(int)),tuple(np.round(u+(v-u)*min(i+1,n)/n).astype(int)),color,3,cv2.LINE_AA)
  else:cv2.line(a,tuple(np.round(u).astype(int)),tuple(np.round(v).astype(int)),color,3,cv2.LINE_AA)
def panel(f,m,view):
 a=cv2.imread(str(DATA/('image_2' if view=='front' else 'bev_iou')/f'{f}.png'))
 for obs,col,dash in [(GT[f],GREEN,True),(PREDS[m][f],RED,False)]:
  for o in obs:
   if view=='front':draw_box(a,o,PS[f],col,dash)
   else:poly(a,project(o,f),col,dash)
 if view=='bev':a=cv2.resize(a,(640,640),interpolation=cv2.INTER_AREA)
 # Front source width1242 height375; pad one row for yuv420p.
 if view=='front':a=cv2.copyMakeBorder(a,0,1,0,0,cv2.BORDER_CONSTANT)
 h,w=a.shape[:2];out=np.full((h+44,w,3),22,np.uint8);out[44:]=a
 cv2.putText(out,METHODS[m],(14,29),cv2.FONT_HERSHEY_SIMPLEX,.65,(245,245,245),1,cv2.LINE_AA)
 r=MATCH.get((m,f));label=(f"BEV IoU {r['bev_iou']:.2f}" if view=='bev' else f"3D error {r['center_error']:.2f} m") if r else 'unmatched'
 cv2.putText(out,label,(w-230,29),cv2.FONT_HERSHEY_SIMPLEX,.6,(245,245,245),1,cv2.LINE_AA)
 return out
SPECS={f'{v}_{m}':(v,[m]) for m in METHODS for v in ['front','bev']}
SPECS.update({f'{v}_{n}':(v,ms) for v in ['front','bev'] for n,ms in [('compensation',['A','D']),('tightfit',['F_no_tightfit','F'])]})
def render(f,v,ms):return np.concatenate([panel(f,m,v) for m in ms],axis=0 if v=='front' else 1)
def main():
 mapping=[{'output_frame':i,'source_frame':IDS[int(i*198/299)]} for i in range(300)]
 csvout(OUT/'frame_mapping.csv',mapping)
 for name,(view,ms) in SPECS.items():
  sample=render('000110',view,ms);h,w=sample.shape[:2];cv2.imwrite(str(OUT/f'{name}.jpg'),sample)
  p=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r','30','-i','-','-an','-c:v','libx264','-preset','veryfast','-threads','3','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/f'{name}.mp4')],stdin=subprocess.PIPE)
  last=None
  for row in mapping:
   f=row['source_frame']
   if f!=last:buf=render(f,view,ms).tobytes();last=f
   p.stdin.write(buf)
  p.stdin.close();assert p.wait()==0;print('DONE',name,flush=True)
 csvout(OUT/'per_frame.csv',[r for r in ROWS if r['method'] in METHODS]);savej(OUT/'summary.json',[stats(m,IDS) for m in METHODS])
 savej(OUT/'catalog.json',{n:{'view':v,'methods':ms,'video':n+'.mp4','poster':n+'.jpg'} for n,(v,ms) in SPECS.items()})
 # Separate chart, absent from videos. Gaps stay gaps.
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,ax=plt.subplots(figsize=(12,4))
 for m in METHODS:
  vals=[MATCH.get((m,f),{}).get('center_error',np.nan) for f in IDS];ax.plot(range(199),vals,label=METHODS[m],lw=1.4)
 ax.set(xlabel='Source image ID (not time)',ylabel='3D center error (m)',title='Lower is better; gaps = unmatched');ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(OUT/'center_error.png',dpi=150);plt.close(fig)
 # Include three independent visual audit frames.
 for f in ['000000','000110','000170']:cv2.imwrite(str(OUT/f'projection_audit_{f}.jpg'),render(f,'bev',['A','F']))
 files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.suffix in ['.mp4','.jpg','.csv','.png','.json'] and p.name not in ['manifest.json','validation.json']}
 savej(OUT/'manifest.json',{'sha256':files,'source':'controlled_20261116','dataset':str(DATA),'playback':'199 image IDs resampled to 300 frames / 10s; not inference FPS','projection':'KITTI (x,y,z) -> CARLA (z,x,-y) -> inverse front extrinsics -> top extrinsics -> optical (y,-z,x); common GT bottom plane','metric':'BEV IoU in metric XZ, not image pixel IoU','synchronization':'paired by image ID; duplicate metadata timestamps retained'})
if __name__=='__main__':main()
