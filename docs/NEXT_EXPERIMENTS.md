# GEMO3D 下一階段實驗清單（2026-11-15 審查建議整理）

> ⚠ **目前最優先：`docs/DEMO_ASSETS.md`（網頁與簡報用 Demo 影片／圖表素材，P0 先做）。**

> 給實驗室電腦上的 AI／同學：依優先順序執行。每完成一項，依 README 第 5 節同步回 GitHub（`RESULTS.md` 新增一節＋`results/` 檔案），並把本表該列狀態改為 ✅。
> 原則：只回報實際量測數字；未量測欄位寫「—」；與論文設定不同處（參數、GPU 是否共享、資料集）一定要寫清楚。

## 狀態總表

| 代號 | 實驗 | 優先 | 狀態 |
|---|---|---|---|
| N1 | 消融實驗：各模組獨立貢獻 | 極高 | 🔄 新Lincoln 199張A–F完成；原論文165來源待補 |
| N2 | 補償方法比較：Rank-1／Rank-2／Rank-3／Full-rank／2D 查表／多項式 | 極高 | 🔄 Rank1/2/3/full/查表/二次曲面比較完成（本次單序列） |
| N3 | 補償公式方向與中心定義之數學檢查＋手算例 | 極高 | 🔄 三距離實測／推論公式完成；建模端待核實，見 results/formula_check.md |
| N4 | 評估公平性：各方法 Precision／Recall／偵測成功率、資料切分表 | 極高 | 🔄 計數完成；查出舊pairs混不同GT，無洩漏證據待補 |
| N5 | 速度重測：與論文相同參數、獨佔 GPU，對照 31.12 FPS | 高 | 🔄 共享GPU四組分段完成；獨佔／論文設定待核實 |
| N6 | 跨條件：俯仰角、道路坡度、焦距、相機高度 | 高 | 🔄（PitchLab 已完成俯仰角 ±5°、±10°） |
| N7 | 投影一致性修正（tightfit）前後之 3D 誤差與 2D IoU | 高 | ✅ 本次序列165筆比較，10筆2D改善但3D變差 |
| N8 | 車型分類錯誤敏感度 | 中 | ✅ 本次序列強制SUV／Compact配置敏感度完成 |
| N9 | 模型參數量與儲存空間 | 中 | 🔄 補償儲存與baseline checkpoint tensor統計；trainable／error-head仍待核實 |
| N10 | KITTI 連續序列（tracking／raw）推論，設定可追溯 | 中 | ⬜ |
| N11 | Jetson（或同級邊緣裝置）計時 | 中 | ⬜ |
| V1 | Demo 影片：Teaser 三聯畫面（前視＋3D 框｜BEV 含 GT｜深度誤差曲線） | 高 | ⬜（現有 `results/GEMO3D_demo_sequence.mp4` 只有前視＋BEV） |
| V2 | Demo 影片：CARLA 情境序列 S1 同向跟車、S2 被超車、S4 對向來車、S5 路口轉彎 | 高 | ⬜ |
| V3 | Demo 影片：同序列 2×2 同步比較 MonoDETR（2023）／MonoDGP（2025）／MonoAMNet（2025）／GEMO3D | 高 | ⬜ |
| V4 | Demo 對照：補償前（Z_raw）／補償後（Z_corr）3D 框與 BEV，6 張代表影像 | 高 | ⬜ |
| V5 | Demo 影片：次要情境 S3 本車超車、S6 前車切入、S7 多車同時 | 中 | ⬜ |
| V6 | 方法動畫：M1 車輛 0–360° 旋轉＋h2D／h3D,proj 比例曲線、M2 針孔相似三角形、M3 Rank-1 曲面分解 | 中 | 🔄 已有 loop-pinhole／loop-ratio／loop-reconstruct 與汽車轉角影片；M3 待做 |
| V7 | 失敗案例圖／短片（遮擋、截斷、車型誤判） | 中 | 🔄 `results/failure_cases/` 已有圖，待補原因說明 |
| V8 | 真實道路連續序列影片（同 N10） | 中 | ⬜（現有 `GEMO3D_demo_kitti.mp4` 為非連續影格） |
| V9 | 低優先情境 S8 彎道／坡道、S9 俯仰角、S10 夜間雨天 | 低 | ⬜ |

---

## N1｜消融實驗（最重要）

在論文同一 CARLA 評估集（165 共同樣本協定，另附全部樣本版本）上，逐步開啟模組：

| 設定 | 說明 | 深度 RMSE | 3D 中心誤差 | BEV IoU |
|---|---|---|---|---|
| A | 針孔模型，無補償 | | | |
| B | A＋固定比例補償（全域常數 r） | | | |
| C | A＋觀測角查表補償（只依 θ） | | | |
| D | A＋Rank-1 SVD 補償 | | | |
| E | D＋道路平面約束 | | | |
| F | E＋投影一致性修正（完整 GEMO3D） | 0.27（論文） | 0.25（論文） | 0.82（論文） |

- 每列記錄：指令、參數差異、樣本數。
- 輸出：`results/ablation.csv`、`RESULTS.md` 任務 N1 一節。

## N2｜補償方法比較

| 方法 | 比例重建 RMSE | 深度 RMSE | 3D 中心誤差 | 參數量 | 推論時間 |
|---|---|---|---|---|---|
| Rank-1 | | | | | |
| Rank-2 | | | | | |
| Rank-3 | | | | | |
| Full-rank（完整比例矩陣插值） | | | | | |
| 2D 查表＋雙線性插值 | | | | | |
| 低階多項式曲面（θ, Z） | | | | | |

