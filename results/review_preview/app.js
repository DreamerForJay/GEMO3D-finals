'use strict';
const $=id=>document.getElementById(id),names={A:'針孔基準 A',D:'Rank-1 補償 D',F_no_tightfit:'完整流程／停用貼合',F:'完整流程 Full F'};
const video=$('video');
function tab(id){document.querySelectorAll('[data-tab]').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.tab===id)));document.querySelectorAll('[role=tabpanel]').forEach(p=>p.hidden=p.id!==id);if(id!=='media')video.pause();}
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>tab(b.dataset.tab));
// Accessible left/right navigation within tabs, without altering the native tab order.
$('workspace').onkeydown=e=>{if(!['ArrowLeft','ArrowRight'].includes(e.key))return;const tabs=[...document.querySelectorAll('[data-tab]')],i=tabs.indexOf(document.activeElement);if(i<0)return;e.preventDefault();const next=tabs[(i+(e.key==='ArrowRight'?1:tabs.length-1))%tabs.length];next.focus();next.click();};
function bars(){const key=$('metric').value,max=Math.max(...DEMO_SUMMARY.map(s=>s[key]))*1.1;$('bars').innerHTML=DEMO_SUMMARY.map(s=>`<div class="barrow"><div class="barlabels"><span>${names[s.method]}</span><strong>${s[key].toFixed(3)} m</strong></div><div class="track"><div class="bar" style="width:${s[key]/max*100}%"></div></div></div>`).join('');$('metric-note').textContent=key==='center_rmse_m'?'三維幾何中心的整段RMSE；與影片當幀誤差分開。':key==='depth_mae_m'?'相機前向距離Z的平均絕對誤差。':'相機前向距離Z的整段RMSE；較大的偏差會受到較高權重。';}
$('metric').onchange=bars;bars();
function media(){const t=video.currentTime||0,playing=!video.paused,clip=$('clip').value,synthetic=clip.startsWith('yaw'),name=clip+'_'+$('lang').value;video.pause();video.onloadedmetadata=()=>{video.currentTime=Math.min(t,video.duration-.02);if(playing)video.play().catch(()=>{});};video.src='../bilingual_demo/'+name+'.mp4';video.poster='../bilingual_demo/'+name+'.jpg';$('download').href=video.src;$('media-status').textContent=synthetic?'幾何示意 · 非實測':'既有實測 · 控制推論重繪';$('media-status').className='pill'+(synthetic?' pending':'');$('legend').innerHTML=synthetic?'黃點＝上下支撐點 · 青色＝車頭標記 · 綠色＝理想高度／真實距離':'<span class="green">綠色虛線＝真值 GT</span>　<span class="red">紅色實線＝預測</span>';$('caption').textContent=synthetic?'固定距離的長方體投影。示意資料與實測結果分開保存。':'全199張來源影格保留；未配對不視為零。依image ID對照，非嚴格感測器同步證明。';$('geometry-notes').hidden=!synthetic;}
$('clip').onchange=$('lang').onchange=media;media();
const plans=[
['P0','固定距離轉角','把幾何示意補成真實車身證據。','固定相機及車輛中心，在10／20／30m分別旋轉車身；角度與距離分開控制。前視＋斜上方展示，每個距離各自成片。','GT姿態與距離、instance mask輪廓高度、偵測框高度、fyH/Z理想高度，以及補償前後的預測。'],
['P0','路口左轉／右轉','確認朝向與距離一起改變時的表現。','固定前視觀測車輛左／右轉，另存固定俯視全景；兩個方向各自錄完整原片。','逐幀角度、GT與預測軌跡、中心誤差、BEV IoU及所有未配對。'],
['P0','同條件方法比較','讓方法差異有可核實的共同條件。','以同一輸入序列跑各方法，先核對權重、前處理、閾值與匹配規則，再輸出前視與BEV比較。','每個方法的commit、權重hash、完整命令、每幀預測與配對規則；現有歷史基準不足以正式排名。'],
['P1','超車／切入','看側面轉背面、遮擋與框抖動。','各拍超車、被超車、前車切入；前視保留模型輸入，車尾斜上方追車只用來交代場景。','目標ID、可見度、截斷情況、逐幀位置與朝向、漏檢，以及同幀俯視。'],
['P1','遠近距離變化','看小目標到近距離的穩定程度。','固定前視，目標從遠到近再遠離；側視全景記錄運動關係。先固定車型與朝向。','框高px、GT距離、預測距離、誤差與未配對；整段數據加距離分箱。'],
['P1','不同車型','檢查尺寸先驗是否限制泛化。','sedan／SUV／van在相同距離與角度拍攝；區分強制車型與實際分類器結果。','實際尺寸、使用的尺寸先驗、車型輸入來源、分類結果及同條件誤差。'],
['P1','失敗案例','清楚說明方法的適用邊界。','分開收集遮擋、截斷、遠距離、車型誤判；保留完整片段，原因僅在有證據時下結論。','原圖、GT／預測、失敗前後影格、漏檢與匹配結果；不要只保存成功樣本。'],
['P2','真實道路連續序列','補上CARLA以外的定性與定量證據。','使用具校正資料的真實連續序列；有GT才計準確率，沒有GT時明標定性展示。','相機校正、資料授權、原始時序、推論設定；若有GT則保存配對及誤差。']
];
$('scenarios').innerHTML=plans.map((p,i)=>`<button class="scenario" data-plan="${i}" aria-pressed="${i===0}"><span class="num">${p[0]} · 建議蒐集</span><h3>${p[1]}</h3><p>${p[2]}</p></button>`).join('');
function plan(i){document.querySelectorAll('[data-plan]').forEach(b=>b.setAttribute('aria-pressed',String(+b.dataset.plan===i)));const p=plans[i];$('priority').textContent=p[0]+' · 尚待蒐集';$('plan-title').textContent=p[1];$('plan-why').textContent=p[2];$('plan-how').textContent=p[3];$('plan-save').textContent=p[4];}
document.querySelectorAll('[data-plan]').forEach(b=>b.onclick=()=>plan(+b.dataset.plan));plan(0);
const cameras=[['前視輸入','模型唯一輸入。看2D／3D框與預測距離；其他視角不送入模型。','<path d="M155 115L290 85V160Z" fill="#63a487" opacity=".24"/><circle cx="155" cy="115" r="8" fill="#146c57"/>'],['固定俯視','看完整軌跡、車距與BEV偏移。使用固定全景，避免跟隨目標讓背景運動難以辨讀。','<rect x="55" y="55" width="370" height="150" rx="12" fill="none" stroke="#146c57" stroke-width="3"/><text x="190" y="42" fill="#146c57" font-size="14">上方俯視範圍</text>'],['斜上追車','交代相機裝在哪裡、超車或切入如何發生；只作展示視角。','<path d="M50 48L140 95M50 48L280 150" stroke="#146c57" stroke-width="2"/><circle cx="50" cy="48" r="9" fill="#146c57"/>'],['固定側視','看前後位置、坡度與高度關係；適合距離偏差分析。','<path d="M240 28L185 80M240 28L365 80" stroke="#146c57" stroke-width="2"/><circle cx="240" cy="28" r="9" fill="#146c57"/>']];
$('camera-controls').innerHTML=cameras.map((c,i)=>`<button data-camera="${i}" aria-pressed="${i===0}">${c[0]}</button>`).join('');function camera(i){document.querySelectorAll('[data-camera]').forEach(b=>b.setAttribute('aria-pressed',String(+b.dataset.camera===i)));$('camera-copy').textContent=cameras[i][1];$('camera-mark').innerHTML=cameras[i][2];}document.querySelectorAll('[data-camera]').forEach(b=>b.onclick=()=>camera(+b.dataset.camera));camera(0);
