"""Reproducible derived demo assets; no inference, filtering by error, or simulated measurements.
Run: python build_demo_assets.py [--assets G-A1,G-B1,...] [--no-video]
"""
from pathlib import Path
import argparse,csv,json,hashlib,subprocess,shutil,math
import numpy as np
import cv2
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
from render_sequence_video import objs,corners,draw_box
from evaluate_controlled_suite import evaluate
ROOT=Path(__file__).resolve().parent
DATA=Path('/home/e114/KITTI_ROOT/sed_lincoln_fr_T1R8/data/KITTIDataset_Carla/training')
OUT=ROOT/'results/demo'
IDS=[f'{i:06d}' for i in range(199)]
PREDS=json.loads((ROOT/'results/controlled_20261116/predictions.json').read_text())
ROWS=list(csv.DictReader((ROOT/'results/controlled_20261116/pairs.csv').open()))
for r in ROWS:
 for k in r:
  if k not in ('method','frame'):r[k]=float(r[k])
GT={f:[g for g in objs(str(DATA/'label_2'/f'{f}.txt')) if g['t']=='Car'] for f in IDS}
PS={f:np.array([float(v) for l in (DATA/'calib'/f'{f}.txt').read_text().splitlines() if l.startswith('P2:') for v in l.split()[1:]]).reshape(3,4) for f in IDS}
META={m:{(r['image_id'],int(r['pred_id'])):r for r in csv.DictReader((ROOT/f'benchmark_output/controlled_20261116/{m}/pred_meta.csv').open(encoding='utf-8-sig'))} for m in ['A','D','F']}
BLUE=(57,148,255); ORANGE=(255,158,57);WHITE=(232,240,248);BG=(13,23,38)
LABEL={'A':'Pinhole A (no correction)','D':'Rank-1 D (no ground/tightfit)','F':'GEMO3D full F','historical_monodetr':'MonoDETR (2023)','historical_monodgp':'MonoDGP (2025)','historical_monoamnet':'MonoAMNet (2025)','timing':'GEMO3D timed run'}
COLORS=[BLUE,(100,218,171),(245,119,176),(229,192,83)]
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n):return ImageFont.truetype(FONT,n)
def text(im,xy,s,n=24,c=WHITE):ImageDraw.Draw(im).text(xy,str(s),font=font(n),fill=c)
def savej(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def csvout(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def bg():return Image.new('RGB',(1920,1080),BG)
def frame_rows(m,f):return [r for r in ROWS if r['method']==m and r['frame']==f]
def fmt(v):return 'unmatched' if v is None else f'{v:.3f}'
def frame_err(m,f,key='depth_error'):
 r=frame_rows(m,f);return float(np.mean([abs(x[key]) for x in r])) if r else None
def front(f,m,w,h,raw=False):
 a=cv2.imread(str(DATA/'image_2'/f'{f}.png'));assert a is not None
 if not raw:
  for g in GT[f]:draw_box(a,g,PS[f],ORANGE[::-1],True)
  for p in PREDS[m][f]:draw_box(a,p,PS[f],BLUE[::-1])
 im=Image.fromarray(cv2.cvtColor(a,cv2.COLOR_BGR2RGB));im.thumbnail((w,h));panel=Image.new('RGB',(w,h),BG);panel.paste(im,((w-im.width)//2,(h-im.height)//2));return panel

def bev(f,m,w,h):
 im=Image.new('RGB',(w,h),(20,34,52));d=ImageDraw.Draw(im)
 # Fixed physical axes across every method. Out-of-range predictions stay in JSON/counts.
 scale=min((h-70)/40,(w-80)/24); cx=w/2; bottom=h-35
 for z in range(0,41,5):
  y=bottom-z*scale;d.line((15,y,w-15,y),fill=(56,73,91));text(im,(5,y-20),f'{z}m',16)
 for x in range(-10,11,5):d.line((cx+x*scale,30,cx+x*scale,bottom),fill=(56,73,91))
 for items,col,dashed in [(GT[f],ORANGE,True),(PREDS[m][f],BLUE,False)]:
  for o in items:
   pts=[(cx+x*scale,bottom-z*scale) for x,z in corners(o)[[0,2],:4].T]
   for a,b in zip(pts,pts[1:]+pts[:1]):
    for k in range(0,10,2) if dashed else [0]:
     lo=k/10 if dashed else 0;hi=(k+1)/10 if dashed else 1
     d.line((a[0]+(b[0]-a[0])*lo,a[1]+(b[1]-a[1])*lo,a[0]+(b[0]-a[0])*hi,a[1]+(b[1]-a[1])*hi),fill=col,width=3)
 text(im,(20,8),'BEV | fixed 0-40m, x +/-12m',18);return im

def chart(methods,ids,key='depth_error',height=260):
 im=Image.new('RGB',(1840,height),(20,34,52));d=ImageDraw.Draw(im)
 vals=[[frame_err(m,f,key) for f in ids] for m in methods];maximum=max([v for a in vals for v in a if v is not None]+[1])*1.08
 x0,x1,y0,y1=85,1810,60,height-35
 for i in range(4):
  y=y1-(y1-y0)*i/3;d.line((x0,y,x1,y),fill=(62,76,92));text(im,(5,y-12),f'{maximum*i/3:.1f}',17)
 for mi,a in enumerate(vals):
  prev=None
  for j,v in enumerate(a):
   p=(x0+j*(x1-x0)/(len(ids)-1),y1-v/maximum*(y1-y0)) if v is not None else None
   if p is not None and prev is not None:d.line((*prev,*p),fill=COLORS[mi],width=3)
   prev=p
  text(im,(100+mi*430,6),LABEL[methods[mi]],19,COLORS[mi])
 text(im,(85,height-28),f'Frame {ids[0]}',16);text(im,(1650,height-28),ids[-1],16)
 return im,(x0,x1,y0,y1)

def stats(m,ids):
 rows=[r for r in ROWS if r['method']==m and r['frame'] in ids];d=np.array([r['depth_error'] for r in rows]);c=np.array([r['center_error'] for r in rows]);ng=sum(len(GT[f]) for f in ids);npred=sum(len(PREDS[m][f]) for f in ids)
 return dict(method=m,frames=len(ids),predictions=npred,gt=ng,matches=len(rows),unmatched_predictions=npred-len(rows),unmatched_gt=ng-len(rows),depth_rmse_m=float(np.sqrt(np.mean(d*d))) if len(d) else None,depth_mae_m=float(np.mean(abs(d))) if len(d) else None,center_rmse_m=float(np.sqrt(np.mean(c*c))) if len(c) else None,center_mean_m=float(np.mean(c)) if len(c) else None,gt_depth_range_m=[min(g['z'] for f in ids for g in GT[f]),max(g['z'] for f in ids for g in GT[f])])

def export_data(folder,methods,ids,limit):
 folder.mkdir(parents=True,exist_ok=True)
 # One row per prediction (matched/unmatched), and one for each missed GT. Null is never zero error.
 rows=[]
 for m in methods:
  for f in ids:
   matches=frame_rows(m,f);used=set()
   for pi,p in enumerate(PREDS[m][f]):
    r=next((r for r in matches if int(r['pred_id'])==pi),None)
    if r:used.add(int(r['gt_id']))
    rows.append(dict(method=m,frame=f,pred_id=pi,gt_id=int(r['gt_id']) if r else '',status='matched' if r else 'unmatched_prediction',gt_z=r['gt_z'] if r else '',pred_z=p['z'],depth_error=r['depth_error'] if r else '',center_error=r['center_error'] if r else ''))
   for gi,g in enumerate(GT[f]):
    if gi not in used:rows.append(dict(method=m,frame=f,pred_id='',gt_id=gi,status='missed_gt',gt_z=g['z'],pred_z='',depth_error='',center_error=''))
 csvout(folder/'per_frame.csv',rows)
 summary=dict(asset=folder.name,methods=[stats(m,ids) for m in methods],limitations=limit,matching='class-aware greedy one-to-one detection bbox IoU >= 0.5; no error filtering',playback='Offline resampled playback, 30 fps; 16s data + 2s summary. Short: same source frames over 10s + 2s summary. Not inference/capture FPS.',dataset=str(DATA),source_frames=ids,source_results='results/controlled_20261116',source_commit='dca5aa6',effective_dimensions_hwl_m=[1.52,1.64,3.86],pinhole_height_m=1.511)
 savej(folder/'summary.json',summary)
 savej(folder/'geometry.json',dict(calibration={f:PS[f].tolist() for f in ids},gt={f:GT[f] for f in ids},predictions={m:{f:PREDS[m][f] for f in ids} for m in methods}))
 (folder/'README.md').write_text(f'# {folder.name}\n\n'+limit+'\n\nSource: `results/controlled_20261116` (2026-11-16 inference; source/weights/command hashes in its manifest). '+str(DATA)+'\n\nRebuild: `python build_demo_assets.py --assets '+folder.name+'`\n\nBlue: predictions; dashed orange: GT. Fixed BEV limits; out-of-view boxes remain in geometry.json and prediction counts. Empty errors mean unmatched, never zero. Per-frame CSV includes all predictions and missed GT. Metrics use matched objects, not all GT; report misses alongside them. Video cursor uses frame_mapping.csv. 30 fps is offline playback. Short version includes all frames with faster playback. No new model inference.\n')
 return summary

def card(summary):
 im=bg();text(im,(80,80),summary['asset']+' | measured sequence summary',44)
 for i,s in enumerate(summary['methods']):
  y=200+i*145;text(im,(80,y),LABEL[s['method']],30,COLORS[i]);text(im,(80,y+44),f"Depth RMSE {s['depth_rmse_m']:.3f}m | MAE {s['depth_mae_m']:.3f}m | Center mean {s['center_mean_m']:.3f}m",26)
  text(im,(80,y+82),f"Matches {s['matches']} | missed GT {s['unmatched_gt']} | unmatched predictions {s['unmatched_predictions']}",24)
 text(im,(80,870),'Same source frames in full / short editions; metrics from matched objects.',25)
 text(im,(80,920),'Offline playback; 30 fps does not measure system throughput.',25)
 if summary['asset']=='G-E1':text(im,(80,980),'Historical baseline settings unverified. NOT a fair leaderboard.',28,ORANGE)
 return im

def video(folder,render,summary,name='video',keyframes=True):
 ids=summary['source_frames'];end=card(summary);mapping=[]
 for short,seconds in [(False,16),(True,10)]:
  dest=folder/(name+('_short' if short else '')+'.mp4')
  cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-preset','veryfast','-threads','3','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE);prev=-1;buf=None
  try:
   for j in range(seconds*30):
    ix=min(len(ids)-1,int(j*(len(ids)-1)/(seconds*30-1)))
    if ix!=prev:buf=render(ids[ix],ix).tobytes();prev=ix
    p.stdin.write(buf);mapping.append(dict(video=dest.name,output_frame=j,source_frame=ids[ix],phase='data'))
   raw=end.tobytes()
   for j in range(60):p.stdin.write(raw);mapping.append(dict(video=dest.name,output_frame=seconds*30+j,source_frame='',phase='summary'))
  finally:p.stdin.close()
  if p.wait()!=0:raise RuntimeError(dest)
  assert dest.stat().st_size<=25_000_000
 if keyframes:
  (folder/'keyframes').mkdir(exist_ok=True)
  render(ids[0],0).save(folder/'poster.jpg',quality=93)
  for ix in np.linspace(0,len(ids)-1,4).astype(int):render(ids[ix],int(ix)).resize((1600,900)).save(folder/'keyframes'/f'{ids[ix]}.png')
 csvout(folder/(name+'_frame_mapping.csv'),mapping)

def run_standard(code,methods,limit,mode='single',ids=None,no_video=False):
 ids=ids or IDS;folder=OUT/code;s=export_data(folder,methods,ids,limit);key='center_error' if mode.startswith('compare') else 'depth_error';curve,axes=chart(methods,ids,key)
 def render(f,ix):
  im=bg();text(im,(40,20),f'{code} | {f} | offline playback',34)
  text(im,(40,67),'Blue: prediction | dashed orange: GT | errors use IoU >= 0.5 matches',22)
  if mode.startswith('compare'):
   text(im,(40,102),'AUDIT PREVIEW: historical baseline settings unverified; not a fair leaderboard.',24,ORANGE)
   for j,m in enumerate(methods):
    x=40+(j%2)*940;y=146+(j//2)*285
    pane=bev(f,m,900,220) if mode=='compare_bev' else front(f,m,900,220)
    im.paste(pane,(x,y+35));text(im,(x,y),LABEL[m]+f' | center {fmt(frame_err(m,f,key))}m',22,COLORS[j])
    if m=='F':ImageDraw.Draw(im).rectangle((x-8,y-5,x+908,y+260),outline=BLUE,width=3)
  elif mode=='pair':
   for j,m in enumerate(methods):
    x=40+j*940;text(im,(x,115),LABEL[m],27,COLORS[j]);im.paste(front(f,m,900,300),(x,158));im.paste(bev(f,m,450,270),(x+450,460));text(im,(x,495),'Depth error (abs)',25);text(im,(x,540),fmt(frame_err(m,f))+' m',35)
  else:
   m=methods[0];im.paste(front(f,m,1240,480),(40,170));im.paste(bev(f,m,550,580),(1330,130));text(im,(40,115),LABEL[m]+f' | absolute depth error {fmt(frame_err(m,f))} m',30)
   text(im,(40,666),f'Predictions {len(PREDS[m][f])} | GT {len(GT[f])} | matches {len(frame_rows(m,f))}',24)
   if m=='timing':text(im,(40,710),f'{TIMES[f]["total_ms"]:.3f} ms | RTX 3060 SHARED | mean 11.206 fps',27,ORANGE)
  im.paste(curve,(40,790));d=ImageDraw.Draw(im);x=40+axes[0]+ix*(axes[1]-axes[0])/(len(ids)-1);d.line((x,850,x,1015),fill=WHITE,width=2)
  text(im,(40,753),('Center error' if key=='center_error' else 'Absolute depth error')+' (m); gaps = unmatched',22)
  return im
 if not no_video:video(folder,render,s,name='bev' if mode=='compare_bev' else 'video',keyframes=mode!='compare_bev')
 return folder,s,render

TIMES={}
def main():
 global ROWS,PREDS,TIMES
 ap=argparse.ArgumentParser();ap.add_argument('--assets',default='G-A1,G-B1,G-C1,G-E1,G-F1,G-I1,G-M1,G-K1');ap.add_argument('--no-video',action='store_true');a=ap.parse_args();selected=a.assets.split(',');OUT.mkdir(exist_ok=True)
 for code in selected:
  print('BUILD',code,flush=True)
  if code=='G-A1':run_standard(code,['F'],'New controlled full-F outputs, not the older historical demo. Known dimension-map override; not a paper reproduction.',no_video=a.no_video)
  elif code=='G-F1':
   folder,s,render=run_standard(code,['A','D'],'Paired A vs D: only Rank-1 correction changes; both ground and tightfit disabled. D is NOT the full system. Six frames chosen by fixed IDs, not by improvement.',mode='pair',no_video=a.no_video)
   pairs=[]
   for f in ['000043','000070','000100','000130','000150','000170']:
    for m,side in [('A','before'),('D','after')]:
     im=Image.new('RGB',(1600,900),BG);im.paste(front(f,m,1040,600),(0,95));im.paste(bev(f,m,560,600),(1040,95));text(im,(25,25),LABEL[m]+' | frame '+f,30);text(im,(25,745),'Absolute depth error '+fmt(frame_err(m,f))+' m',32);im.save(folder/f'{f}_{side}.png')
    pairs.append(dict(frame=f,before=f'{f}_before.png',after=f'{f}_after.png',before_depth_error_m=frame_err('A',f),after_depth_error_m=frame_err('D',f)))
   savej(folder/'slider_pairs.json',pairs)
  elif code=='G-E1':
   ms=['historical_monodetr','historical_monodgp','historical_monoamnet','F'];limit='AUDIT PREVIEW ONLY: baselines use historical predictions on this dataset, but checkpoint/threshold/original commands are unverified. Own matched subsets differ; not a fair leaderboard or verified 165-sample comparison.'
   run_standard(code,ms,limit,'compare',no_video=a.no_video);run_standard(code,ms,limit,'compare_bev',no_video=a.no_video)
  elif code=='G-C1':
   folder=OUT/code;ids=['000043','000110','000170'];export_data(folder,['F'],ids,'Near/mid/far front-camera examples only; oblique-view coverage remains missing. Vehicle type is FORCED sedan, not a measured classifier decision. Intermediate values are full-F pred_meta from the SAME run; final Z includes tightfit and can differ from Z_corr. Core architecture diagram task C remains skipped.')
   steps=[]
   for f in ids:
    pi=0;r=META['F'][(f,pi)];z=float(r['z_est']);comp=float(r['comp_final']);ratio=1-comp/z
    values=dict(frame=f,pred_id=pi,gt_z_m=GT[f][0]['z'],bbox=[float(r[k]) for k in ['x1','y1','x2','y2']],vehicle_type=r['veh_type'],vehicle_type_source='forced sedan',model_observation_angle_deg=float(r['yaw_comp_deg_final']),z_raw_m=z,ratio=ratio,z_corr_m=z-comp,z_final_before_txt_rounding_m=float(r['pred_z']),z_final_txt_m=PREDS['F'][f][pi]['z'],dimensions_hwl=[float(r[k]) for k in ['pred_h','pred_w','pred_l']],note='ratio = 1-comp_final/z_est; comp_final is meters. z_corr=z_est-comp_final; final includes refinement. No classifier accuracy claim.')
    steps.append(values);sub=folder/f;sub.mkdir(exist_ok=True)
    captions=['Original input','YOLO11 detection',f'FORCED sedan | angle {values["model_observation_angle_deg"]:.3f} deg',f'Z_raw = {z:.4f} m',f'r_hat = {ratio:.6f}',f'Z_corr = {z-comp:.4f} m',f'Final Z = {values["z_final_txt_m"]:.2f} m (after refinement)']
    for i,title in enumerate(captions):
     image=cv2.imread(str(DATA/'image_2'/f'{f}.png'))
     if 1<=i<=5:
      b=[int(v) for v in values['bbox']];cv2.rectangle(image,tuple(b[:2]),tuple(b[2:]),BLUE[::-1],3)
     if i==6:
      for g in GT[f]:draw_box(image,g,PS[f],ORANGE[::-1],True)
      for p in PREDS['F'][f]:draw_box(image,p,PS[f],BLUE[::-1])
     im=Image.new('RGB',(1600,900),BG);im.paste(Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB)).resize((1600,483)),(0,180));text(im,(35,45),f'{f} | Step {i+1}: '+title,32);text(im,(35,745),'Recorded intermediate values; front-camera distance example.',27);im.save(sub/f'step_{i+1}.png')
   savej(folder/'steps.json',steps)
  elif code=='G-B1':
   folder=OUT/code;s=export_data(folder,['F'],IDS,'PARTIAL: front/top/side paired by image ID; duplicate timestamps/simulator frame IDs prevent strict temporal sync verification (capture_anomalies.json). Side orthographic audit camera is NOT third-person chase. Chase view remains unavailable; no CARLA actors or active world modified.')
   cameras={f:json.loads((DATA/'meta'/f'{f}.json').read_text()) for f in IDS}
   savej(folder/'camera_settings.json',{f:{k:cameras[f][k] for k in ['frame','timestamp','camera','top_camera','side_iou_camera','intrinsics']} for f in IDS})
   savej(folder/'capture_anomalies.json',[dict(previous=IDS[i],current=IDS[i+1],previous_simulator_frame=cameras[IDS[i]]['frame'],current_simulator_frame=cameras[IDS[i+1]]['frame'],previous_timestamp=cameras[IDS[i]]['timestamp'],current_timestamp=cameras[IDS[i+1]]['timestamp']) for i in range(198) if cameras[IDS[i]]['frame']>=cameras[IDS[i+1]]['frame'] or cameras[IDS[i]]['timestamp']>=cameras[IDS[i+1]]['timestamp']])
   csvout(folder/'sensor_frames.csv',[dict(source_frame=f,simulator_frame=cameras[f]['frame'],timestamp=cameras[f]['timestamp'],front=f'image_2/{f}.png',top=f'bev_iou/{f}.png',side=f'side_iou/{f}.png') for f in IDS])
   curve,ax=chart(['F'],IDS)
   def render(f,ix):
    im=bg();text(im,(40,20),'G-B1 | '+f+' | recorded views paired by image ID',36);text(im,(40,75),'PARTIAL: timestamp anomalies; side audit view is NOT a chase camera',28,ORANGE)
    for j,(sub,title) in enumerate([('image_2','Front | mount height 1.65m | FOV 82.48 deg'),('bev_iou','Top | height 18m | FOV 35 deg'),('side_iou','Side audit | offset -28m | FOV 10 deg')]):
     x=40+j*625;img=Image.open(DATA/sub/f'{f}.png').convert('RGB');img.thumbnail((600,530));im.paste(img,(x+(600-img.width)//2,180+(530-img.height)//2));text(im,(x,130),title,21)
    text(im,(40,725),'Mount/FOV/extrinsics per frame: camera_settings.json. Strict timing synchronization unverified.',24);im.paste(curve,(40,790));x=40+ax[0]+ix*(ax[1]-ax[0])/198;ImageDraw.Draw(im).line((x,850,x,1015),fill=WHITE,width=2);return im
   if not a.no_video:video(folder,render,s)
  elif code=='G-I1':
   folder=OUT/code;export_data(folder,['A','D','F'],IDS,'Depth-bin and recorded observation-angle data available; no new pitch-controlled experiment. This single approach sequence does not cover 0-360 degrees.')
   csvout(folder/'angle_errors.csv',[dict(method=r['method'],frame=r['frame'],pred_id=int(r['pred_id']),model_observation_angle_deg=float(META[r['method']][(r['frame'],int(r['pred_id']))]['yaw_comp_deg_final']),gt_depth_m=r['gt_z'],depth_error_m=r['depth_error']) for r in ROWS if r['method'] in ['A','D','F']])
   bins=[]
   for m in ['A','D','F']:
    for lo,hi in [(0,10),(10,20),(20,30),(30,40)]:
     d=np.array([r['depth_error'] for r in ROWS if r['method']==m and lo<=r['gt_z']<hi]);bins.append(dict(method=m,bin_min_inclusive=lo,bin_max_exclusive=hi,n=len(d),depth_rmse_m=float(np.sqrt(np.mean(d*d))) if len(d) else None,depth_mae_m=float(np.mean(abs(d))) if len(d) else None))
   csvout(folder/'depth_bins.csv',bins)
   import matplotlib;matplotlib.use('Agg')
   import matplotlib.pyplot as plt
   fig,ax=plt.subplots(figsize=(12,5))
   for m in ['A','D','F']:
    bs=[b for b in bins if b['method']==m];ax.plot([5,15,25,35],[b['depth_rmse_m'] for b in bs],marker='o',label=LABEL[m])
   ax.set(xlabel='GT depth bin center (m)',ylabel='Matched depth RMSE (m)',title='Controlled 199-frame approach | matched-only metrics; misses in CSV');ax.legend();ax.grid(alpha=.3);fig.tight_layout();fig.savefig(folder/'depth_bins.png',dpi=160);plt.close(fig)
  elif code=='G-M1':
   t=json.loads((ROOT/'results/timing_production_io.json').read_text());ts=t['settings']['production_io_fp16'];ids=[s['frame'] for s in ts['samples']];TIMES={s['frame']:s for s in ts['samples']}
   pairs,counts,hashes,preds=evaluate(ROOT/'benchmark_output/stages_production_io_20261116/production_io_fp16/pred/data',DATA,ids,'timing');ROWS+=pairs;PREDS['timing']=preds
   folder,s,_=run_standard(code,['timing'],'Actual production_io_fp16 timing and predictions from the SAME 100-frame run; RTX 3060 shared with other processes. Mean 89.241ms, 11.206fps excludes startup/warmup. Offline video playback is 30fps. No dedicated-GPU or paper-FPS claim.',ids=ids,no_video=a.no_video)
   s['source_results']='results/timing_production_io.json';s['timing_mean_ms']=ts['means_ms'];s['throughput_fps']=ts['fps'];savej(folder/'summary.json',s);savej(folder/'timing_provenance.json',dict(gpu=t['gpu'],shared_gpu=t['shared_gpu'],command=ts['command'],source_sha256=t['source_sha256'],prediction_sha256=hashes));csvout(folder/'timing.csv',ts['samples'])
   with (folder/'README.md').open('a') as fp:fp.write('\nTiming exception: source is `results/timing_production_io.json`, prediction paths/hashes and exact command in timing_provenance.json, not controlled F.\n')
  elif code=='G-K1':
   folder=OUT/code;shutil.copytree(ROOT/'results/failure_cases',folder,dirs_exist_ok=True)
  else:raise ValueError(code)
  print('DONE',code,flush=True)
 # Manifest only delivered outputs. Inputs stay local; provenance hashes are public.
 files={str(p.relative_to(OUT)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ['manifest.json','validation.json']}
 savej(OUT/'manifest.json',dict(files=files,source_revision='dca5aa6',requirements_revision='4bf3a08',generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
if __name__=='__main__':main()
