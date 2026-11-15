"""Time 100 image pipelines, including I/O, after five same-image warmups."""
import argparse
import json
from pathlib import Path
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    args, forwarded = parser.parse_known_args()
    if forwarded[:1] == ['--']: forwarded = forwarded[1:]
    sys.path.insert(0, str(Path(args.source).resolve()))
    import torch
    from submodule import cli
    original = cli.infer_one_image
    samples = []
    def timed(**kwargs):
        if not samples:
            warm = dict(kwargs, pred_meta_rows=None)
            for _ in range(5): original(**warm)
        torch.cuda.synchronize()
        start = time.perf_counter()
        result = original(**kwargs)
        torch.cuda.synchronize()
        samples.append({'frame': kwargs['img_path'].stem, 'ms': (time.perf_counter()-start)*1000})
        return result
    cli.infer_one_image = timed
    started = time.perf_counter()
    cli.main(forwarded)
    wall = time.perf_counter()-started
    if len(samples) != 100: raise RuntimeError(f'Expected 100 frames, got {len(samples)}')
    mean = sum(x['ms'] for x in samples)/len(samples)
    result = dict(gpu=torch.cuda.get_device_name(0), torch=torch.__version__, samples=samples,
                  mean_ms=mean, fps=1000/mean, wall_seconds_including_setup_and_warmup=wall,
                  warmup_images=5, command=sys.argv, scope='infer_one_image: image I/O, YOLO, EgoNet, compensation, projection refinement, tightfit and prediction write; excludes model setup, calibration loading, final metadata CSV write; synchronized CUDA')
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ('samples','command')}))

if __name__ == '__main__': main()
