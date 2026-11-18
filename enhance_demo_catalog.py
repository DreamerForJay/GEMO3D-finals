"""Enhance the existing offline catalog; all browser values derive from delivered CSV/JSON."""
from pathlib import Path
import json,csv,shutil
import cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results/demo'
LABEL={'A':'Pinhole A','D':'Rank-1 D','F':'GEMO3D full F','historical_monodetr':'MonoDETR (2023)','historical_monodgp':'MonoDGP (2025)','historical_monoamnet':'MonoAMNet (2025)','timing':'GEMO3D timed run'}
def enhance():
 data={};s=(OUT/'index.html').read_text();prints=OUT/'print';prints.mkdir(exist_ok=True)
 for folder in sorted(OUT.glob('G-*')):
  videos=[p for p in folder.glob('*.mp4') if '_short' not in p.stem]
  if not videos:continue
  summary=json.loads((folder/'summary.json').read_text());mappings={}
  for p in folder.glob('*_frame_mapping.csv'):
   for r in csv.DictReader(p.open()):mappings.setdefault(r['video'],[]).append(r)
  data[folder.name]={'summary':summary,'geometry':json.loads((folder/'geometry.json').read_text()),'rows':list(csv.DictReader((folder/'per_frame.csv').open())),'mappings':mappings,'labels':LABEL}
  for video in videos:
   cap=cv2.VideoCapture(str(video));sheet=Image.new('RGB',(3200,520),'#0d1726');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
   rows=mappings[video.name]
   for j,f in enumerate([summary['source_frames'][int((len(summary['source_frames'])-1)*i/3)] for i in range(4)]):
    k=next(i for i,r in enumerate(rows) if r['source_frame']==f);cap.set(cv2.CAP_PROP_POS_FRAMES,k);ok,frame=cap.read();assert ok
    sheet.paste(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).resize((800,450)),(j*800,55));d.text((j*800+12,15),f'{folder.name} {video.stem} | {f}',font=font,fill='white')
   cap.release();name=f'{folder.name}_{video.stem}.png';sheet.save(prints/name)
   needle=f'<h3>{video.stem}</h3><video';start=s.index(needle,s.index(f'id="{folder.name}"'));end=s.index('</video>',start)+len('</video>');s=s[:end]+f'<details class="print-frames"><summary>列印／簡報：四個關鍵影格</summary><a href="print/{name}"><img loading="lazy" src="print/{name}" alt="{folder.name} {video.stem} 四幀橫排圖"></a></details>'+s[end:]
  for video in videos:
   highlight=folder/(video.stem+'_highlight_short.mp4')
   if highlight.exists():
    needle=f'<h3>{video.stem}</h3>'
    start=s.index(needle,s.index(f'id="{folder.name}"'))+len(needle)
    links=f'<p><a href="{folder.name}/{highlight.name}">真正精華剪輯：固定3–13秒＋片段RMSE卡（12秒）</a> · <a href="{folder.name}/{video.stem}_highlight_summary.json">片段數據</a></p>'
    s=s[:start]+links+s[start:]
 payload=json.dumps(data,ensure_ascii=False,allow_nan=False,separators=(',',':')).replace('</','<\\/')
 (OUT/'interactive_data.js').write_text('window.GEMO_DEMO_DATA='+payload+';\n');shutil.copyfile(ROOT/'demo_interactions.js',OUT/'interactions.js')
 metrics=json.loads((OUT/'G-I1/summary.json').read_text())['methods']
 table='<section id="controlled-results"><h2>H｜可排序消融表（非跨方法排行榜）</h2><p>A／D／F 使用同一199幀，皆165個配對；缺失數一併列出。完整F未必比純Rank-1 D更好。原165共同樣本排行榜仍待核實。</p><table id="controlled-table"><thead><tr><th>配置</th>'+''.join(f'<th><button data-column="{i}">{name} ↕</button></th>' for i,name in enumerate(['深度RMSE(m)','深度MAE(m)','中心均值(m)','配對','漏檢'],1))+'</tr></thead><tbody>'
 for r in metrics:table+='<tr><td>'+LABEL[r['method']]+'</td>'+''.join(f'<td>{r[k]:.6f}</td>' if isinstance(r[k],float) else f'<td>{r[k]}</td>' for k in ['depth_rmse_m','depth_mae_m','center_mean_m','matches','unmatched_gt'])+'</tr>'
 table+='</tbody></table></section>'
 styles='<style>#controlled-results{overflow-x:auto}body{overflow-wrap:anywhere}.interactive-panel{padding:16px;background:#142234;margin:15px 0}canvas{width:100%;height:auto;display:block}.error-curve{cursor:crosshair}select,button{background:#233b58;color:#fff;padding:8px;border:1px solid #7091b6;border-radius:6px}table{width:100%;border-collapse:collapse}td,th{padding:12px;border-bottom:1px solid #40546c;text-align:left}output{display:block;line-height:1.7}summary{cursor:pointer;padding:12px 0}.print-frames img{margin:10px 0}@media print{body{background:white;color:black;max-width:none;padding:0}video,.interactive-panel,input,select,button,.pair,#G-C1,#G-K1{display:none}section{break-inside:avoid}.print-frames{display:block}.print-frames::details-content{content-visibility:visible}.print-frames img{display:block}a{color:black}h2{font-size:14pt}}</style>'
 s=s.replace('</html>',table+styles+'<script src="interactive_data.js"></script><script src="interactions.js"></script></html>');(OUT/'index.html').write_text(s)
 p=OUT/'README.md';t=p.read_text();t+='\n## v2 互動呈現\n\n逐幀曲線支援點擊定位、影格滑桿；以影片映射表定位，非假設每來源幀都佔1/30秒。互動BEV／3D線框可切換方法與旋轉。這是既有框的幾何檢視，不是稠密場景重建。A/D/F消融表可排序；未製造跨方法排行榜。`print/`提供六張3200×520四幀橫排PNG，包括四方法BEV版。原12秒版為整段加速呈現；另有6支 `_highlight_short.mp4` 真正片段剪輯：固定擷取完整版3–13秒，加上2秒片段數據卡（重算該片段unique source frames的RMSE）。時段為預先固定規則，不依誤差挑選。\n\n先執行原build_demo_catalog.py，它會自動呼叫enhance_demo_catalog.enhance；不要單獨重複套用enhance。互動資料由已交付CSV／geometry.json內嵌為JS，可file://離線開啟。\n';p.write_text(t)
if __name__=='__main__':raise SystemExit('Run build_demo_catalog.py to regenerate the base and apply once.')
