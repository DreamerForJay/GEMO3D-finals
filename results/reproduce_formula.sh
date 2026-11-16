#!/usr/bin/env bash
set -euo pipefail
mkdir -p /home/e114/Desktop/GEMO3D-finals/benchmark_dataset/formula_20261116/ImageSets
if [ ! -e /home/e114/Desktop/GEMO3D-finals/benchmark_dataset/formula_20261116/training ]; then
  ln -s /home/e114/KITTI_ROOT/sed_lincoln_fr_T1R8/data/KITTIDataset_Carla/training /home/e114/Desktop/GEMO3D-finals/benchmark_dataset/formula_20261116/training
fi
printf '%s\n' 000170 000110 000043 > /home/e114/Desktop/GEMO3D-finals/benchmark_dataset/formula_20261116/ImageSets/val.txt
export EGONET_ROOT=/home/e114/Desktop/mono3d/GEMO3D/EgoNet-master
export EGONET_CFG="$EGONET_ROOT/configs/KITTI_inference:test_submission.yml"
/home/e114/anaconda3/envs/mono3d/bin/python /home/e114/Desktop/mono3d/GEMO3D/gemo3d.py --kitti_root /home/e114/Desktop/GEMO3D-finals/benchmark_dataset/formula_20261116 --split val --out_dir /home/e114/Desktop/GEMO3D-finals/benchmark_output/formula_20261116 --yolo_weights /home/e114/Desktop/mono3d/GEMO3D/yolo11n.pt --egonet_weights /home/e114/Desktop/mono3d/GEMO3D/weights/egonet --dims_source fixed --fixed_dims_hwl 1.511,2.128,4.902 --height_m 1.511 --force_veh_type sedan --vt_comp_pkl_map compact=-,sedan=/home/e114/Desktop/mono3d/GEMO3D/comp/sed_rank_ratio_linear_model.pkl,suv=-,van=- --proj_center_source pred_reproj_geom_x --proj_refine_iters 3 --tightfit --tightfit_max_nfev 15 --tightfit_k 50 --conf 0.25 --imgsz 1280 --device cuda:0 --half --pred_meta_csv /home/e114/Desktop/GEMO3D-finals/benchmark_output/formula_20261116/pred_meta.csv
