# GEMO3D Demo 與方法比較展示規劃（2026-11-18）

參考學術專案頁的呈現方式：Teaser 影片 → 方法總覽 → 輸入／輸出 Demo → 前後對照滑桿 → 與其他方法同畫面比較 → 失敗案例。
目標：評審 30 秒內看懂「輸入一張影像 → 得到 3D 車輛框與距離」，且看得出補償前後、與其他方法的差異。

> 規則：所有數字須來自實驗輸出檔（`results/`）；未量測者在頁面與簡報標「—」，不得以估計值代替。

## 一、展示項目

| # | 項目 | 內容 | 現有素材 | 需實驗室產出 |
|---|---|---|---|---|
| D1 | Teaser 影片（≤30 s） | CARLA 連續序列：左為原影像＋3D 框，右為 BEV 俯視（含 GT 框） | `GEMO3D_demo_CARLA連續序列_並排版.mp4` | 加 BEV 面板與 GT 框的版本 |
| D2 | 輸入→輸出 Demo | 單張影像 → 2D 框／車型／觀測角 → Z_raw → 比例 r̂ → Z_corr → 3D 框，逐步出現 | `loop-pinhole.mp4`、`loop-ratio.mp4`、`loop-reconstruct.mp4` | 3–5 張代表影像（近／中／遠、不同朝向）的各階段中間輸出圖 |
| D3 | 補償前後對照滑桿 | 同一張影像左右拖曳：僅針孔深度（Z_raw）vs. 投影高度比例補償（Z_corr），BEV 上同時顯示 GT | — | 同影像兩種輸出的 3D 框圖與 BEV 圖（PNG，同尺寸） |
| D4 | 與其他方法同畫面比較 | 2×2 影片：MonoDETR（2023）、MonoDGP（2025）、MonoAMNet（2025）、GEMO3D，同一 CARLA 序列同步播放，角落顯示該幀中心誤差 | — | 三個比較方法在同一序列的逐幀預測（KITTI 格式 txt） |
| D5 | 觀測角掃描 | 車輛 0–360° 旋轉，同步畫出 h2D 與 h3D,proj 比例曲線 | `GEMO3D_汽車轉角_觀測角.mp4` | 比例曲線逐角度數據（CSV） |
| D6 | 真實道路序列 | KITTI 或實拍序列上的 3D 框（對應 NEXT_EXPERIMENTS N10） | — | 待量測；未完成前頁面不放 |
| D7 | 失敗案例 | 遮擋、截斷、車型分類錯誤時的輸出與原因 | — | 3–5 個案例圖＋一句原因 |

## 二、實驗室工作清單（依優先順序）
1. **D4 比較影片**：在同一 CARLA 序列（建議 300 幀）跑 MonoDETR / MonoDGP / MonoAMNet，輸出 `results/demo/baselines/<method>/<frame>.txt`。
2. **D3 前後對照**：選 6 張影像（近 / 中 / 遠 × 正面 / 斜側），輸出 `results/demo/compare/<id>_raw.png`、`<id>_corr.png`、`<id>_bev.png`。
3. **D1 Teaser**：`render_sequence_video.py` 加 BEV 面板與 GT，輸出 `results/demo/teaser.mp4`。
4. **D2 中間輸出**：每張代表影像輸出 2D 框、Z_raw、r̂、Z_corr 數值（JSON）與疊圖。
5. **D7 失敗案例**：從 165 個共同樣本中挑誤差最大的 5 筆，附原因。
6. **D6 真實序列**：完成 N10 後再加入。

## 三、檔案規格
- 影片：1920×1080、30 fps、H.264（`-crf 23 -pix_fmt yuv420p`），單檔 ≤ 25 MB（GitHub 單檔上限 100 MB，網頁載入考量取 25 MB）；附一張首幀 JPG 作封面。
- 對照圖：同組 PNG 尺寸完全相同，寬 1600 px。
- 命名：`<demo編號>_<內容>_<日期>.mp4`，例如 `D4_method_compare_1120.mp4`。
- 上傳位置：本 repo `results/demo/`；網頁用的壓縮版另放 GitHub Pages `assets/`；原始大檔放雲端並在 `docs/MATERIALS_NEEDED.md` 記錄連結。

## 四、網頁區塊（GitHub Pages）
1. 標題、作者（可連結）、論文／影片／程式碼按鈕
2. D1 Teaser（自動靜音循環播放）
3. 方法總覽圖（系統架構圖）＋ D2 步驟動畫
4. D3 前後對照滑桿（純 HTML/JS，不需外部套件）
5. D4 比較影片＋結果表（方法名附年份）
6. D5 觀測角掃描
7. D7 失敗案例與限制
8. 引用格式（BibTeX）

## 五、簡報對應
- 決賽簡報可加一頁「Demo 展示」：左 D1 Teaser 影片、右 D4 比較影片截圖；QR code 連到 Demo 頁。
- 影片未完成前，簡報與海報只放已存在的素材。
