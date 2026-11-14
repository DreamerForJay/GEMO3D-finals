# GEMO3D 決賽補充實驗（實驗室伺服器執行用）

> 給實驗室電腦上的 AI／同學：GEMO3D 程式本體在 <https://github.com/DreamerForJay/GEMO3D>（安裝與推論參數見該 repo 之 README）。
> 本 repo 只放**決賽需要的補充任務**與繪圖腳本。請依〈任務清單〉執行，完成後依〈回傳清單〉把 `results/` 打包傳回。

- 專案頁：<https://xn--zwq108c.tw/GEMO3D/>　影片：<https://youtu.be/WyC59Sddipc>
- 資料（伺服器）：`/home/e114/KITTI_ROOT/...`、`/home/e114/data/KITTIDataset_Carla/training/`、`/home/e114/mono3d_comparison_fr/`

---

## 0. 環境

依 GEMO3D repo README 建立 `gemo3d` conda 環境，另外：

```bash
pip install pillow opencv-python numpy
sudo apt install ffmpeg fonts-noto-cjk   # 影片轉檔與中文字型
```

Linux 執行繪圖腳本時加：`--font /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc`

## 1. 任務清單（依優先順序）

### 任務 A｜CARLA 連續序列 demo 影片（最重要）

決賽評審要看「一段車子移動過程的畫面，經過系統後的結果」。

1. 以論文設定對 CARLA 評估序列推論，並保留預測檔（例：sedan 序列；路徑依伺服器實際位置）：

```bash
cd ~/Desktop/GEMO3D && conda activate gemo3d
export EGONET_ROOT="$PWD/EgoNet-master"; export EGONET_CFG="$PWD/EgoNet-master/configs/KITTI_inference:test_submission.yml"
KITTI_ROOT=/home/e114/KITTI_ROOT/sed_fr_T1R8/data/KITTIDataset_Carla
OUT=$HOME/finals/gemo3d_sed_seq
python gemo3d.py --kitti_root "$KITTI_ROOT" --split val --out_dir "$OUT" \
  --yolo_weights weights/yolo11n.pt --egonet_weights "$PWD/weights/egonet" \
  --dims_source fixed --fixed_dims_hwl 1.52,1.64,3.86 --height_m 1.52 --force_veh_type sedan \
  --vt_comp_pkl_map "compact=-,sedan=$PWD/models/sed_rank_ratio_linear_model.pkl,suv=-,van=-" \
  --proj_center_source pred_reproj_geom_x --proj_refine_iters 3 --tightfit --tightfit_max_nfev 15 --tightfit_k 50 \
  --conf 0.25 --imgsz 1280 --device cuda:0 --half --pred_meta_csv "$OUT/pred_meta.csv"
```

2. 畫成影片（車輛由遠而近的連續影格，建議 15–40 秒）：

```bash
python render_sequence_video.py --kitti_root "$KITTI_ROOT/training" --pred_dir "$OUT/pred/data" \
  --split_file "$KITTI_ROOT/ImageSets/val.txt" --fps 10 \
  --font /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc --out results/GEMO3D_demo_sequence.mp4
```

> 若 val 影格不是連續序列，請改用 `--frames 000100-000400` 指定一段連續影格。
> 若伺服器上已有之前跑好的 `pred/data`（例如 `/home/e114/mono3d_comparison_fr/` 下之 GEMO3D 輸出），可直接畫，不必重跑。

### 任務 B｜真實道路影像 demo（KITTI，若伺服器有 KITTI 原始資料）

證明可用於真實影像（產品化可行性）。對 KITTI val 中一段連續序列執行上述推論與繪圖，輸出 `results/GEMO3D_demo_kitti.mp4`，並記錄所用權重與參數。

### 任務 C｜高解析度圖檔

1. CVGIP 中文架構圖（論文圖 1）原始檔（drawio／pptx／visio）匯出 **PNG，寬 ≥ 4000 px**：`results/fig_architecture_zh.png`。
2. 若有英文版原始檔，同樣匯出 `results/fig_architecture_en.png`。

### 任務 D｜推論時間（可選）

在伺服器 GPU 上以同一組 100 張影像量測完整流程平均時間（ms／張、FPS），記錄 GPU 型號：`results/timing.json`。

## 2. 回傳清單

壓縮成 `gemo3d_results_<日期>.zip`：

- `results/GEMO3D_demo_sequence.mp4`（必要）、`results/GEMO3D_demo_kitti.mp4`（若有）
- `results/fig_architecture_zh.png`、`results/fig_architecture_en.png`
- 推論所用指令與 `pred_meta.csv`、`results/timing.json`
- 文字紀錄：資料路徑、權重、遇到的問題

## 3. 其他文件

- `docs/IMPROVEMENT_PLAN.md`：改善計畫
