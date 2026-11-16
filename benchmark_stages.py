"""Instrument an immutable pipeline in memory; report exclusive stages and unassigned overhead."""
import ast
import argparse
import contextlib
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from collections import defaultdict

SOURCE=Path('/home/e114/Desktop/mono3d/GEMO3D')
ROOT=Path(__file__).resolve().parent

class StageTimer:
    def __init__(self,sync):self.sync=sync;self.values=defaultdict(float);self.stack=[]
    @contextlib.contextmanager
    def stage(self,name):
        self.sync();entry=[time.perf_counter(),0.];self.stack.append(entry)
        try:yield
        finally:
            self.sync();elapsed=time.perf_counter()-entry[0];self.stack.pop();self.values[name]+=elapsed-entry[1]
            if self.stack:self.stack[-1][1]+=elapsed
    def wrap(self,name,fn):
        def wrapped(*a,**kw):
            with self.stage(name):return fn(*a,**kw)
        return wrapped

def instrument(pipeline,timer):
    original=pipeline.infer_one_image
    source=inspect.getsource(original);tree=ast.parse(source)
    # Version-specific line boundaries; guard against unreviewed source changes.
    path=SOURCE/'submodule/pipeline.py'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == '455d9dcac8ae4da61a6c570fe246a8486665c41f6b6e601066852fa564e6f52e', 'Pipeline version changed; review timing boundaries'
    start=inspect.getsourcelines(original)[1]
    def absolute(node):return node.lineno+start-1
    assert any(isinstance(n,ast.For) and absolute(n)==220 for n in tree.body[0].body)
    def group(stmts,ranges):
        result=[];bucket=[];last=None
        def flush():
            if not bucket:return
            if last:
                ctx=ast.Call(func=ast.Attribute(value=ast.Name(id='_stage_timer',ctx=ast.Load()),attr='stage',ctx=ast.Load()),args=[ast.Constant(last)],keywords=[])
                result.append(ast.copy_location(ast.With(items=[ast.withitem(context_expr=ctx)],body=bucket.copy()),bucket[0]))
            else:result.extend(bucket)
            bucket.clear()
        for n in stmts:
            category=next((name for lo,hi,name in ranges if lo<=absolute(n)<=hi),None)
            if category!=last:flush();last=category
            bucket.append(n)
        flush();return result
    fn=tree.body[0]
    for node in fn.body:
        if isinstance(node,ast.For) and absolute(node)==220:
            node.body=group(node.body,[(283,306,'compensation'),(307,322,'projection'),(368,638,'projection')])
    fn.body=group(fn.body,[(96,127,'read'),(129,153,'yolo'),(178,187,'egonet'),(724,729,'write')])
    namespace=dict(pipeline.__dict__);namespace['_stage_timer']=timer
    for name in ('solve_translation_tightfit','solve_translation_metric_plane_support_xz'):
        namespace[name]=timer.wrap('tightfit',namespace[name])
    namespace['_predict_compensation']=timer.wrap('compensation',namespace['_predict_compensation'])
    exec(compile(ast.fix_missing_locations(tree),str(path),'exec'),namespace)
    return namespace['infer_one_image']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--production-io',action='store_true');opts=ap.parse_args()
    sys.path.insert(0,str(SOURCE));os.environ['EGONET_ROOT']=str(SOURCE/'EgoNet-master');os.environ['EGONET_CFG']=str(SOURCE/'EgoNet-master/configs/KITTI_inference:test_submission.yml')
    import torch
    from submodule import cli,pipeline
    output=ROOT/('benchmark_output/stages_production_io_20261116' if opts.production_io else 'benchmark_output/stages_20261116');output.mkdir(parents=True,exist_ok=False)
    smi=subprocess.run(['nvidia-smi'],capture_output=True,text=True,check=True).stdout
    timer=StageTimer(torch.cuda.synchronize);measured=instrument(pipeline,timer)
    # Reuse established 100-frame dataset, same source and effective dimensions as historical timing.
    results=dict(source_sha256=hashlib.sha256((SOURCE/'submodule/pipeline.py').read_bytes()).hexdigest(),gpu=torch.cuda.get_device_name(0),torch=torch.__version__,cuda=torch.version.cuda,shared_gpu=True,nvidia_smi_before=smi,settings={})
    settings=[('production_io_fp16',True,True)] if opts.production_io else [('reference_fp32',False,True),('no_tightfit_fp32',False,False),('fp16',True,True)]
    destination=ROOT/'results'/('timing_production_io.json' if opts.production_io else 'timing_breakdown.json')
    for setting,half,tight in settings:
        dest=output/setting;records=[];verified=False
        def timed(**kwargs):
            nonlocal verified
            if not verified:
                warm=dict(kwargs,pred_meta_rows=None)
                pipeline.infer_one_image(**warm)
                path=kwargs['out_pred_data_dir']/(kwargs['img_path'].stem+'.txt');plain=path.read_bytes()
                if opts.production_io:warm.update(top_bev_img_path=None,fr_iou_img_path=None,side_iou_img_path=None)
                measured(**warm);assert plain==path.read_bytes(),'Instrumentation changed predictions'
                # Five additional same-image warmups; equivalence runs also warmed models, explicitly recorded.
                for _ in range(5):measured(**warm)
                verified=True
            if opts.production_io:kwargs.update(top_bev_img_path=None,fr_iou_img_path=None,side_iou_img_path=None)
            timer.values.clear();torch.cuda.synchronize();begin=time.perf_counter();measured(**kwargs);torch.cuda.synchronize();total=time.perf_counter()-begin
            stages={k:1000*v for k,v in timer.values.items()};other=1000*total-sum(stages.values())
            assert other>=-1e-6
            records.append(dict(frame=kwargs['img_path'].stem,total_ms=1000*total,other_ms=other,**stages))
        cli.infer_one_image=timed
        argv=['--kitti_root',str(ROOT/'benchmark_dataset'),'--split','val','--out_dir',str(dest),'--yolo_weights',str(SOURCE/'yolo11n.pt'),'--egonet_weights',str(SOURCE/'weights/egonet'),'--dims_source','fixed','--fixed_dims_hwl','1.511,2.128,4.902','--height_m','1.511','--force_veh_type','sedan','--vt_comp_pkl_map',f'compact=-,sedan={SOURCE}/comp/sed_rank_ratio_linear_model.pkl,suv=-,van=-','--proj_center_source','pred_reproj_geom_x','--proj_refine_iters','3','--tightfit_max_nfev','15','--tightfit_k','50','--conf','0.25','--imgsz','1280','--device','cuda:0','--pred_meta_csv',str(dest/'pred_meta.csv')]
        if half:argv+=['--half']
        if tight:argv+=['--tightfit']
        begin=time.perf_counter();cli.main(argv);wall=time.perf_counter()-begin
        assert len(records)==100
        keys=sorted(set().union(*(r.keys() for r in records))-{'frame'})
        means={k:sum(r.get(k,0) for r in records)/100 for k in keys}
        results['settings'][setting]=dict(command=argv,means_ms=means,fps=1000/means['total_ms'],wall_seconds_including_setup_and_7_extra_inferences=wall,warmup=5,equivalence_inferences=2,predictions_byte_identical=True,samples=records)
        destination.write_text(json.dumps(results,indent=2)+'\n')
        print('COMPLETED_TIMING',setting,means,flush=True)
    results['nvidia_smi_after']=subprocess.run(['nvidia-smi'],capture_output=True,text=True,check=True).stdout
    destination.write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
