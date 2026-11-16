"""Controlled CARLA ablations. Does not modify the GEMO3D source or historical outputs."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import numpy as np

SOURCE = Path('/home/e114/Desktop/mono3d/GEMO3D')
DATA = Path('/home/e114/KITTI_ROOT/sed_lincoln_fr_T1R8/data/KITTIDataset_Carla')
ROOT = Path(__file__).resolve().parent


def make_models(model):
    R = np.asarray(model['R_original_grid'])
    b = np.asarray(model['b_theta'])
    u, s, vt = np.linalg.svd(R-b[:, None], full_matrices=False)
    assert np.max(abs(b[:,None]+(u[:,:1]*s[:1])@vt[:1]-model['R_reconstructed_grid'])) < 1e-12
    grids = {'global': np.full_like(R,R.mean()), 'angle': np.repeat(R.mean(axis=1)[:,None],R.shape[1],axis=1), 'rank1': model['R_reconstructed_grid'], 'full': R}
    for k in (2,3): grids[f'rank{k}'] = b[:,None]+(u[:,:k]*s[:k])@vt[:k]
    # Degree-2 surface, fit to TRAINING grid only; no CARLA GT involved.
    a,z=np.meshgrid(np.linspace(-1,1,R.shape[0]),np.linspace(-1,1,R.shape[1]),indexing='ij')
    X=np.stack([np.ones_like(a),a,z,a*a,a*z,z*z],axis=-1)
    coef=np.linalg.lstsq(X.reshape(-1,6),R.ravel(),rcond=None)[0]
    grids['poly2'] = X@coef
    models={}
    stats={}
    for name,g in grids.items():
        m=copy.copy(model);m['R_reconstructed_grid']=g
        models[name]=m
        stats[name]={'grid_rmse':float(np.sqrt(np.mean((g-R)**2))), 'runtime_grid_entries':int(g.size), 'runtime_grid_bytes':int(g.nbytes)}
    stats['energy']={'uncentered':(np.cumsum(np.linalg.svd(R,compute_uv=False)**2)/np.sum(np.linalg.svd(R,compute_uv=False)**2)).tolist()[:3], 'row_centered':(np.cumsum(s*s)/np.sum(s*s)).tolist()[:3]}
    stats['poly2_coefficients']=coef.tolist()
    return models,stats


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--variants',default='A,B,C,D,E,F,F_no_tightfit,rank2,rank3,full,poly2,wrong_suv,wrong_compact,F_cli_dims')
    args=ap.parse_args();out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(SOURCE))
    os.environ['EGONET_ROOT']=str(SOURCE/'EgoNet-master')
    os.environ['EGONET_CFG']=str(SOURCE/'EgoNet-master/configs/KITTI_inference:test_submission.yml')
    import torch
    from submodule import cli, pipeline, config
    from submodule.compensation import _load_models
    model_paths={k:SOURCE/'comp'/v for k,v in {'sedan':'sed_rank_ratio_linear_model.pkl','suv':'suv2_rank_ratio_linear_model.pkl','compact':'com_rank_ratio_linear_model.pkl'}.items()}
    models,stats=make_models(_load_models(str(model_paths['sedan'])))
    all_models={k:_load_models(str(v)) for k,v in model_paths.items()}
    base=cli.build_arg_parser().parse_args(['--kitti_root',str(DATA),'--split','val','--out_dir',str(out),'--yolo_weights',str(SOURCE/'yolo11n.pt'),'--egonet_weights',str(SOURCE/'weights/egonet'),'--dims_source','fixed','--fixed_dims_hwl','1.511,2.128,4.902','--height_m','1.511','--force_veh_type','sedan','--conf','0.25','--imgsz','1280','--device','cuda:0','--half'])
    runtime=cli.build_runtime_models(base)
    cli.build_runtime_models=lambda args:runtime
    original=pipeline.infer_one_image
    original_dims=pipeline.resolve_fixed_dims_hwl_for_k
    original_comp=pipeline._predict_compensation
    specs={
      'A':('none',False,False,False,'sedan'), 'B':('global',False,False,False,'sedan'),
      'C':('angle',False,False,False,'sedan'), 'D':('rank1',False,False,False,'sedan'),
      'E':('rank1',True,False,False,'sedan'), 'F':('rank1',True,True,True,'sedan'),
      'F_no_tightfit':('rank1',True,True,False,'sedan'),
      **{k:(k,False,False,False,'sedan') for k in ('rank2','rank3','full','poly2')},
      'wrong_suv':('suv',True,True,True,'suv'), 'wrong_compact':('compact',True,True,True,'compact'),
      'F_cli_dims':('rank1',True,True,True,'sedan'), 'poly2_direct':('poly2',False,False,False,'sedan')}
    ids=(DATA/'ImageSets/val.txt').read_text().split()
    assert len(ids)==199 and len(set(ids))==199
    hashes={}
    for p in [*model_paths.values(),SOURCE/'submodule/pipeline.py',SOURCE/'submodule/config.py',SOURCE/'submodule/geometry.py',SOURCE/'submodule/compensation.py',SOURCE/'yolo11n.pt',*sorted((SOURCE/'weights/egonet').glob('*')),DATA/'ImageSets/val.txt']:
        if p.is_file():hashes[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    manifest=dict(dataset=str(DATA),frames=ids,torch=torch.__version__,gpu=torch.cuda.get_device_name(0),shared_gpu=True,source_sha256=hashes,model_stats=stats,variants={})
    for name in args.variants.split(','):
        dest=out/name
        if dest.exists(): raise FileExistsError(f'Refuse overwrite {dest}')
        mode,ground,projection,tight,vehicle=specs[name]
        pipeline._predict_compensation=original_comp
        if name=='poly2_direct':
            from submodule.compensation import _angle_for_rank_ratio_grid
            def direct(yaw_deg,model,z_raw=None):
                angle=_angle_for_rank_ratio_grid(yaw_deg,model['angle_grid'])
                a=2*(angle-model['angle_grid'][0])/(model['angle_grid'][-1]-model['angle_grid'][0])-1
                dz=model['depth_grid'];z=2*(np.clip(z_raw,dz[0],dz[-1])-dz[0])/(dz[-1]-dz[0])-1
                ratio=float(np.dot(stats['poly2_coefficients'],[1,a,z,a*a,a*z,z*z]))
                return float(z_raw*(1-ratio))
            pipeline._predict_compensation=direct
        model=None if mode=='none' else all_models[mode] if mode in all_models else models[mode]
        cli.build_vehicle_compensation_models=lambda args:(None,{k:model if k==vehicle else None for k in ('sedan','suv','compact','van')})
        def controlled(**kwargs):
            # No GT labels or debug side-camera images enter inference. Camera extrinsics only in E/F.
            kwargs.update(label_path=None,top_bev_img_path=None,fr_iou_img_path=None,side_iou_img_path=None)
            if not ground: kwargs['meta_path']=None
            return original(**kwargs)
        cli.infer_one_image=controlled
        pipeline.resolve_fixed_dims_hwl_for_k=(lambda pred_by_k,k,default_hwl:default_hwl) if name=='F_cli_dims' else original_dims
        run=copy.copy(base);run.out_dir=str(dest);run.pred_meta_csv=str(dest/'pred_meta.csv');run.force_veh_type=vehicle
        run.proj_center_source='pred_reproj_geom_x' if projection else 'bbox_bottom';run.proj_refine_iters=3 if projection else 0;run.tightfit=tight
        if vehicle!='sedan': run.height_m=config.VT5_FIXED_DIMS_HWL[vehicle][0]
        torch.cuda.synchronize();start=time.perf_counter();cli.run(run);torch.cuda.synchronize()
        manifest['variants'][name]=dict(mode=mode,ground=ground,projection=projection,tightfit=tight,vehicle=vehicle,height_m=run.height_m,effective_dims_hwl=list(base.fixed_dims_hwl.split(',')) if name=='F_cli_dims' else config.VT5_FIXED_DIMS_HWL[vehicle],wall_seconds=time.perf_counter()-start,command_args=vars(run))
        (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print('COMPLETED_VARIANT',name,flush=True)

if __name__=='__main__':main()
