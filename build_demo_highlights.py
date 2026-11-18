"""Real 10-second contiguous excerpts plus 2s subset metric cards; fixed time window, no error selection."""
from pathlib import Path
import csv,json,subprocess
import cv2,numpy as np,imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results/demo'
def writecsv(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
for code in ['G-A1','G-B1','G-E1','G-F1','G-M1']:
 folder=OUT/code;summary=json.loads((folder/'summary.json').read_text());geometry=json.loads((folder/'geometry.json').read_text());allrows=list(csv.DictReader((folder/'per_frame.csv').open()))
 for source in sorted(folder.glob('*.mp4')):
  if '_short' in source.stem:continue
  mapping=[r for r in csv.DictReader((folder/(source.stem+'_frame_mapping.csv')).open()) if r['video']==source.name][90:390]
  ids=list(dict.fromkeys(r['source_frame'] for r in mapping));rows=[r for r in allrows if r['frame'] in ids];methods=[]
  for old in summary['methods']:
   m=old['method'];mr=[r for r in rows if r['method']==m];matched=[r for r in mr if r['status']=='matched'];d=np.array([float(r['depth_error']) for r in matched]);c=np.array([float(r['center_error']) for r in matched]);gt=[g['z'] for f in ids for g in geometry['gt'][f]]
   methods.append(dict(method=m,frames=len(ids),matches=len(matched),unmatched_gt=sum(r['status']=='missed_gt' for r in mr),unmatched_predictions=sum(r['status']=='unmatched_prediction' for r in mr),depth_rmse_m=float(np.sqrt(np.mean(d*d))),depth_mae_m=float(np.mean(abs(d))),center_mean_m=float(c.mean()),gt_depth_range_m=[min(gt),max(gt)]))
  base=source.stem+'_highlight';s=dict(summary,methods=methods,source_frames=ids,excerpt={'source':source.name,'source_start_seconds':3,'source_end_exclusive_seconds':13,'selection':'Fixed 3–13s window for every video; not selected by error','data_output_frames':300,'summary_output_frames':60},playback='10 seconds copied from full offline video timeline, followed by 2-second recomputed excerpt metric card. Not measured capture/inference FPS.')
  (folder/(base+'_summary.json')).write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n');writecsv(folder/(base+'_per_frame.csv'),rows)
  dest=folder/(base+'_short.mp4');outmap=[dict(video=dest.name,output_frame=i,source_frame=r['source_frame'],phase='data') for i,r in enumerate(mapping)]+[dict(video=dest.name,output_frame=i,source_frame='',phase='summary') for i in range(300,360)];writecsv(folder/(base+'_frame_mapping.csv'),outmap)
  card=Image.new('RGB',(1920,1080),'#0d1726');d=ImageDraw.Draw(card);font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
  d.text((60,50),code+' | excerpt summary (source 3-13 seconds)',font=font(38),fill='white');d.text((60,115),f'Frames {ids[0]} - {ids[-1]} | {len(ids)} unique source frames',font=font(28),fill='white')
  for i,m in enumerate(methods):
   y=210+i*145;d.text((60,y),m['method'],font=font(29),fill='#3994ff');d.text((60,y+42),f"Depth RMSE {m['depth_rmse_m']:.3f}m | MAE {m['depth_mae_m']:.3f}m | center mean {m['center_mean_m']:.3f}m",font=font(27),fill='white');d.text((60,y+80),f"Matches {m['matches']} | missed GT {m['unmatched_gt']} | unmatched predictions {m['unmatched_predictions']}",font=font(25),fill='white')
  d.text((60,875),'Matched-only excerpt statistics; 30fps is offline playback.',font=font(27),fill='white')
  if code=='G-E1':d.text((60,940),'Historical baselines unverified. NOT a fair leaderboard.',font=font(28),fill='#ff9e39')
  command=[imageio_ffmpeg.get_ffmpeg_exe(),'-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-preset','veryfast','-threads','3','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
  proc=subprocess.Popen(command,stdin=subprocess.PIPE);cap=cv2.VideoCapture(str(source));cap.set(cv2.CAP_PROP_POS_FRAMES,90)
  for i in range(300):
   ok,im=cap.read();assert ok;proc.stdin.write(cv2.cvtColor(im,cv2.COLOR_BGR2RGB).tobytes())
  for i in range(60):proc.stdin.write(card.tobytes())
  cap.release();proc.stdin.close();assert proc.wait()==0;assert dest.stat().st_size<=25_000_000;print('HIGHLIGHT',dest.name,ids[0],ids[-1],flush=True)
