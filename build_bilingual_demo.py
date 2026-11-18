"""Large bilingual metrics and explicit controlled cuboid yaw mechanism (not inference)."""
import json,math,subprocess,hashlib,functools
from pathlib import Path
import numpy as np,cv2,imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
import build_clean_demo as b
OUT=b.ROOT/'results/bilingual_demo';OUT.mkdir(exist_ok=True)
BG=(16,23,29);WHITE=(241,245,249);RED=(255,106,99);GREEN=(85,224,133);YELLOW=(255,212,92);BLUE=(75,157,215)
@functools.lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def text(im,pos,s,n=30,c=WHITE):ImageDraw.Draw(im).text(pos,s,font=font(n),fill=c)
NAMES={'zh':{'A':'針孔基準','D':'Rank-1 補償','F':'完整流程','F_no_tightfit':'完整流程／停用貼合'},'en':b.METHODS}
def panel(f,m,v,lang):
 # Re-render uncompressed source overlays; replace small old header.
 a=b.panel(f,m,v)[44:];im=Image.new('RGB',(a.shape[1],a.shape[0]+142),BG)
 im.paste(Image.fromarray(cv2.cvtColor(a,cv2.COLOR_BGR2RGB)),(0,142))
 text(im,(20,8),NAMES[lang][m],30)
 r=b.MATCH.get((m,f));key='bev_iou' if v=='bev' else 'center_error'
 val=f'{r[key]:.2f}'+(' m' if v=='front' else '') if r else ('未配對' if lang=='zh' else 'Unmatched')
 label=('俯視重疊率 ↑' if v=='bev' else '3D 中心誤差 ↓') if lang=='zh' else ('BEV IoU ↑' if v=='bev' else '3D center error ↓')
 text(im,(20,73),label,26);w=ImageDraw.Draw(im).textbbox((0,0),val,font=font(54))[2];text(im,(im.width-w-20,55),val,54,YELLOW)
 return im

def compare(f,view,ms,lang):
 ims=[panel(f,m,view,lang) for m in ms];w=ims[0].width*(len(ms) if view=='bev' else 1);h=ims[0].height*(len(ms) if view=='front' else 1);out=Image.new('RGB',(w,h),BG)
 for i,im in enumerate(ims):out.paste(im,(i*im.width if view=='bev' else 0,i*im.height if view=='front' else 0))
 return out
# Pure geometry: no learned model, no CARLA captured rotation.
H,W,L,Z,FY,Y=1.511,2.128,4.902,10.,721.5377,1.65

def geometry(deg):
 o={'x':0.,'y':Y,'z':Z,'h':H,'w':W,'l':L,'ry':math.radians(deg)}
 p=b.corners(o);uv=np.column_stack([FY*p[0]/p[2],FY*p[1]/p[2]])
 top=int(np.argmin(uv[:,1]));bottom=int(np.argmax(uv[:,1]));h=float(uv[bottom,1]-uv[top,1]);ideal=FY*H/Z;raw=FY*H/h
 return p,uv,dict(yaw_deg=deg,upper_vertex=top,lower_vertex=bottom,h2d_px=h,h_ideal_px=ideal,ratio=h/ideal,z_true_m=Z,z_pinhole_m=raw,bias_m=raw-Z)