- 能量占比定義：η_k = Σ_{i≤k} σ_i² ／ Σ σ_i²。
- 論文表 1 已有：Rank-1 95.11／98.55／98.94%，Rank-1+2 96.77／99.28／99.29%（Compact／Sedan／SUV）。
- 目的：證明 Rank-1 的深度精度接近 Full-rank，且優於查表、多項式。

## N3｜補償公式一致性檢查

1. 確認程式中 r 的定義：r = h_2D／h_ideal 或 h_ideal／h_2D，以及補償式是 Z_corr = r·Z_raw 或 Z_raw／r。
2. 確認建模（Blender）與推論（CARLA）使用的深度是幾何中心或底部中心，是否一致。
3. 從 `pred_meta.csv` 取 3 個實際樣本，列出 f_y、H_avg、h_2D、Z_raw、r、Z_corr、GT 深度做手算驗證。
4. 補充誤差傳遞：ΔZ ≈ −Z²／(f_y·H)·Δh，用實際 f_y 算 20／30 m 時 1 px 框高誤差造成的深度誤差。
- 輸出：`results/formula_check.md`（含 CARLA 相機實際 f_y，**簡報需要此數值取代目前 KITTI 示意值**）。

## N4｜評估公平性

- 對四種方法分別報告：偵測數、配對數、Precision、Recall（IoU ≥ 0.5），以及 165 共同樣本外的漏偵測數。
- 資料切分表：Blender 建模資料（車型 CAD、尺寸、相機內參、高度、角度與距離分布）vs. CARLA 測試資料，確認沒有測試資料洩漏。
- 輸出：`results/detection_stats.csv`、`results/data_split.md`。

## N5｜速度重測（對照論文 31.12 FPS）

- 與論文相同之參數與量測範圍（README 中 timing 設定），**獨佔 GPU**（無其他行程），RTX 3060。
- 分別記錄：YOLO、Ego-Net、補償、投影修正、tightfit、檔案寫入各段時間。
- 若關閉 tightfit 或改 FP16 另列一行。
- 輸出：`results/timing_breakdown.json`。決賽前已測得共享 GPU 6.51 FPS（153.56 ms），需說明差異來源。

## N6｜跨條件測試

| 條件 | 建議值 | 狀態 |
|---|---|---|
| 俯仰角 Pitch | −10°、−5°、0°、+5°、+10° | ✅ PitchLab（雲端 PitchLab_研究成果_20261115） |
| 道路縱坡 | −5%、0%、+5% | ⬜ |
| 焦距 | 700、900、1100 px | ⬜ |
| 相機高度 | 1.2、1.5、1.8 m | ⬜ |

- PitchLab 已有：+10° 未校正深度誤差約 7 m；影像旋回水平後 3D 中心誤差 7.69 → 1.81 m。下一步：不旋轉影像之幾何補償，並以地平線／消失點估測未知 Pitch。
- 請把 PitchLab 的摘要、CSV、代表圖複製到本 repo `results/pitchlab/`，並在 RESULTS.md 新增一節。

## N7｜投影一致性修正前後比較

- 修正前／後之深度誤差、3D 中心誤差、BEV IoU、2D 投影 IoU。
- 若 2D IoU 上升但 3D 誤差變大，記錄案例。輸出 `results/tightfit_ablation.csv`。

## N8｜車型分類錯誤敏感度

- 對同一批樣本強制替換車型（Sedan→SUV、Sedan→Compact 等），量測深度 RMSE、3D 中心誤差、BEV IoU 變化。

## N9｜參數量與儲存空間

- Rank-1 模型（每車型三條曲線）之參數數與檔案大小，對照 MonoDGP 誤差預測頭、MonoDETR 模型大小。

## N10｜KITTI 連續序列

- 使用 KITTI tracking 或 raw 連續影格，以可追溯設定（權重、尺寸來源、指令）重新推論並繪製影片；記錄配對率與深度誤差。決賽前 KITTI 非連續樣本配對深度 RMSE 26.54 m，需找出原因（尺寸、內參、Pitch、坡度）。

## N11｜邊緣裝置計時

- 若有 Jetson Orin Nano（或同級）：完整流程 ms／張、FPS、功耗。

---

## V 系列｜Demo 影片與動畫（2026-11-18 新增）

用途：決賽現場簡報（3 分鐘版第 7 頁系統展示）、GitHub Pages 專案頁、評審 Q&A。完整情境與畫面設計見 `docs/DEMO_PLAN.md` 第一、六、七節。

- 規格：1920×1080、30 fps、H.264（`-crf 23 -pix_fmt yuv420p`），單檔 ≤ 25 MB，另附首幀 JPG；對照圖同組尺寸相同、寬 1600 px。
- 命名：`<代號>_<內容>_<日期>.mp4`，例如 `V3_method_compare_1120.mp4`；放 `results/demo/`，大檔放雲端並記錄連結於 `docs/MATERIALS_NEEDED.md`。
- 每支影片附一段 `results/demo/<代號>.md`：資料來源、幀數、距離範圍、使用的權重／設定、影片中顯示的數字出處。
- 影片中出現的誤差數字必須來自同一次推論輸出；結果不佳的情境也如實呈現，不剪掉。
- 完成後把上表狀態改為 ✅，並通知更新簡報與專案頁。

## 同步規則

```bash
git pull
git add results/ -f && git add RESULTS.md docs/NEXT_EXPERIMENTS.md
git commit -m "lab results: N<代號> <一句摘要>"
git push
```
並依 `scripts/` 或既有方式同步到雲端資料夾 `GEMO3D語喬/GEMO3D-finals`。
