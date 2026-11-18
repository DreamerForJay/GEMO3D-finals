# G-M1

Actual production_io_fp16 timing and predictions from the SAME 100-frame run; RTX 3060 shared with other processes. Mean 89.241ms, 11.206fps excludes startup/warmup. Offline video playback is 30fps. No dedicated-GPU or paper-FPS claim.

Source: `results/controlled_20261116` (2026-11-16 inference; source/weights/command hashes in its manifest). /home/e114/KITTI_ROOT/sed_lincoln_fr_T1R8/data/KITTIDataset_Carla/training

Rebuild: `python build_demo_assets.py --assets G-M1`

Blue: predictions; dashed orange: GT. Fixed BEV limits; out-of-view boxes remain in geometry.json and prediction counts. Empty errors mean unmatched, never zero. Per-frame CSV includes all predictions and missed GT. Metrics use matched objects, not all GT; report misses alongside them. Video cursor uses frame_mapping.csv. 30 fps is offline playback. Short version includes all frames with faster playback. No new model inference.

Timing exception: source is `results/timing_production_io.json`, prediction paths/hashes and exact command in timing_provenance.json, not controlled F.
