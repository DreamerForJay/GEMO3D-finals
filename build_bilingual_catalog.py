from pathlib import Path
import build_bilingual_demo as b
out=b.OUT
html='''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GEMO3D bilingual demo</title><style>body{font:18px system-ui;background:#10171d;color:#eee;max-width:1100px;margin:auto;padding:24px}video{width:100%;max-height:75vh;background:black}select{font:inherit;padding:10px;background:#26343f;color:white;margin:6px;max-width:95%}p{line-height:1.6}a{color:#8cddad}details{margin:20px 0}table{border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #465461}</style><h1>GEMO3D｜中英文影片</h1><label>語言 / Language <select id="lang"><option value="zh">中文</option><option value="en">English</option></select></label><label>內容 / Clip <select id="clip"><option value="yaw_support">① 朝向與支撐點 / Yaw & supports</option><option value="yaw_depth">② 針孔深度偏差 / Pinhole bias</option>'''
for name,(view,ms) in b.b.SPECS.items():
 title=('俯視 / BEV' if view=='bev' else '前視 / Front')+' · '+' / '.join(b.NAMES['zh'][m] for m in ms)
 html+=f'<option value="{name}">{title}</option>'
html+='''</select></label><p id="legend"></p><video id="video" controls playsinline preload="metadata"></video><p><a id="download" download>下載目前影片 / Download clip</a></p><details open><summary>朝向角影片怎麼看？ / Reading the yaw clips</summary><p>① 黃點是決定框高的上下支撐點；紅框是投影外接框；綠線是理想高度。藍色車輛外接盒只旋轉，距離固定10m。淡藍線標車頭方向，左上角方向盤顯示yaw。② 綠色真實距離不動；紅色針孔估計隨框高變動。兩片使用相同角度與資料，可以分開講解原因與結果。</p><p>Yellow dots mark the projected height extrema; red is the projected bounding rectangle, green the ideal height. A cyan nose marker and yaw dial reveal rotation. Clip 2 compares fixed true depth with pinhole depth. Both clips share the same sweep.</p><p><b>幾何示意 / Geometry illustration：</b>這是矩形車輛外接盒的精確透視投影，不是實測旋轉影片、偵測器輸出或模型準確率。h_ideal = fy H / Z，r = h2D / h_ideal，Z_pinhole = Z / r。原訓練h3D,proj定義仍待原始建模腳本核對。影像框支撐點在物體輪廓上的位置可切換；不表示所有真實車型或任意角度都有相同偏差方向。</p></details><details><summary>實測影片圖例與數據 / Recorded-data legend</summary><p>綠虛線＝GT，紅實線＝預測。3D中心誤差越低越好；BEV重疊率越高越好。黃色大字僅強調數值，不代表新物件。Full＝完整F流程，貼合＝tightfit。199來源影格完整保留，漏檢標未配對；影片30fps為離線播放，非推論速度。RGB配對以image ID為準，原metadata的三處重複仍保留。</p><p>Green dashed = GT; red solid = prediction. Lower 3D center error / higher BEV IoU is better. Yellow highlights numbers only. Unmatched observations are not zero errors. These are re-rendered controlled predictions, not new inference. Image-ID pairing does not establish strict sensor synchronization.</p><a href="per_frame.csv">逐幀實測 / Recorded pairs</a> · <a href="summary.json">整段統計 / Summary</a> · <a href="yaw_geometry.csv">幾何示意數據 / Synthetic geometry</a></details><script>
const video=document.querySelector('#video'),clip=document.querySelector('#clip'),lang=document.querySelector('#lang');function update(){const t=video.currentTime||0,playing=!video.paused,n=clip.value+'_'+lang.value;video.pause();video.onloadedmetadata=()=>{video.currentTime=Math.min(t,video.duration-.02);if(playing)video.play().catch(()=>{});};video.src=n+'.mp4';video.poster=n+'.jpg';document.querySelector('#download').href=n+'.mp4';document.querySelector('#legend').textContent=clip.value.startsWith('yaw')?'幾何示意：固定距離，只改朝向 / Geometry only: fixed depth, changing yaw':'綠虛線 GT · 紅實線預測 / Green dashed GT · Red prediction';}clip.onchange=lang.onchange=update;update();</script></html>'''
(out/'index.html').write_text(html)
(out/'README.md').write_text('''# 中英文大字版 + 朝向角機制分片

28支影片：原12種單方法／成對視角各有中文、英文版（24支10秒），另有支撐點／深度偏差兩支幾何示意各兩語（4支12秒）。index.html可切換影片與語言，保留播放時間。數值54px，放在專用142px標頭；實測影片不塞入圖表。

## 朝向機制與定義

- 藍色長方體代表車輛外接盒，不是真實車身mesh。固定尺寸H1.511/W2.128/L4.902m，中心Z10m，底部Y1.65m，fy721.5377px，無pitch，只掃yaw0–180°。本設定yaw亦為觀測角（X=0）；長方體幾何180°週期。
- h2D=max(v)-min(v)，由8角點精確透視投影得到；黃點標上下極值，重合極值只選一個頂點。淡藍車頭標記與方向盤顯示旋轉。h_ideal=fy*H/Z是同中心深度直立線段的投影高度，綠線為固定參考。
- r=h2D/h_ideal，Z_pinhole=fy*H/h2D=Z/r，bias=Z_pinhole-Z。第一片看高度比例，第二片看距離偏差，無曲線混入。
- 這不是原始Blender訓練資料的h3D,proj重現；其分母原始建模定義尚未核實。不使用GT比例校正來冒充模型改善，也不是實測轉角因果影片。不能推廣這個長方體的幅度／符號至所有車輛輪廓與相機姿態。
- yaw_geometry.csv是獨立合成數據；per_frame.csv/summary.json才是controlled_20261116實測輸出。實測數值和未配對計數均不變，既有同步／尺寸先驗限制保留。

## 重建與驗證

python build_bilingual_demo.py → python build_bilingual_catalog.py → python validate_bilingual_demo.py；網頁：node validate_bilingual_page.cjs。依賴既有build_clean_demo.py、build_demo_assets.py及原本資料根目錄。raw資料與權重不包含在包中。

## 名詞

針孔基準=Pinhole；Rank-1補償=Rank-1；完整流程=Full；停用貼合=no tightfit；俯視重疊率=BEV IoU；3D中心誤差=3D center error；上下支撐點=height supports；理想高度=ideal height；深度偏差=depth bias。
''')
