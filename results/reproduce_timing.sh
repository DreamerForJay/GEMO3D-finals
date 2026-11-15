#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p benchmark_dataset/ImageSets
if [ ! -e benchmark_dataset/training ]; then ln -s /home/e114/KITTI_ROOT/sed_lincoln_fr_T1R8/data/KITTIDataset_Carla/training benchmark_dataset/training; fi
seq -f "%06g" 0 99 > benchmark_dataset/ImageSets/val.txt
export EGONET_ROOT=/home/e114/Desktop/mono3d/GEMO3D/EgoNet-master
export EGONET_CFG="$EGONET_ROOT/configs/KITTI_inference:test_submission.yml"
/home/e114/anaconda3/envs/mono3d/bin/python benchmark_pipeline.py --source /home/e114/Desktop/mono3d/GEMO3D --output results/timing.json -- --kitti_root /home/e114/Desktop/GEMO3D-finals/benchmark_dataset --split val --out_dir /home/e114/Desktop/GEMO3D-finals/benchmark_output --yolo_weights /home/e114/Desktop/mono3d/GEMO3D/yolo11n.pt --egonet_weights /home/e114/Desktop/mono3d/GEMO3D/weights/egonet --dims_source fixed --fixed_dims_hwl 1.511,2.128,4.902 --height_m 1.511 --force_veh_type sedan --vt_comp_pkl_map compact=-,sedan=/home/e114/Desktop/mono3d/GEMO3D/comp/sed_rank_ratio_linear_model.pkl,suv=-,van=- --proj_center_source pred_reproj_geom_x --proj_refine_iters 3 --tightfit --tightfit_max_nfev 15 --tightfit_k 50 --conf 0.25 --imgsz 1280 --device cuda:0 --half --pred_meta_csv /home/e114/Desktop/GEMO3D-finals/benchmark_output/pred_meta.csv
