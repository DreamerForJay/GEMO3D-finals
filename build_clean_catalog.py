from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()))
import build_clean_demo as b
out=b.OUT
html='''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GEMO3D｜分開比較</title><style>body{font:17px system-ui;background:#111517;color:#ecf0ed;margin:auto;max-width:1100px;padding:24px}h1{font-size:30px}p{line-height:1.6;color:#b9c4bd}button,select{font:inherit;background:#26312b;color:white;border:1px solid #6b8072;border-radius:8px;padding:10px;margin:4px}video{display:block;width:100%;max-height:72vh;background:#080a09;margin-top:18px}a{color:#8cd7ae}.legend{padding:15px;border:1px solid #35423a;border-radius:10px}.green{color:#50e141}.red{color:#f54141}section{margin-top:28px}img{max-width:100%}summary{cursor:pointer}td,th{padding:8px;text-align:left}table{display:block;overflow:auto}</style><h1>GEMO3D｜一次看一種比較</h1><p>前視看 3D 框的位置；俯視看框的地面範圍重疊。比較影片各格使用同一來源影格。</p><div class="legend"><span class="green">▱ 綠色虛線＝真值 GT</span>　<span class="red">▱ 紅色實線＝預測</span></div><section><label>比較內容 <select id="case"><option value="compensation">補償前 → Rank-1</option><option value="tightfit">Full 停用 → 啟用 tightfit</option><option value="F">只看 Full</option><option value="D">只看 Rank-1</option><option value="A">只看 Pinhole</option><option value="F_no_tightfit">只看 Full 停用 tightfit</option></select></label><label>視角 <select id="view"><option value="bev">實際俯視影像</option><option value="front">前視 3D 框</option></select></label><video id="video" controls playsinline preload="metadata" src="bev_compensation.mp4" poster="bev_compensation.jpg"></video><p id="hint"></p><a id="download" href="bev_compensation.mp4" download>下載目前影片</a></section><section><details><summary>數字是什麼意思？</summary><p>BEV IoU＝兩個框地面範圍的交集面積 ÷ 聯集面積，0–1，越高越好。框是地面投影，不是車頂輪廓；畫面使用 CARLA 實際俯視相機。3D error＝預測與真值幾何中心距離，單位公尺，越低越好。unmatched 表示未配對，不當作 0。</p></details><details><summary>另外看誤差曲線與整段數據</summary><p>橫軸＝來源影格；縱軸＝3D 中心誤差（m）。越低越好；斷線＝未配對。曲線不放進影片。</p><img src="center_error.png" alt="逐影格3D中心誤差"><table><thead><tr><th>設定</th><th>深度 RMSE (m)</th><th>配對</th><th>漏檢</th></tr></thead><tbody>'''
for m in b.METHODS:
 s=b.stats(m,b.IDS);html+=f'<tr><td>{b.METHODS[m]}</td><td>{s["depth_rmse_m"]:.3f}</td><td>{s["matches"]}</td><td>{s["unmatched_gt"]}</td></tr>'
html+='''</tbody></table><p><a href="per_frame.csv">逐幀數據 CSV</a> · <a href="summary.json">整段統計 JSON</a></p></details><details><summary>來源與限制</summary><p>11/16 控制實驗既有預測，199 張來源影像完整保留；離線重取樣成 10 秒，不代表推論 FPS。方法分格按 image ID 對照；既有 metadata 有三處重複時間／幀號，不宣稱嚴格感測器時間同步。Full＝完整 F 管線，並非 full 矩陣補償變體。預測尺寸先驗與真值不同，框大小偏差也是誤差來源。尚無可核實的真實轉彎因果影片。本版不是新推論。</p></details></section><script>const video=document.getElementById('video'),which=document.getElementById('case'),view=document.getElementById('view'),hint=document.getElementById('hint');function update(){const t=video.currentTime||0,wasPlaying=!video.paused,name=view.value+'_'+which.value;video.pause();video.src=name+'.mp4';video.poster=name+'.jpg';document.getElementById('download').href=name+'.mp4';video.onloadedmetadata=()=>{video.currentTime=Math.min(t,video.duration-.01);if(wasPlaying)video.play().catch(()=>{});};hint.textContent=view.value==='bev'?'左右比較｜BEV IoU 越高，地面框重疊越好。':'上下比較｜3D error 越低，中心位置越準。';if(!['tightfit','compensation'].includes(which.value))hint.textContent=hint.textContent.split('｜')[1];}which.onchange=update;view.onchange=update;hint.textContent='左右比較｜BEV IoU 越高，地面框重疊越好。';</script></html>'''
(out/'index.html').write_text(html)
(out/'README.md').write_text('''# 清爽比較素材（取代解說密集版作為預設入口）

開啟 index.html：一次只播放一種比較／視角。12 支 10 秒影片：四種設定各自前視、俯視，加上 A/D 與 F_no_tightfit/F 的前視、俯視比較。所有影片保留199來源影格，沒有圖表、說明段落、片尾卡；只留方法名與一個當幀指標。

- 綠色虛線＝GT；紅色實線＝預測。前視為3D框，俯視為同一水平面上的框底面投影，非車頂輪廓。
- 真實 CARLA top_camera RGB，利用每幀前視／俯視外參轉換，不是格線示意或生成影像。
- BEV IoU以公尺XZ平面計算，不能將影像像素IoU當正式指標；各框統一投影到GT底部Y，讓顯示對應BEV定義，忽略預測高度偏差。
- unmatched保留，不當0；所有預測框仍畫出。summary.json為全199張配對統計；per_frame.csv為配對明細，未配對數在summary保留。
- 誤差曲線獨立center_error.png，橫軸影格、縱軸3D幾何中心誤差m；缺值斷線。影片上3D error不等於深度RMSE。
- Full指F完整流程；來源controlled_20261116，並非新推論或公平跨模型比較。資料三處重複timestamp/frame仍保留；按image ID配對，不保證嚴格時間同步。
- 所有影片離線30fps重取樣、10秒，不是實測推論效能。沒有新增真實轉角因果影片。

重建：python build_clean_demo.py → python build_clean_catalog.py；驗證：python validate_clean_demo.py。前視比較上下排列以保留原始寬幅解析度；俯視左右排列。所有單方法片可單獨嵌入其他網頁。

參考：MoGe-3 分開展示、Scal3R 分視角、GaMO 方法切換、RL-AWB 前後比較。沿用 docs/DEMO_REFERENCE_REVIEW.md 八頁對照。
''')
