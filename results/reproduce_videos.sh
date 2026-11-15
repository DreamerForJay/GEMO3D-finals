#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON=${PYTHON:-/home/e114/anaconda3/envs/mono3d/bin/python}
"$PYTHON" render_sequence_video.py --kitti_root /home/e114/KITTI_ROOT/sed_lincoln_fr_T1R8/data/KITTIDataset_Carla/training --pred_dir /home/e114/eval_kitti/build/results/sed_lincoln_fr_T1R8/SVD/pred/data --frames 000000-000198 --fps 10 --summary_json results/carla_summary.json --out results/GEMO3D_demo_sequence.mp4
"$PYTHON" render_sequence_video.py --kitti_root /home/e114/KITTI_ROOT/training --pred_dir /home/e114/eval_kitti/build/results/kitti/unknown_hwl/pred/data --split_file results/kitti_demo_frames.txt --fps 1 --bev_range 80 --title 'GEMO3D KITTI 真實影像樣本（非連續序列）' --summary_json results/kitti_summary.json --out results/GEMO3D_demo_kitti.mp4
