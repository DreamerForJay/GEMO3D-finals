# G-B1

PARTIAL: front/top/side paired by image ID; duplicate timestamps/simulator frame IDs prevent strict temporal sync verification (capture_anomalies.json). Side orthographic audit camera is NOT third-person chase. Chase view remains unavailable; no CARLA actors or active world modified.

Source: `results/controlled_20261116` (2026-11-16 inference; source/weights/command hashes in its manifest). /home/e114/KITTI_ROOT/sed_lincoln_fr_T1R8/data/KITTIDataset_Carla/training

Rebuild: `python build_demo_assets.py --assets G-B1`

Blue: predictions; dashed orange: GT. Fixed BEV limits; out-of-view boxes remain in geometry.json and prediction counts. Empty errors mean unmatched, never zero. Per-frame CSV includes all predictions and missed GT. Metrics use matched objects, not all GT; report misses alongside them. Video cursor uses frame_mapping.csv. 30 fps is offline playback. Short version includes all frames with faster playback. No new model inference.
