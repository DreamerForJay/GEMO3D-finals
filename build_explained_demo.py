"""Standalone, Chinese annotated videos from immutable controlled predictions.
Only yaw_geometry uses an explicitly synthetic yaw intervention; never called inference.
"""
from pathlib import Path
import csv,json,math,hashlib,subprocess,functools
import numpy as np,cv2,imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from render_sequence_video import draw_box,corners
from evaluate_controlled_suite import bev_iou
from build_demo_assets import DATA,GT,PS,PREDS,ROWS,stats,IDS
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results/explained_demo';OUT.mkdir(exist_ok=True)
BLUE=(63,166,255);ORANGE=(255,169,66);WHITE=(235,243,251);MUTED=(169,192,214);BG=(13,23,38)
@functools.lru_cache()
def font(n):return ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def txt(im,xy,t,n=27,c=WHITE):ImageDraw.Draw(im).text(xy,t,font=font(n),fill=c)
def canvas():return Image.new('RGB',(1920,1080),BG)
def js(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def csvout(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def match(m,f):return next((r for r in ROWS if r['method']==m and r['frame']==f),None)
def angle(o):return math.degrees(o['ry'])
def num(v,unit='m'):return '未配對，不計誤差' if v is None else f'{v:.3f} {unit}'
def annotated(f,m,w=1242,h=375):
 a=cv2.imread(str(DATA/'image_2'/f'{f}.png'));pred=PREDS[m][f]
 for o in GT[f]:draw_box(a,o,PS[f],ORANGE[::-1],True)
 for o in pred:draw_box(a,o,PS[f],BLUE[::-1])
 im=Image.fromarray(cv2.cvtColor(a,cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(im)
 for j,(objects,col,label,x) in enumerate([(GT[f],ORANGE,'真值 GT',15),(pred,BLUE,'預測',650)]):
  for i,o in enumerate(objects):
   y=15+i*66;t=f'{label}  Z={o["z"]:.2f}m   朝向={angle(o):.1f}°';bb=d.textbbox((x,y),t,font=font(23));d.rectangle((bb[0]-5,bb[1]-4,bb[2]+5,bb[3]+5),fill=BG);txt(im,(x,y),t,23,col)
   b=o['box'];anchor=((b[0]+b[2])/2,b[1]);d.line((x+100,y+39,*anchor),fill=col,width=2)
 if not pred:txt(im,(650,15),'沒有預測框（漏檢）',24,BLUE)
 return im.resize((w,h))
def bev(f,m,width=570,height=570):
 im=Image.new('RGB',(width,height),(20,34,52));d=ImageDraw.Draw(im);s=11;cx=width/2;bottom=height-40
 for z in range(0,41,5):
  y=bottom-z*s;d.line((15,y,width-15,y),fill=(54,72,94));txt(im,(15,y-26),f'{z}m',19,MUTED)
 for arr,col,dash in [(GT[f],ORANGE,True),(PREDS[m][f],BLUE,False)]:
  for o in arr:
   pts=[(cx+x*s,bottom-z*s) for x,z in corners(o)[[0,2],:4].T]
   for p,q in zip(pts,pts[1:]+pts[:1]):
    for k in range(0,10,2) if dash else [0]:
     l=k/10 if dash else 0;r=(k+1)/10 if dash else 1;d.line((p[0]+(q[0]-p[0])*l,p[1]+(q[1]-p[1])*l,p[0]+(q[0]-p[0])*r,p[1]+(q[1]-p[1])*r),fill=col,width=3)
   x,z=o['x'],o['z'];p=(cx+x*s,bottom-z*s);q=(p[0]+math.cos(o['ry'])*25,p[1]+math.sin(o['ry'])*25);d.line((*p,*q),fill=col,width=4)
 txt(im,(80,8),'鳥瞰 BEV：由上往下看',25);txt(im,(25,height-32),'線段：車輛縱向軸；上方較遠',20,MUTED);return im

def plot(im,ids,m,ix,key='depth_error',y=790,title=None):
 vals=[abs(match(m,f)[key]) if match(m,f) else None for f in ids];mx=5.0 if key=='depth_error' else max([v for v in vals if v is not None]+[.1])*1.15;d=ImageDraw.Draw(im);x0,x1,top,bottom=120,1830,y+65,1010
 txt(im,(40,y),title or '下圖＝每一張影像的深度誤差；越低越好，0 表示距離預測正確',27)
 for j in range(4):
  yy=bottom-j*(bottom-top)/3;d.line((x0,yy,x1,yy),fill=(54,72,94));txt(im,(38,yy-17),f'{mx*j/3:.1f}',20,MUTED)
 last=None
 for j,v in enumerate(vals):
  p=(x0+j*(x1-x0)/max(1,len(ids)-1),bottom-v/mx*(bottom-top)) if v is not None else None
  if p and last:d.line((*last,*p),fill=BLUE,width=3)
  last=p
 x=x0+ix*(x1-x0)/max(1,len(ids)-1);d.line((x,top-4,x,bottom),fill=WHITE,width=2);txt(im,(max(130,min(x+8,1500)),top-34),'白線＝目前這一幀',20)
 txt(im,(120,1022),f'橫軸：來源影格 {ids[0]} → {ids[-1]}（不是推論秒數）',22);txt(im,(1230,1022),'縱軸：公尺 m；斷線＝未配對',22)

def base(m,f,ix,ids,title,subtitle):
 im=canvas();txt(im,(35,15),title,39);txt(im,(35,72),subtitle,25,MUTED)
 txt(im,(35,112),'藍色實線＝本方法預測 3D 框',28,BLUE);txt(im,(690,112),'橘色虛線＝資料集真值 3D 框',28,ORANGE)
 im.paste(annotated(f,m),(35,160));im.paste(bev(f,m),(1315,165));r=match(m,f)
 txt(im,(35,555),f'影格 {f}   深度 Z＝相機前向距離，不是斜線距離',28)
 txt(im,(35,610),'目前深度誤差 |預測 Z − 真值 Z|：'+num(abs(r['depth_error']) if r else None),30,BLUE)
 txt(im,(35,660),'3D 中心誤差：'+num(r['center_error'] if r else None)+'   （位置偏差）',28)
 txt(im,(35,710),'朝向角誤差：'+num(r['yaw_error_deg'] if r else None,'°')+'   （旋轉偏差）',28)
 plot(im,ids,m,ix);return im

def endcard(title,summary):
 im=canvas();txt(im,(70,80),title+'｜整段數據',40)
 for i,s in enumerate(summary):
  y=190+i*220;txt(im,(70,y),s['method'],30,BLUE);txt(im,(70,y+50),f"深度 RMSE {s['depth_rmse_m']:.3f}m    平均絕對誤差 {s['depth_mae_m']:.3f}m",31);txt(im,(70,y+100),f"配對 {s['matches']} ／ GT {s['gt']}    漏檢 {s['unmatched_gt']}    未配對預測 {s['unmatched_predictions']}",28)
 txt(im,(70,840),'只對已配對物件計算誤差；漏檢另外列出，不當作零誤差。',28)
 txt(im,(70,900),'影片是離線重繪，30fps 播放速度不代表推論效能。',28)
 return im

def encode(name,ids,render,card,seconds=16):
 path=OUT/(name+'.mp4');p=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-preset','veryfast','-threads','3','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE);mapping=[];prev=-1
 for j in range(seconds*30):
  ix=int(j*(len(ids)-1)/(seconds*30-1))
  if ix!=prev:buf=render(ids[ix],ix).tobytes();prev=ix
  p.stdin.write(buf);mapping.append(dict(output_frame=j,source_frame=ids[ix],phase='data'))
 for j in range(60):p.stdin.write(card.tobytes());mapping.append(dict(output_frame=seconds*30+j,source_frame='',phase='summary'))
 p.stdin.close();assert p.wait()==0;assert path.stat().st_size<25_000_000;csvout(OUT/(name+'_mapping.csv'),mapping);render(ids[0],0).save(OUT/(name+'_poster.jpg'),quality=94);print('DONE',name,flush=True)

def export(name,methods,ids,notes):
 sums=[stats(m,ids) for m in methods];rows=[]
 for m in methods:
  for f in ids:
   r=match(m,f);pred=PREDS[m][f];g=GT[f][0]
   rows.append(dict(method=m,frame=f,predictions=len(pred),gt=len(GT[f]),matched=r is not None,gt_z=g['z'],pred_z=pred[0]['z'] if pred else '',gt_ry_deg=angle(g),pred_ry_deg=angle(pred[0]) if pred else '',depth_error=r['depth_error'] if r else '',center_error=r['center_error'] if r else '',yaw_error_deg=r['yaw_error_deg'] if r else '',bev_iou=r['bev_iou'] if r else ''))
 csvout(OUT/(name+'_per_frame.csv'),rows);js(OUT/(name+'_summary.json'),dict(methods=sums,frames=ids,notes=notes,source='results/controlled_20261116',matching='class-aware IoU >= .5; unmatched errors left blank',capture='Metadata has repeated timestamps/frame IDs; offline image-ID order, not verified strict sensor timing.'));return sums

def main():
 configs=[('full_only','F','Full 完整流程（F）','Rank-1 補償＋道路約束＋回授＋tightfit；這支只畫 Full'),('pinhole_only','A','未補償（A）','只用針孔深度；沒有 Rank-1、道路約束、回授與 tightfit'),('rank1_only','D','僅 Rank-1 補償（D）','針孔深度＋Rank-1；沒有道路約束、回授與 tightfit'),('no_tightfit_only','F_no_tightfit','停用 tightfit 的流程','保留道路約束與回授；供檢查 tightfit 是否真的改善3D')]
 for name,m,title,subtitle in configs:
  sums=export(name,[m],IDS,subtitle);encode(name,IDS,lambda f,ix:base(m,f,ix,IDS,title,subtitle),endcard(title,sums))
 # Actual recorded failure segment, selected to explain failure, not to estimate overall accuracy.
 ids=IDS[:31];sums=export('tightfit_failure',['F_no_tightfit','F'],ids,'Failure-focused first 31 frames; not a representative performance estimate. Matched A/B pipeline outputs, not evidence that yaw causes these changes.')
 trows={r['frame']:r for r in csv.DictReader((ROOT/'results/tightfit_ablation.csv').open())}
 def failure(f,ix):
  im=base('F',f,ix,ids,'實際失敗案例：2D 更貼框，不保證 3D 更準','畫面只顯示 Full 的框；右下數字對照同幀停用 tightfit 的結果')
  ImageDraw.Draw(im).rectangle((1300,555,1910,752),fill=BG);r=trows.get(f)
  if r:
   txt(im,(1325,564),'3D 中心誤差（m）',24);txt(im,(1325,602),f"停用 {float(r['center_error_before']):.3f} → Full {float(r['center_error_after']):.3f}",27)
   txt(im,(1325,646),'投影框與2D偵測框 IoU（越高越貼）',22);txt(im,(1325,681),f"{float(r['projected_det_iou_before']):.3f} → {float(r['projected_det_iou_after']):.3f}",26)
   if r['iou_up_center_worse']=='True':txt(im,(1325,721),'本幀：2D較貼，但3D位置更差',22,ORANGE)
  else:txt(im,(1325,600),'本幀未配對，不做誤差比較',23)
  return im
 encode('tightfit_failure',ids,failure,endcard('失敗片段（不是整體排名）',sums),10)
 # Measured orientation-error sequence, no causal claim.
 ids=IDS[157:176];sums=export('yaw_observed',['F'],ids,'Observed yaw vs center error, not controlled yaw intervention or proof of causal angle conversion error.')
 def observed(f,ix):
  im=base('F',f,ix,ids,'實測：朝向角誤差與位置誤差是兩件事','只顯示 Full；這段不是受控轉彎實驗，不能把共同變化當成因果')
  ImageDraw.Draw(im).rectangle((0,780,1920,1080),fill=BG)
  # degree plot gets an explicit degree axis; never reuse meter labels.
  plot(im,ids,'F',ix,'yaw_error_deg',title='下圖＝預測朝向與真值朝向之最短角差；越低越好')
  ImageDraw.Draw(im).rectangle((1220,1018,1920,1080),fill=BG);txt(im,(1230,1022),'縱軸：角度 °；不是公尺',22,ORANGE)
  return im
 encode('yaw_observed',ids,observed,endcard('朝向觀察片段（非因果實驗）',sums),10)
 # Geometry-only intervention: GT center/dimensions fixed; yaw changed artificially.
 f='000110';g=GT[f][0];offsets=np.linspace(-30,30,121);sim=[]
 for off in offsets:
  p=dict(g,ry=g['ry']+math.radians(float(off)));corner=float(np.sqrt(np.mean(np.sum((corners(p)-corners(g))**2,axis=0))))
  sim.append(dict(sample=len(sim),source_frame=f,injected_yaw_error_deg=float(abs(off)),signed_yaw_offset_deg=float(off),center_error_m=0.,corner_rms_displacement_m=corner,bev_iou=bev_iou(p,g),kind='synthetic_geometry_not_inference'))
 csvout(OUT/'yaw_geometry_per_frame.csv',sim)
 def geometry(_,ix):
  p=dict(g,ry=g['ry']+math.radians(float(offsets[ix])));a=cv2.imread(str(DATA/'image_2'/f'{f}.png'));draw_box(a,g,PS[f],ORANGE[::-1],True);draw_box(a,p,PS[f],BLUE[::-1]);im=canvas();txt(im,(35,20),'幾何示意：位置固定，只把朝向角旋轉',40);txt(im,(35,80),'人工改角度，不是模型推論，也不是實際轉彎拍攝',29,ORANGE)
  txt(im,(35,135),'橘虛線＝原始 GT 框；藍實線＝人工旋轉後的框',28);im.paste(Image.fromarray(cv2.cvtColor(a,cv2.COLOR_BGR2RGB)),(35,205))
  temp='synthetic';PREDS[temp]={f:[p]};im.paste(bev(f,temp),(1315,180));r=sim[ix]
  txt(im,(35,625),f"人工角度偏移 {offsets[ix]:+.1f}°     中心位置誤差始終 = 0.000m",34)
  txt(im,(35,690),f"角點位移 RMS = {r['corner_rms_displacement_m']:.3f}m     BEV IoU = {r['bev_iou']:.3f}",32,BLUE)
  txt(im,(35,800),'看框的方向與重疊：即使位置沒動，朝向錯誤也會改變3D框形狀的投影。',30)
  txt(im,(35,870),'所以「3D 中心誤差」無法單獨衡量朝向是否正確；還要看角差與重疊。',28)
  txt(im,(35,940),'這支不量測角度如何影響深度補償；那需要固定其他條件重跑模型。',27,MUTED);return im
 card=canvas();txt(card,(65,140),'示意結論',42);txt(card,(65,270),'只旋轉朝向 → 框與角點移動、BEV重疊改變。',35);txt(card,(65,370),'固定中心 → 中心誤差仍為0，不能當作深度補償實驗。',33);txt(card,(65,520),'人工幾何示意；不代表任何模型的準確率。',33,ORANGE)
 js(OUT/'yaw_geometry_summary.json',dict(kind='synthetic_geometry_not_inference',source_frame=f,offset_range_deg=[-30,30],samples=121,center_error_m=0.,note='Fixed GT dimensions and center, change ry only; corner RMS uses corresponding corners, not model accuracy.'))
 encode('yaw_geometry',[str(i) for i in range(121)],geometry,card,10)
 mapping=list(csv.DictReader((OUT/'yaw_geometry_mapping.csv').open()))
 for row in mapping:
  row['simulation_sample']=row['source_frame']
  row['source_frame']=f if row['phase']=='data' else ''
 csvout(OUT/'yaw_geometry_mapping.csv',mapping)
 # Self-contained player; each file has a single configuration, no toggling ambiguity.
 descriptions=[(n,t,sub) for n,m,t,sub in configs]+[('tightfit_failure','實際失敗：2D改善但3D變差','取前31幀，保留未配對；不是整體評估。'),('yaw_observed','實測朝向誤差','實際Full輸出；只說明觀測，不證明角度轉換造成深度錯誤。'),('yaw_geometry','人工朝向幾何示意','固定GT位置與尺寸，只改角度；不是模型推論。')]
 html='<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GEMO3D 分開看懂</title><style>body{max-width:1200px;margin:auto;padding:24px;background:#0d1726;color:#eaf3fa;font:18px system-ui}video{width:100%}a{color:#79bdff}section{padding:25px 0;border-bottom:1px solid #40546c}</style><h1>每種流程分開看</h1><p>藍實線：該流程預測；橘虛線：GT。Z為相機前向距離；下方橫軸為來源影格，縱軸通常為絕對深度誤差m，朝向專片則明標°；白線為現在，斷線為未配對。</p>'
 for name,title,sub in descriptions:html+=f'<section><h2>{title}</h2><p>{sub}</p><video controls preload="none" poster="{name}_poster.jpg" src="{name}.mp4"></video><p><a href="{name}_per_frame.csv">逐幀CSV</a> · <a href="{name}_summary.json">數據與範圍</a></p></section>'
 (OUT/'index.html').write_text(html+'</html>')
 (OUT/'README.md').write_text('# 分開看懂的 Demo\n\nFull（F）、未補償（A）、純Rank-1（D）、停用tightfit分開各18秒，使用相同199個來源影格、相同0–40m BEV及0–5m深度誤差尺度（程式固定上限見來源）。其餘三片各12秒：實際tightfit失敗、實際朝向誤差觀察、人工yaw幾何示意。\n\n藍色實線是該流程的預測3D框；橘色虛線是真值；框旁標Z與相機座標朝向ry（度）。Z是前向距離，不是歐氏距離。曲線橫軸來源影格，白線現在，縱軸絕對深度誤差m（yaw_observed則為角度°），斷線是未配對，不是零。\n\n人工yaw_geometry是固定GT尺寸與位置、只改ry的幾何示意；藍框在此片代表人工旋轉，不是推論。不能用它宣稱角度轉換造成模型深度誤差。已查找Desktop、Videos、Downloads、mono3d_predictions等，尚未找到可核實的實際轉角影片及對應推論／GT組合。\n\n來源results/controlled_20261116及results/tightfit_ablation.csv；不重跑推論、不修改原實驗。Full是F完整管線，不是full矩陣補償變體。既有相機時間異常與尺寸映射限制仍適用。\n\n重建：python build_explained_demo.py。\n')
 files={str(p.relative_to(OUT)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ['manifest.json','validation.json']};js(OUT/'manifest.json',dict(files=files,source_commit='32be75c',generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
if __name__=='__main__':main()
