/* Offline interactions: only recorded predictions/GT; no network or inferred measurements. */
'use strict';
function frameAt(mapping,time){return mapping[Math.max(0,Math.min(mapping.length-1,Math.floor(time*30+1e-6)))];}
function meanError(rows,key){const v=rows.filter(r=>r.status==='matched').map(r=>Math.abs(Number(r[key])));return v.length?v.reduce((a,b)=>a+b,0)/v.length:null;}
function firstTime(mapping,f){return mapping.findIndex(r=>r.source_frame===f)/30;}
function boxCorners(o){const c=Math.cos(o.ry),s=Math.sin(o.ry);return [[1,0,1],[1,0,-1],[-1,0,-1],[-1,0,1],[1,-1,1],[1,-1,-1],[-1,-1,-1],[-1,-1,1]].map(([a,b,d])=>{const x=a*o.l/2,z=d*o.w/2;return [c*x+s*z+o.x,b*o.h+o.y,-s*x+c*z+o.z];});}
const EDGES=[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];
function initDemoInteractions(){
const DATA=window.GEMO_DEMO_DATA,colors=['#3994ff','#64daab','#f577b0','#e5c053'];
for(const video of document.querySelectorAll('section video')){
 const section=video.closest('section'),asset=DATA[section.id];if(!asset)continue;
 const name=video.querySelector('source').getAttribute('src').split('/').pop(),mapping=asset.mappings[name];if(!mapping)continue;
 const methods=asset.summary.methods.map(m=>m.method),ids=asset.summary.source_frames;
 const unit=section.id==='G-E1'?'center_error':'depth_error';
 const curveValues=Object.fromEntries(methods.map(m=>[m,ids.map(f=>meanError(asset.rows.filter(r=>r.method===m&&r.frame===f),unit))]));
 const host=document.createElement('div');host.className='interactive-panel';
 host.innerHTML='<p>互動誤差曲線：點擊或使用影格滑桿定位。缺口代表未配對，不是零誤差。</p><canvas class="error-curve" width="1200" height="280" aria-label="逐幀誤差曲線"></canvas><label>來源影格<input class="frame-seek" aria-label="定位來源影格" type="range" min="0" max="'+(ids.length-1)+'" value="0"></label><output class="frame-info" aria-live="off"></output><details><summary>G｜互動 BEV／3D 框（同一影格，可切換方法）</summary><label>方法<select class="method-select" aria-label="檢視方法"></select></label><label>視角<select class="view-select" aria-label="檢視角度"><option value="bev">BEV 鳥瞰</option><option value="3d">3D 線框（正交投影）</option></select></label><label>3D 旋轉角<input class="orbit" aria-label="旋轉3D框" type="range" min="-180" max="180" value="25"></label><canvas class="geometry-view" width="1200" height="500" aria-label="預測與GT幾何框"></canvas><p>藍色：預測；橘虛線：GT。僅顯示已記錄的框，沒有重建車身或補出漏檢。固定 0–40m 範圍；範圍外預測仍保留於計數與 geometry.json。</p></details>';
 video.insertAdjacentElement('afterend',host);
 const chart=host.querySelector('.error-curve'),ctx=chart.getContext('2d'),range=host.querySelector('.frame-seek'),info=host.querySelector('.frame-info'),select=host.querySelector('.method-select'),view=host.querySelector('.view-select'),orbit=host.querySelector('.orbit'),canvas=host.querySelector('.geometry-view'),g=canvas.getContext('2d');
 for(const m of methods){const o=document.createElement('option');o.value=m;o.textContent=asset.labels[m];select.append(o);}
 const maximum=Math.max(1,...Object.values(curveValues).flat().filter(x=>x!==null))*1.08;
 function geometry(f){
  g.fillStyle='#142234';g.fillRect(0,0,1200,500);g.font='20px system-ui';g.fillStyle='#e8f0f8';g.fillText(asset.labels[select.value]+' · '+f,20,32);
  const angle=Number(orbit.value)*Math.PI/180;
  const project=([x,y,z])=>view.value==='bev'?[600+x*11,465-z*10]:[600+(Math.cos(angle)*x+Math.sin(angle)*(z-20))*12,290+y*24-(Math.cos(angle)*(z-20)-Math.sin(angle)*x)*7];
  g.strokeStyle='#40546c';g.setLineDash([]);g.lineWidth=1;
  for(let z=0;z<=40;z+=5){const a=project([-12,0,z]),b=project([12,0,z]);g.beginPath();g.moveTo(...a);g.lineTo(...b);g.stroke();}
  const pred=asset.geometry.predictions[select.value][f],gt=asset.geometry.gt[f];
  for(const [objects,color,dash] of [[gt,'#ff9e39',[6,5]],[pred,'#3994ff',[]]]){g.strokeStyle=color;g.lineWidth=2;g.setLineDash(dash);for(const o of objects){if(o.z<0||o.z>40||Math.abs(o.x)>12)continue;const p=boxCorners(o).map(project);for(const [i,j] of EDGES){g.beginPath();g.moveTo(...p[i]);g.lineTo(...p[j]);g.stroke();}}}
  g.setLineDash([]);g.fillStyle='#e8f0f8';g.fillText('Pred '+pred.length+' / GT '+gt.length+' · 固定範圍裁切',20,480);
 }
 function draw(){
  const row=frameAt(mapping,video.currentTime),ended=row.phase==='summary',f=ended?ids[ids.length-1]:row.source_frame,ix=ids.indexOf(f);range.value=ix;
  ctx.fillStyle='#142234';ctx.fillRect(0,0,1200,280);ctx.font='17px system-ui';
  const X=i=>70+i*1100/(ids.length-1),Y=v=>235-v/maximum*160;
  ctx.strokeStyle='#40546c';ctx.fillStyle='#c8d9e9';
  for(let j=0;j<4;j++){const v=maximum*j/3;ctx.beginPath();ctx.moveTo(70,Y(v));ctx.lineTo(1170,Y(v));ctx.stroke();ctx.fillText(v.toFixed(2),5,Y(v)+5);}
  methods.forEach((m,j)=>{ctx.fillStyle=colors[j];ctx.fillText(asset.labels[m],70+j*280,25);ctx.strokeStyle=colors[j];ctx.lineWidth=2;ctx.beginPath();let gap=true;curveValues[m].forEach((v,i)=>{if(v===null){gap=true;return;}if(gap)ctx.moveTo(X(i),Y(v));else ctx.lineTo(X(i),Y(v));gap=false;});ctx.stroke();});
  ctx.strokeStyle='#fff';ctx.beginPath();ctx.moveTo(X(ix),60);ctx.lineTo(X(ix),235);ctx.stroke();ctx.fillStyle='#e8f0f8';ctx.fillText('Frame '+ids[0]+' → '+ids.at(-1)+' | '+(unit==='center_error'?'3D中心誤差':'絕對深度誤差')+' (m)',70,267);
  info.textContent=(ended?'片尾數據卡；保留最後資料影格 ':'影格 ')+f+' · '+methods.map(m=>asset.labels[m]+': '+(curveValues[m][ix]===null?'未配對':curveValues[m][ix].toFixed(3)+'m')).join(' / ');
  geometry(f);host.dataset.sourceFrame=f;host.dataset.phase=row.phase;
 }
 function seek(ix){const t=firstTime(mapping,ids[ix]);if(t>=0){video.currentTime=t+1/60;draw();}}
 range.addEventListener('input',()=>seek(Number(range.value)));
 chart.addEventListener('click',e=>{const r=chart.getBoundingClientRect(),x=(e.clientX-r.left)*1200/r.width;seek(Math.max(0,Math.min(ids.length-1,Math.round((x-70)/1100*(ids.length-1)))));});
 for(const el of [select,view,orbit])el.addEventListener('input',draw);
 for(const event of ['timeupdate','seeked','loadedmetadata'])video.addEventListener(event,draw);
 if(video.requestVideoFrameCallback){const tick=()=>{draw();video.requestVideoFrameCallback(tick);};video.requestVideoFrameCallback(tick);}
 draw();
}
let printState=[];window.addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('.print-frames')].map(e=>[e,e.open]);printState.forEach(([e])=>e.open=true);});window.addEventListener('afterprint',()=>printState.forEach(([e,open])=>e.open=open));
const table=document.querySelector('#controlled-table');if(table)for(const button of table.querySelectorAll('button'))button.addEventListener('click',()=>{const col=Number(button.dataset.column),rows=[...table.tBodies[0].rows],asc=button.dataset.direction!=='asc';rows.sort((a,b)=>(Number(a.cells[col].textContent)-Number(b.cells[col].textContent))*(asc?1:-1));rows.forEach(r=>table.tBodies[0].append(r));button.dataset.direction=asc?'asc':'desc';});
}
if(typeof document!=='undefined')initDemoInteractions();
if(typeof module!=='undefined')module.exports={frameAt,meanError,firstTime,boxCorners};
