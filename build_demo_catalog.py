"""Build partial model-grid asset, honest delivery status, and an offline integration catalog.
Run after build_demo_assets.py. Does not claim missing capture or baseline validation complete.
"""
import json,csv,pickle,hashlib,html
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results/demo'
def savej(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
p=Path('/home/e114/Desktop/mono3d/GEMO3D/comp/sed_rank_ratio_linear_model.pkl');m=pickle.load(p.open('rb'));d=OUT/'G-D1';d.mkdir(exist_ok=True)
with (d/'model_ratio_grid.csv').open('w',newline='') as fp:
 w=csv.writer(fp,lineterminator='\n');w.writerow(['model_angle_deg','model_depth_m','original_ratio','rank1_ratio'])
 for i,a in enumerate(m['angle_grid']):
  for j,z in enumerate(m['depth_grid']):w.writerow([a,z,m['R_original_grid'][i,j],m['R_reconstructed_grid'][i,j]])
savej(d/'summary.json',dict(status='partial_model_grid_only',source=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),angle_range_deg=[float(min(m['angle_grid'])),float(max(m['angle_grid']))],rows=7200,limitation='Stored 0-180 degree model grid, NOT a new 0-360 capture. Raw h2D/h3D projection samples unavailable. No raw-height curve or extrapolated second half fabricated.'))
(d/'README.md').write_text('# G-D1：部分資料\n\nmodel_ratio_grid.csv 為既有補償模型內的 0–180° 比例網格（90×80），非新的 360° 拍攝。原始 h₂D、h₃D,proj 樣本不在 pkl；尚不能提供所需即時高度比例影片。原模型雜湊見 summary.json，不上傳權重。\n')
status=[
 ('G-A1','ready','18 秒 Teaser＋12 秒版；完整 F 的 199 幀、GT、BEV、誤差曲線。'),
 ('G-B1','partial','三個既有視角同 ID 配對；缺追車視角，3 處時間／幀號異常，嚴格同步未驗證。'),
 ('G-C1','partial','近中遠三張、各七步 PNG＋JSON；目前只有前視，缺斜側；sedan 為強制設定而非分類結果。'),
 ('G-E1','audit_preview','四方法前視／BEV 各 18 秒＋12 秒版；歷史基準設定未核實，禁止作公平排行榜。'),
 ('G-F1','ready','6 組同尺寸成對 PNG、影片與逐幀 CSV；A→D 只改補償，非完整 F。'),
 ('G-D1','partial','7200 筆模型比例網格可供互動圖；缺原始高度資料與 360° 實測掃描。'),
 ('G-H1','blocked','舊 165 筆來源混不同 GT，不能製成可信排行榜；見 historical_165_audit.md。'),
 ('G-I1','partial','深度分箱、逐幀觀測角與誤差 CSV、分析 PNG；缺受控 pitch 敏感度。'),
 ('G-M1','ready','100 幀實際計時及同次預測；RTX 3060 共享，89.241ms／11.206fps；影片為離線播放。'),
 ('G-K1','partial','15 例失敗圖＋3 張 tightfit 對照。強制 SUV 是人工干預，不是真實分類器誤判。'),
 ('G-J1','blocked','缺可核實 S1/S2/S4/S5 場景腳本與新捕捉；單一 approach 不冒充四情境。'),
 ('G-J2','blocked','缺 S3/S6/S7/S8–S10 場景捕捉。'),
 ('G-L1','blocked','缺路口監控捕捉與數位孿生對應資料。'),
 ('G-R1','blocked','缺有時間資訊的真實 KITTI raw/tracking 連續序列。')]
assets=[dict(code=c,status=s,note=n,files=[str(p.relative_to(OUT)) for p in sorted((OUT/c).rglob('*')) if p.is_file()]) for c,s,n in status];savej(OUT/'catalog.json',assets)
(OUT/'README.md').write_text('# Demo／網頁素材交付｜2026-11-18\n\n## 重點\n\n- 可用：G-A1 Teaser、G-F1 六組補償對照、G-M1 同次計時影片；另有步驟圖、三視角、方法比較查核預覽、分析與失敗素材。\n- 所有影片為 1080p／30fps／H.264；完整版 18 秒，簡報版 12 秒，各含 2 秒數據卡。播放重新取樣，不代表原始拍攝／推論 FPS。\n- 新控制完整 F 深度 RMSE 1.305m；A→D 1.694→0.762m。F 不比 D 好，未隱藏失敗。\n- capture_anomalies.json 有 3 個時間或幀號重複轉換。素材按影像 ID 排列，不宣稱嚴格時間同步。\n\n## 使用\n\n解壓後直接開啟 index.html 可離線預覽影片、拖曳對照與七步圖，不需安裝工具。catalog.json 為網站整合入口；讀各項 summary.json、per_frame.csv、geometry.json。影片時間與來源影格用 video_frame_mapping.csv（BEV 用 bev_frame_mapping.csv）對應。缺值是未配對，不可轉成零。\n\n```bash\npython build_demo_assets.py\npython build_demo_catalog.py\npython validate_demo_assets.py\n```\n\n依賴 Python 3、numpy、Pillow、opencv-python、matplotlib、imageio-ffmpeg。原資料、權重與精確命令見 results/controlled_20261116/manifest.json；預測／GT 幾何已隨包提供。重建背景圖片仍需本機原資料（未打包完整資料集）。非已部署網站。\n\n## 狀態\n\n| 素材 | 狀態 | 範圍／限制 |\n|---|---|---|\n'+''.join(f'| {c} | {s} | {n} |\n' for c,s,n in status)+'\n原始整體架構圖任務 C 依使用者要求跳過；G-C1 是本次新增的逐步輸出素材，兩者不同。\n')
# Keep new capture caveat visible in all summaries without changing measurements.
for p in OUT.glob('*/summary.json'):
 x=json.loads(p.read_text());x['capture_note']='Dataset metadata has non-increasing timestamps/simulator frame IDs at 000091→000092, 000094→000095, 000097→000098. Ordered image IDs do not prove strict temporal synchronization.';savej(p,x)
