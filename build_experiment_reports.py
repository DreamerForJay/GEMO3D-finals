"""Build report tables and evidence images from the controlled suite."""
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from evaluate_controlled_suite import write_csv,assign,objs
from render_sequence_video import draw_box
from run_controlled_suite import make_models,SOURCE,DATA,ROOT


def main():
    out=ROOT/'results';run=out/'controlled_20261116'
    manifest=json.loads((run/'manifest.json').read_text())
    metrics=list(csv.DictReader((run/'metrics.csv').open()))
    allrows={r['method']:r for r in metrics if r['scope']=='all_matched'}
    sys.path.insert(0,str(SOURCE))
    from submodule.compensation import _load_models,_predict_rank_ratio,_angle_for_rank_ratio_grid
    m=_load_models(str(SOURCE/'comp/sed_rank_ratio_linear_model.pkl'));models,stats=make_models(m)
    comparison=[]
    for name,key in [('Rank-1','rank1'),('Rank-2','rank2'),('Rank-3','rank3'),('Full-rank','full'),('2D bilinear table','full'),('Degree-2 grid','poly2'),('Degree-2 direct','poly2_direct')]:
        method='D' if key=='rank1' else key;r=allrows[method]
        gridkey='poly2' if key=='poly2_direct' else key
        def lookup(angle,z):
            if key!='poly2_direct':return _predict_rank_ratio(angle,z,models[key])
            a=2*_angle_for_rank_ratio_grid(angle,m['angle_grid'])/180-1
            dg=m['depth_grid'];d=2*(np.clip(z,dg[0],dg[-1])-dg[0])/(dg[-1]-dg[0])-1
            return float(np.dot(stats['poly2_coefficients'],[1,a,d,a*a,a*d,d*d]))
        queries=[(float(i%181),3.2+(i%100)*.36) for i in range(1000)]
        for q in queries[:20]:lookup(*q)
        samples=[]
        for _ in range(5):
            start=time.perf_counter()
            for q in queries:lookup(*q)
            samples.append((time.perf_counter()-start)*1e6/len(queries))
        k=int(key[-1]) if key.startswith('rank') else None
        comparison.append(dict(method=name,n=int(r['n']),ratio_grid_rmse=stats[gridkey]['grid_rmse'],depth_rmse=float(r['depth_rmse']),depth_mae=float(r['depth_mae']),center_error=float(r['center_error']),bev_iou=float(r['bev_iou']),stored_runtime_values=10 if key=='poly2_direct' else 7200+170,factorized_values_including_axes=90+170*k+170 if k else 10 if key=='poly2_direct' else 10 if key=='poly2' else 7370,cpu_ratio_lookup_us_median=float(np.median(samples))))
    write_csv(out/'compensation_compare.csv',comparison)
    (out/'compensation_compare.md').write_text('''# 補償比較：199張 Lincoln CARLA 新實驗

只替換 D 的比例模型，YOLO、EgoNet、尺寸、無道路平面／無tightfit均固定。匹配165筆，非舊論文165清單。全精度見 compensation_compare.csv。

原模型保存90×80原始比例網格與逐角度均值b。以R−b做SVD；b+U1Σ1V1與原Rank-1網格最大差2.22e-16。Rank-2／3依相同分解重建。訓練網格不含本次CARLA標註；全域比例與角度查表也只由該網格計算。

Full-rank與2D雙線性查表在這個實作是同一方法，使用相同原網格＋RegularGridInterpolator，不能假裝成兩個獨立驗證。二次曲面使用正規化角度／深度的[1,a,z,a²,az,z²]六係數擬合訓練網格，先取樣回網格再依相同雙線性插值，報為Degree-2 grid，不冒稱直接多項式評估。另跑Degree-2 direct，直接以六係數及四個軸端點計算，沒有網格查表；兩者分開回報。

CPU時間：每方法20次暖機、5輪各1000次查詢的中位數，含每次建RegularGridInterpolator；共享CPU環境，非GPU或整體FPS。為隔離比例精度，除Degree-2 direct外其餘方法目前都以完整網格執行，因此runtime儲存值都是7370；factorized欄只是可用因子表示的理論值，尚未實作壓縮部署。

能量ηk=Σ前k奇異值²/Σ全部奇異值²；必須分清原始R與去逐行均值後R−b。此模型的數值與論文其他車型表不能互換。

'''+json.dumps(stats['energy'],indent=2)+'\n')
    # Recompute current historical files and compare against the stale 165-row summary.
    source=Path('/home/e114/mono3d_comparison_fr/pairs')
    historical={p.stem:list(csv.DictReader(p.open(encoding='utf-8-sig'))) for p in source.glob('*_pairs.csv')}
    sets=[{(r['image_id'],r['gt_id']) for r in rows} for rows in historical.values()]
    common=set.intersection(*sets)
    indexed={name:{(r['image_id'],r['gt_id']):r for r in rows} for name,rows in historical.items()}
    fields=['gt_x','gt_y','gt_z','gt_H','gt_W','gt_L']
    consistent=[]
    for key in common:
        vectors=[[float(rows[key][k]) for k in fields] for rows in indexed.values()]
        if all(np.allclose(vectors[0],v,rtol=0,atol=1e-6) for v in vectors[1:]):consistent.append(key)
    historical_summary=[]
    for method,rows in historical.items():
        rr=[r for r in rows if (r['image_id'],r['gt_id']) in common]
        d=np.array([float(r['depth_err_m']) for r in rr])
        historical_summary.append(dict(method=method,current_pairs=len(rows),common_id_only=len(rr),verified_common_gt=len(consistent),depth_rmse=float(np.sqrt(np.mean(d*d))),mean_bev_iou=float(np.mean([float(r['iou_bev']) for r in rr]))))
    write_csv(out/'historical_pair_reaudit.csv',historical_summary)
    old=Path('/home/e114/mono3d_comparison_fr/plots/compare_all/compare_overall_summary_common.csv')
    oldrows=list(csv.DictReader(old.open(encoding='utf-8-sig')))
    selected=[r for r in oldrows if r['metric'] in ['depth_error','center_3d_error','bev_iou']]
    write_csv(out/'historical_165_summary_unverified.csv',selected)
    vals={r['model']:float(r['mean']) for r in oldrows if r['metric']=='bev_iou'}
    (out/'historical_165_audit.md').write_text(f'''# 舊165樣本摘要查核

舊摘要保留的BEV均值為MonoDETR={vals['MonoDETR']!r}、GEMO3D={vals['GEMO3D']!r}；相對增加={(vals['GEMO3D']/vals['MonoDETR']-1)*100!r}%。這比0.70→0.82的四捨五入計算更精確，但仍只是歷史摘要，不能視為本次重新驗證。

目前四份pairs各有{[len(x) for x in historical.values()]}筆，僅ID交集{len(common)}筆，不是165；核對GT位置與尺寸後一致的共同GT為{len(consistent)}筆。相同000000，GEMO3D GT深度33.135363m、尺寸H/W/L=1.535/1.882/5.008，其他三份為35.777483m、1.475/1.97/3.806，屬不同資料來源，不能以相同ID視為同物件。部分IoU在0.3–0.5。摘要與現存逐筆資料版本不一致，完整逐筆165來源待補。原摘要複製於 historical_165_summary_unverified.csv，現存pairs各自的ID交集子集統計於historical_pair_reaudit.csv，這些均值**不能作跨方法比較**，verified_common_gt欄記錄真正一致GT數。不混用二者。

舊摘要SHA256：{hashlib.sha256(old.read_bytes()).hexdigest()}。

本次Lincoln四方法在IoU≥0.5下共同匹配僅20筆；控制實驗15種設定共同165筆只是數量巧合，資料集與舊論文清單不同。
''')
    make_cases(run,out,allrows)


