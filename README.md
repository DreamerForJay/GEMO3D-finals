# GEMO3D 決賽補充實驗（實驗室伺服器執行用）

> **展示審閱頁**：[成果／影片／補拍規劃](results/review_preview/README.md)，入口 `results/review_preview/index.html`。先供使用者檢視，未部署或整合正式網站。


> **中英文大字版已上傳**：[下載42.18MB素材包](https://drive.google.com/file/d/1vmbj7Oe3oZ_O9CdCQ_GumZJSS_IOVH9T/view?usp=drivesdk)（28支影片／離線頁）。內容commit `04960df`，42,182,897 bytes，ZIP、本機SHA256與Drive回讀檔名／大小／資料夾已核對；遠端checksum未提供。播放可離線，重建需完整專案與原始資料。舊版保留。

> **最新大字中英文版**：[28支素材與定義](results/bilingual_demo/README.md)，離線開啟 `results/bilingual_demo/index.html`。朝向支撐點與針孔偏差分兩片，明示幾何示意；實測片數據不變。


> **清爽版雲端已更新**：[下載21.93MB素材包](https://drive.google.com/file/d/1vDXZd7Y4cbov-cxtOhR-fQdA01PjWCUs/view?usp=drivesdk)（12片＋獨立圖表＋離線頁）。內容commit `0b631d2`，21,927,181 bytes；ZIP與本機SHA256、Drive回讀檔名／大小／資料夾已核對，遠端checksum未提供。舊包與分享範圍保留。

> **最新清爽版（2026-11-18）**：[獨立前視／實際俯視比較素材](results/clean_demo/README.md)。12支10秒影片，綠虛線GT／紅實線預測；影片只有方法名＋當幀指標，圖表移到影片外。離線開啟 `results/clean_demo/index.html`。


> **最新：分開看懂**：[下載7片解說包](https://drive.google.com/file/d/12tqZDcKPr3Qzl1ICrto0_j_lHEvQsg_c/view?usp=drivesdk) · [4種流程＋3支誤差解說影片](results/explained_demo/README.md)，框旁Z／朝向、中文圖例與曲線說明；離線開啟 `results/explained_demo/index.html`。

> **2026-11-18 Demo v2**：[下載新版79.76MB ZIP](https://drive.google.com/file/d/1Cgbtkw47FfzurnFNdHKa9XPaHhx1RqnX/view?usp=drivesdk) · 新增曲線跳幀、方法／3D框切換、6支真正精華剪輯與6張列印橫排圖。[參考頁對照](docs/DEMO_REFERENCE_REVIEW.md)。

> **v1 雲端快照**：[雲端下載 ZIP](https://drive.google.com/file/d/1iRgBjb9RdAtCWrnTYF72UfBBu0S2FfvC/view?usp=drivesdk) · [素材清單／限制](results/demo/README.md) · [最新成果摘要](RESULTS.md) · [機器整合清單](results/demo/catalog.json)。含12支1080p影片、方法步驟、補償拖曳圖、逐幀數據；離線預覽 `results/demo/index.html`。

> ⚠ 目前最優先：Demo 影片／圖表素材需求見 [`docs/DEMO_ASSETS.md`](docs/DEMO_ASSETS.md)。

> **2026-11-15 更新：下一階段實驗清單（審查建議整理、依優先順序）見 [docs/NEXT_EXPERIMENTS.md](docs/NEXT_EXPERIMENTS.md)，請優先執行。**


## 2026-11-16 重點更新

15組×199張控制推論及4組×100張計時完成。Rank-1降低深度誤差，但tightfit在本序列可能惡化；精簡讀圖降低約33.4%流程時間，100張預測不變。舊比較CSV發現混用不同GT。**尚非全部實驗／論文同條件重現完成**，詳見 [最新摘要](RESULTS.md) 與 [新實驗報告](results/ablation.md)。

## 最新成果與 AI 協作入口

- [實驗結果與雲端上傳紀錄](RESULTS.md)
- [成果壓縮檔（Google Drive，需要授權）](https://drive.google.com/file/d/1pZv85YbiBR9JTaJ24XN0BopSRfpYNidn/view?usp=drivesdk)
- [AI 工作規則](AGENTS.md) · [目前狀態與待辦交接](docs/HANDOFF.md)

2026-11-15：A 完成 CARLA 連續影片；B 僅完成 KITTI 非連續樣本展示；C 依使用者要求跳過；D 已有 RTX 3060 計時。詳細限制以 RESULTS.md 為準。每次實質更動後須更新結果與交接文件並同步 GitHub。


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

---

## 5. 完成後：同步回 GitHub（必做）

每完成一項任務就同步一次，讓本機（決賽簡報製作端）能直接取用：

```bash
git pull
mkdir -p results
# 1) 結果檔放在 results/；單檔 > 95 MB 的影片請改傳雲端並在 RESULTS.md 寫連結
git add results/ -f
# 2) 更新 RESULTS.md：每項任務一節，寫「指令、資料路徑、數值結果（表格）、檔案清單、遇到的問題」
# 3) 更新 docs/IMPROVEMENT_PLAN.md：完成的項目把 🔄/⬜ 改為 ✅，並在該列補一句結果
git add RESULTS.md docs/IMPROVEMENT_PLAN.md
git commit -m "lab results: <任務代號與一句摘要>"
git push
```

`RESULTS.md` 範本：

```markdown
## 任務 B｜表 8（測試距離 1.2–6.7 m）
- 執行日期／電腦：
- 指令：
- 資料路徑：
- 結果：（貼 CSV 表格）
- 檔案：results/table8_testdist.csv
- 備註：
```