k=OUT/'G-K1/README.md'
if k.exists():
 txt=k.read_text().replace('../tightfit_ablation.csv','../../tightfit_ablation.csv').replace('../controlled_20261116/pairs.csv','../../controlled_20261116/pairs.csv');k.write_text(txt)
parts=['''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GEMO3D 素材預覽</title><style>body{background:#0d1726;color:#e8f0f8;font:17px system-ui;max-width:1200px;margin:auto;padding:30px}a{color:#8cc1ff}section{border-top:1px solid #43546a;padding:28px 0}video,img{max-width:100%;height:auto}video{width:100%;background:black}label,select{display:block;margin:14px 0}input{width:100%}.pair{position:relative}.pair img{display:block;width:100%}.pair .after{position:absolute;inset:0;clip-path:inset(0 0 0 50%)}.warn{color:#ffbd72}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}</style><h1>GEMO3D｜Demo 與網頁素材</h1><p>2026-11-18 · 離線交付預覽 · <a href="README.md">交接說明</a> · <a href="catalog.json">整合清單 JSON</a></p><p class="warn">30 fps 是影片播放速度。歷史基準設定未核實；四方法預覽不能當公平排行榜。素材依影像 ID 排列，捕捉時間有三處異常。</p>''']
for item in assets:
 c=item['code'];parts.append(f'<section id="{c}"><h2>{c} · {item["status"]}</h2><p>{html.escape(item["note"])}</p>')
 for v in (OUT/c).glob('*.mp4'):
  if '_short' in v.stem:continue
  path=str(v.relative_to(OUT));parts.append(f'<h3>{v.stem}</h3><video controls preload="none" playsinline poster="{c}/poster.jpg"><source src="{path}" type="video/mp4"></video><p><a href="{c}/{v.stem}_short.mp4">12 秒簡報版</a></p>')
 if c=='G-F1':
  pairs=json.loads((OUT/c/'slider_pairs.json').read_text())
  for pair in pairs:
   parts.append(f'<p>{pair["frame"]} · 左補償前／右補償後</p><div class="pair"><img alt="補償前" src="{c}/{pair["before"]}"><img class="after" alt="補償後" src="{c}/{pair["after"]}"></div><label>拖曳比較<input aria-label="補償前後分界" type="range" value="50" min="0" max="100" oninput="this.parentElement.previousElementSibling.querySelector(\'.after\').style.clipPath=\'inset(0 0 0 \'+this.value+\'%)\'"></label>')
 if c=='G-C1':
  for f in ['000043','000110','000170']:
   parts.append(f'<h3>{f}</h3><img alt="{f} 方法步驟" src="{c}/{f}/step_1.png"><label>方法步驟 1–7<input aria-label="{f} 方法步驟" type="range" value="1" min="1" max="7" step="1" oninput="this.parentElement.previousElementSibling.src=\'{c}/{f}/step_\'+this.value+\'.png\'"></label>')
 if c=='G-I1':parts.append(f'<img src="{c}/depth_bins.png" alt="各距離區間深度誤差">')
 if c=='G-K1':parts.append('<div class="grid">'+''.join(f'<a href="{c}/{p.name}"><img loading="lazy" alt="{p.stem}" src="{c}/{p.name}"></a>' for p in sorted((OUT/c).glob('*.jpg')))+'</div>')
 if (OUT/c/'README.md').exists():parts.append(f'<p><a href="{c}/README.md">來源與限制</a>')
 if (OUT/c/'per_frame.csv').exists():parts.append(f' · <a href="{c}/per_frame.csv">逐幀 CSV</a> · <a href="{c}/summary.json">數據摘要</a>')
 parts.append('</section>')
parts.append('</html>');(OUT/'index.html').write_text('\n'.join(parts))
# Bind every rendered sensor frame and intermediate CSV to local source hashes.
data=Path('/home/e114/KITTI_ROOT/sed_lincoln_fr_T1R8/data/KITTIDataset_Carla/training')
sources=[]
for f in range(199):
 for sub,suffix in [('image_2','.png'),('label_2','.txt'),('calib','.txt'),('meta','.json'),('bev_iou','.png'),('side_iou','.png')]:
  q=data/sub/(f'{f:06d}'+suffix);sources.append(dict(path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest()))
for variant in ['A','D','F']:
 q=ROOT/f'benchmark_output/controlled_20261116/{variant}/pred_meta.csv';sources.append(dict(path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest()))
savej(OUT/'source_hashes.json',sources)
# Artifact checksum manifest excludes itself and post-build validation report.
files={str(p.relative_to(OUT)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ['manifest.json','validation.json']};savej(OUT/'manifest.json',dict(files=files,requirements_revision='4bf3a08',inference_revision='dca5aa6',scripts={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['build_demo_assets.py','build_demo_catalog.py']}))
print('Catalog:',len(assets),'assets;',len(files),'files')