def mechanism(deg,kind,lang):
 p,uv,r=geometry(deg);im=Image.new('RGB',(1280,720),BG);d=ImageDraw.Draw(im);zh=lang=='zh'
 text(im,(30,16),('① 朝向改變 → 上下支撐點改變' if kind=='support' else '② 框高改變 → 針孔深度偏差') if zh else ('1. Yaw changes the height supports' if kind=='support' else '2. Box height changes pinhole depth'),34)
 text(im,(30,66),'幾何示意｜固定距離 10 m' if zh else 'Geometry illustration | distance fixed at 10 m',23,YELLOW)
 # Fixed display scaling, never fit box per frame; pixel measurements refer to FY above.
 pts=uv*1.55+np.array([480,220]);faces=[[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
 for j,face in sorted(enumerate(faces),key=lambda z:-np.mean(p[2,z[1]])):
  color=[(46,87,115),(80,137,173),(51,102,139),(40,78,106),(64,116,150),(39,84,117)][j];d.polygon([tuple(pts[k]) for k in face],fill=color,outline=(137,190,219),width=2)
 # Longitudinal nose arrow on roof, projected in same camera.
 a=math.radians(deg);arr=np.array([[0,Y-H-.02,Z],[L*.46*math.cos(a),Y-H-.02,Z-L*.46*math.sin(a)]])
 q=np.column_stack([FY*arr[:,0]/arr[:,2],FY*arr[:,1]/arr[:,2]])*1.55+np.array([480,220]);d.line([tuple(q[0]),tuple(q[1])],fill=(115,220,250),width=7);d.ellipse((q[1,0]-7,q[1,1]-7,q[1,0]+7,q[1,1]+7),fill=(115,220,250))
 lo=pts.min(axis=0);hi=pts.max(axis=0)
 if kind=='support':
  d.rectangle((*lo,*hi),outline=RED,width=3)
  for k in [r['upper_vertex'],r['lower_vertex']]:
   x,y=pts[k];d.line((lo[0]-25,y,hi[0]+35,y),fill=YELLOW,width=2);d.ellipse((x-9,y-9,x+9,y+9),fill=YELLOW)
  x=hi[0]+25;d.line((x,lo[1],x,hi[1]),fill=RED,width=5)
  x=lo[0]-35;y0=220+FY*(Y-H)/Z*1.55;y1=220+FY*Y/Z*1.55;d.line((x,y0,x,y1),fill=GREEN,width=6)
  text(im,(875,170),'框高' if zh else 'Box height',27,RED);text(im,(875,213),f"{r['h2d_px']:.1f} px",50)
  text(im,(875,308),'理想高度' if zh else 'Ideal height',27,GREEN);text(im,(875,350),f"{r['h_ideal_px']:.1f} px",50)
  text(im,(875,458),'比例 r' if zh else 'Ratio r',27);text(im,(875,500),f"{r['ratio']:.3f}",56,YELLOW)
 else:
  text(im,(870,160),'真實距離' if zh else 'True depth',27,GREEN);text(im,(870,200),'10.00 m',52,GREEN)
  text(im,(870,303),'針孔估計' if zh else 'Pinhole depth',27,RED);text(im,(870,345),f"{r['z_pinhole_m']:.2f} m",52,RED)
  text(im,(870,453),'深度偏差' if zh else 'Depth bias',27);text(im,(870,497),f"{r['bias_m']:+.2f} m",52,YELLOW)
  # Fixed metric ruler visually separates true and estimated range.
  x0,x1=100,760;yy=570;d.line((x0,yy,x1,yy),fill=(100,118,130),width=3)
  for z in [6,7,8,9,10,11]:
   xx=x0+(z-6)/5*(x1-x0);d.line((xx,yy-5,xx,yy+5),fill=WHITE,width=2);text(im,(xx-12,yy+8),str(z),20)
  for z,c in [(Z,GREEN),(r['z_pinhole_m'],RED)]:
   xx=x0+(z-6)/5*(x1-x0);d.ellipse((xx-9,yy-9,xx+9,yy+9),fill=c)
 # Yaw indicator makes rotation unmistakable independently of perspective.
 center=(110,165);d.ellipse((60,115,160,215),outline=(85,105,119),width=2);end=(110+43*math.cos(a),165-43*math.sin(a));d.line((*center,*end),fill=YELLOW,width=6)
 text(im,(185,135),f"{deg:.0f}°",50,YELLOW)
 text(im,(30,655),('黃點：上下支撐點　綠線：理想高度' if kind=='support' else 'Z = fy H / h2D　｜　框越高，估計距離越近') if zh else ('Yellow dots: height supports | Green: ideal height' if kind=='support' else 'Z = fy H / h2D  |  Taller box → smaller estimated depth'),25)
 return im

def encode(name,keys,func):
 first=func(keys[0]);w,h=first.size;p=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r','30','-i','-','-an','-c:v','libx264','-preset','veryfast','-threads','3','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/(name+'.mp4'))],stdin=subprocess.PIPE)
 last=None
 for k in keys:
  if k!=last:buf=func(k).tobytes();last=k
  p.stdin.write(buf)
 p.stdin.close();assert p.wait()==0;func(keys[len(keys)//2]).save(OUT/(name+'.jpg'));print(name,flush=True)

def main():
 mapping=[{'output_frame':i,'source_frame':b.IDS[int(i*198/299)]} for i in range(300)];b.csvout(OUT/'frame_mapping.csv',mapping)
 angles=[float(i) for i in np.linspace(0,180,360)];b.csvout(OUT/'yaw_geometry.csv',[dict(output_frame=i,**geometry(a)[2]) for i,a in enumerate(angles)])
 for lang in ['zh','en']:
  for name,(v,ms) in b.SPECS.items():encode(name+'_'+lang,[x['source_frame'] for x in mapping],lambda f:compare(f,v,ms,lang))
  for kind in ['support','depth']:encode('yaw_'+kind+'_'+lang,angles,lambda a:mechanism(a,kind,lang))
 for n in ['per_frame.csv','summary.json']:(OUT/n).write_bytes((b.OUT/n).read_bytes())
 b.savej(OUT/'manifest.json',{'source':'controlled_20261116 for RGB; synthetic cuboid only for yaw_*','geometry':dict(H=H,W=W,L=L,Z=Z,fy=FY,bottom_y=Y,yaw_range=[0,180],definition='h_ideal=fy*H/Z; h2d=max projected v-min projected v of cuboid; not verified Blender training h3D_proj'), 'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.suffix in ['.mp4','.csv','.jpg']}})
if __name__=='__main__':main()