def make_cases(run,out,metrics):
    dest=out/'failure_cases';dest.mkdir(exist_ok=True)
    predictions=json.loads((run/'predictions.json').read_text())
    pairs=list(csv.DictReader((run/'pairs.csv').open()));fpairs=[r for r in pairs if r['method']=='F']
    tight=list(csv.DictReader((out/'tightfit_ablation.csv').open()))
    bad=[r for r in tight if r['iou_up_center_worse']=='True']
    bad.sort(key=lambda r:float(r['center_error_after'])-float(r['center_error_before']),reverse=True)
    chosen=[]
    far=sorted([r for r in fpairs if float(r['gt_z'])>30],key=lambda r:abs(float(r['depth_error'])),reverse=True)[:3]
    for r in far:chosen.append(('far',r['frame'],'F',DATA/'training',int(r['gt_id'])))
    for r in bad[:3]:chosen.append(('tightfit_iou_up_3d_worse',r['frame'],'F',DATA/'training',int(r['gt_id'])))
    wrong=sorted([r for r in pairs if r['method']=='wrong_suv'],key=lambda r:float(r['center_error']),reverse=True)[:3]
    for r in wrong:chosen.append(('forced_wrong_suv',r['frame'],'wrong_suv',DATA/'training',int(r['gt_id'])))
    kdata=Path('/home/e114/KITTI_ROOT/training');ids=(out/'kitti_demo_frames.txt').read_text().split()
    for category,col in [('occluded',2),('truncated',1)]:
        found=[]
        for fid in ids:
            cars=[v.split() for v in (kdata/'label_2'/(fid+'.txt')).read_text().splitlines() if v.split()[0]=='Car']
            for gi,v in enumerate(cars):
                if float(v[col])>0:found.append((float(v[col]),fid,gi))
        # Select distinct frames by annotation severity, not prediction error.
        seen=set()
        for severity,fid,gi in sorted(found,reverse=True):
            if fid in seen:continue
            chosen.append((category,fid,'historical_kitti',kdata,gi));seen.add(fid)
            if len(seen)==3:break
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    records=[]
    for category,fid,method,data,gi in chosen:
        img=cv2.imread(str(data/'image_2'/(fid+'.png')))
        gt=[g for g in objs(str(data/'label_2'/(fid+'.txt'))) if g['t']=='Car']
        pred=([p for p in objs(str(out/'predictions/kitti'/(fid+'.txt'))) if p['t']=='Car'] if method=='historical_kitti' else predictions[method][fid])
        P=np.array([float(v) for line in (data/'calib'/(fid+'.txt')).read_text().splitlines() if line.startswith('P2:') for v in line.split()[1:]]).reshape(3,4)
        matched=next(((pi,iou) for pi,gj,iou in assign(pred,gt) if gj==gi),None)
        draw_box(img,gt[gi],P,(0,180,255))
        err=None
        if matched:
            p=pred[matched[0]];draw_box(img,p,P,(255,150,0));err=p['z']-gt[gi]['z']
        canvas=Image.new('RGB',(img.shape[1],img.shape[0]+85),'white');canvas.paste(Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)),(0,85));d=ImageDraw.Draw(canvas)
        d.text((10,6),f'{category} | {method} | frame {fid} | GT {gi}',font=font,fill='black')
        d.text((10,32),f'GT depth {gt[gi]["z"]:.3f} m | '+(f'depth error {err:+.3f} m' if err is not None else 'UNMATCHED at 2D IoU >= 0.5'),font=font,fill='black')
        d.text((10,58),'Orange: GT | Blue: matched prediction | selection rule in cases.csv',font=font,fill='black')
        name=f'{category}_{fid}.jpg';canvas.save(dest/name,quality=92)
        if category=='tightfit_iou_up_3d_worse':
            before=cv2.imread(str(data/'image_2'/(fid+'.png')))
            bp=predictions['F_no_tightfit'][fid]
            bm=next((pi for pi,gj,iou in assign(bp,gt) if gj==gi),None)
            assert bm is not None
            draw_box(before,gt[gi],P,(0,180,255));draw_box(before,bp[bm],P,(255,150,0))
            panel=Image.new('RGB',(img.shape[1]*2,img.shape[0]+85),'white')
            panel.paste(Image.fromarray(cv2.cvtColor(before,cv2.COLOR_BGR2RGB)),(0,85));panel.paste(Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)),(img.shape[1],85))
            dd=ImageDraw.Draw(panel)
            values=next(r for r in tight if r['frame']==fid and int(r['gt_id'])==gi)
            for x,tag in [(0,'before'),(img.shape[1],'after')]:
                dd.text((x+10,8),f'{fid} | tightfit {tag} | Orange GT, Blue prediction',font=font,fill='black')
                dd.text((x+10,35),f"3D center error {float(values['center_error_'+tag]):.4f} m | projection IoU {float(values['projected_det_iou_'+tag]):.4f}",font=font,fill='black')
            panel.save(dest/f'tightfit_compare_{fid}.jpg',quality=92)
        records.append(dict(category=category,frame=fid,method=method,gt_id=gi,gt_z=gt[gi]['z'],depth_error=err,matched=matched is not None,image=name,source_image_sha256=hashlib.sha256((data/'image_2'/(fid+'.png')).read_bytes()).hexdigest()))
    write_csv(dest/'cases.csv',records)
    (dest/'README.md').write_text('''# 失敗案例

遠距取新CARLA完整流程中GT>30m的最大深度誤差3張；tightfit取2D投影IoU升但中心誤差增加最大的3張；車型敏感度為強制SUV配置的最大中心誤差3張，這是人為干預，**不是觀測到分類器真的誤判**。

CARLA本序列所有標註occlusion/truncation皆0，不能虛構遮擋案例。遮擋／截斷改用既有KITTI展示30張中的標註，依嚴重度取不同影格各3張。KITTI為歷史推論，原權重／完整參數未核實；僅供失敗展示，不納入CARLA消融。未配對以UNMATCHED呈現，不填造深度誤差。

全部tightfit前後數值在../tightfit_ablation.csv；所有配對含較差結果在../controlled_20261116/pairs.csv。
''')

if __name__=='__main__':main()
