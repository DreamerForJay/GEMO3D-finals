"""All-prediction counts and class-aware, one-to-one IoU>=.5 metrics; no depth filtering."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import cv2
import numpy as np
from render_sequence_video import objs, corners

ROOT=Path(__file__).resolve().parent

def iou2d(a,b):
    area=lambda x:max(0,x[2]-x[0])*max(0,x[3]-x[1])
    inter=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    union=area(a)+area(b)-inter
    return inter/union if union else 0.

def bev_iou(a,b):
    pa=np.ascontiguousarray(corners(a)[[0,2],:4].T,dtype=np.float32)
    pb=np.ascontiguousarray(corners(b)[[0,2],:4].T,dtype=np.float32)
    inter,_=cv2.intersectConvexConvex(pa,pb)
    union=a['l']*a['w']+b['l']*b['w']-inter
    return float(np.clip(inter/union if union>0 else 0,0,1))

def assign(pred,gt,threshold=.5):
    candidates=sorted([(iou2d(p['box'],g['box']),pi,gi) for pi,p in enumerate(pred) for gi,g in enumerate(gt) if p['t'].lower()==g['t'].lower()],reverse=True)
    usedp=set();usedg=set();matches=[]
    for iou,pi,gi in candidates:
        if iou>=threshold and pi not in usedp and gi not in usedg:
            matches.append((pi,gi,iou));usedp.add(pi);usedg.add(gi)
    return matches

def project_box(o,P):
    c=corners(o)
    if np.any(c[2]<=0):return None
    q=P@np.vstack([c,np.ones(8)]);q=q[:2]/q[2]
    return [float(q[0].min()),float(q[1].min()),float(q[0].max()),float(q[1].max())]

def evaluate(directory,data,ids,method):
    pairs=[];npred=ngt=0;hashes={};missing=[];prediction_dump={}
    for fid in ids:
        pp=directory/(fid+'.txt');gp=data/'label_2'/(fid+'.txt')
        if not pp.exists(): missing.append(fid)
        else:hashes[str(pp)]=hashlib.sha256(pp.read_bytes()).hexdigest()
        pred=[x for x in objs(str(pp)) if x['t']=='Car'];gt=[x for x in objs(str(gp)) if x['t']=='Car']
        prediction_dump[fid]=pred
        npred+=len(pred);ngt+=len(gt)
        P=np.array([float(v) for line in (data/'calib'/(fid+'.txt')).read_text().splitlines() if line.startswith('P2:') for v in line.split()[1:]]).reshape(3,4)
        for pi,gi,iou in assign(pred,gt):
            p,g=pred[pi],gt[gi];delta=p['z']-g['z']
            center=math.sqrt((p['x']-g['x'])**2+(p['y']-p['h']/2-g['y']+g['h']/2)**2+delta**2)
            bottom=math.sqrt((p['x']-g['x'])**2+(p['y']-g['y'])**2+delta**2)
            projected=project_box(p,P)
            pairs.append(dict(method=method,frame=fid,gt_id=gi,pred_id=pi,gt_z=g['z'],pred_z=p['z'],depth_error=delta,center_error=center,bottom_center_error=bottom,bev_iou=bev_iou(p,g),yaw_error_deg=abs(math.degrees(math.atan2(math.sin(p['ry']-g['ry']),math.cos(p['ry']-g['ry'])))),det_iou=iou,projected_det_iou=iou2d(projected,p['box']) if projected else 0))
    counts=dict(method=method,frames=len(ids),gt=ngt,predictions=npred,matches=len(pairs),false_positives=npred-len(pairs),false_negatives=ngt-len(pairs),precision=len(pairs)/npred if npred else 0,recall=len(pairs)/ngt if ngt else 0,missing_prediction_files=len(missing))
    return pairs,counts,hashes,prediction_dump

def aggregate(rows,method,scope):
    d=np.array([r['depth_error'] for r in rows]);n=len(d)
    out=dict(method=method,scope=scope,n=n)
    out.update(depth_rmse=float(np.sqrt(np.mean(d*d))) if n else None,depth_mae=float(np.mean(abs(d))) if n else None,depth_bias=float(np.mean(d)) if n else None)
    for k in ['center_error','bottom_center_error','bev_iou','yaw_error_deg','projected_det_iou']:
        out[k]=float(np.mean([r[k] for r in rows])) if n else None
    return out

def write_csv(path,rows):
    if not rows:raise ValueError(f'Empty report {path}')
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--output',default='results/controlled_20261116');a=ap.parse_args()
    run=Path(a.run);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((run/'manifest.json').read_text());data=Path(manifest['dataset'])/'training';ids=manifest['frames']
    sources={name:run/name/'pred/data' for name in manifest['variants']}
    extra=ROOT/'benchmark_output/poly_direct_20261116'
    if (extra/'manifest.json').exists():
        extra_manifest=json.loads((extra/'manifest.json').read_text())
        assert extra_manifest['frames']==ids
        for name,spec in extra_manifest['variants'].items():
            sources[name]=extra/name/'pred/data';manifest['variants'][name]=spec
    base=Path('/home/e114/mono3d_predictions/sed_lincoln_fr_T1R8')
    for name in ['monodetr','monodgp','monoamnet']:sources['historical_'+name]=base/name/'data'
    by_method={};counts=[];hashes={};preds={}
    for name,d in sources.items():
        pairs,count,h,pred=evaluate(d,data,ids,name);by_method[name]=pairs;counts.append(count);hashes.update(h);preds[name]=pred
        if name in manifest['variants']:assert count['missing_prediction_files']==0
    sets={name:{(r['frame'],r['gt_id']) for r in rows} for name,rows in by_method.items()}
    controlled=list(manifest['variants']);common=set.intersection(*(sets[n] for n in controlled))
    four=['F','historical_monodetr','historical_monodgp','historical_monoamnet'];fourcommon=set.intersection(*(sets[n] for n in four))
    summaries=[]
    for name,rows in by_method.items():
        summaries.append(aggregate(rows,name,'all_matched'))
        if name in controlled:summaries.append(aggregate([r for r in rows if (r['frame'],r['gt_id']) in common],name,'controlled_common'))
        if name in four:summaries.append(aggregate([r for r in rows if (r['frame'],r['gt_id']) in fourcommon],name,'four_methods_common'))
    write_csv(out/'metrics.csv',summaries);write_csv(ROOT/'results/detection_stats.csv',counts)
    write_csv(out/'pairs.csv',[r for rows in by_method.values() for r in rows])
    write_csv(ROOT/'results/ablation.csv',[r for r in summaries if r['method'] in ['A','B','C','D','E','F'] and r['scope']!='four_methods_common'])
    write_csv(ROOT/'results/vehtype_sensitivity.csv',[r for r in summaries if r['method'] in ['F','wrong_suv','wrong_compact','F_cli_dims'] and r['scope']!='four_methods_common'])
    before={(r['frame'],r['gt_id']):r for r in by_method['F_no_tightfit']};after={(r['frame'],r['gt_id']):r for r in by_method['F']}
    tight=[]
    for key in sorted(before.keys()&after.keys()):
        b,f=before[key],after[key];row=dict(frame=key[0],gt_id=key[1])
        for k in ['depth_error','center_error','bev_iou','projected_det_iou']:row[k+'_before']=b[k];row[k+'_after']=f[k]
        row['iou_up_center_worse']=f['projected_det_iou']>b['projected_det_iou'] and f['center_error']>b['center_error'];tight.append(row)
    write_csv(ROOT/'results/tightfit_ablation.csv',tight)
    manifest.update(prediction_sha256=hashes,controlled_common=sorted(common),four_methods_common=sorted(fourcommon))
    inputs=[data/d/(fid+ext) for fid in ids for d,ext in [('image_2','.png'),('label_2','.txt'),('calib','.txt'),('meta','.json')]]
    manifest['dataset_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    reference={f:[o['box'] for o in pp] for f,pp in preds['A'].items()}
    for name in controlled:assert reference=={f:[o['box'] for o in pp] for f,pp in preds[name].items()},name
    manifest['detection_boxes_identical_all_variants']=True
    prior=json.loads((ROOT/'results/input_manifest.json').read_text())
    shared=[r for r in prior if r['path'] in manifest['dataset_sha256']]
    different=[r['path'] for r in shared if r['sha256']!=manifest['dataset_sha256'][r['path']]]
    assert not different
    manifest['prior_input_manifest_comparison']={'files':len(shared),'different':different}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'predictions.json').write_text(json.dumps(preds,separators=(',',':'))+'\n')
    print(json.dumps({'controlled_common':len(common),'four_common':len(fourcommon),'counts':counts},indent=2))

if __name__=='__main__':main()
