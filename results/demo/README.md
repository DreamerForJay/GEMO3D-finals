# Demo／網頁素材交付｜2026-11-18

## 重點

- 可用：G-A1 Teaser、G-F1 六組補償對照、G-M1 同次計時影片；另有步驟圖、三視角、方法比較查核預覽、分析與失敗素材。
- 所有影片為 1080p／30fps／H.264；完整版 18 秒，簡報版 12 秒，各含 2 秒數據卡。播放重新取樣，不代表原始拍攝／推論 FPS。
- 新控制完整 F 深度 RMSE 1.305m；A→D 1.694→0.762m。F 不比 D 好，未隱藏失敗。
- capture_anomalies.json 有 3 個時間或幀號重複轉換。素材按影像 ID 排列，不宣稱嚴格時間同步。

## 使用

解壓後直接開啟 index.html 可離線預覽影片、拖曳對照與七步圖，不需安裝工具。catalog.json 為網站整合入口；讀各項 summary.json、per_frame.csv、geometry.json。影片時間與來源影格用 video_frame_mapping.csv（BEV 用 bev_frame_mapping.csv）對應。缺值是未配對，不可轉成零。

```bash
python build_demo_assets.py
python build_demo_catalog.py
python validate_demo_assets.py
```

依賴 Python 3、numpy、Pillow、opencv-python、matplotlib、imageio-ffmpeg。原資料、權重與精確命令見 results/controlled_20261116/manifest.json；預測／GT 幾何已隨包提供。重建背景圖片仍需本機原資料（未打包完整資料集）。非已部署網站。

## 狀態

| 素材 | 狀態 | 範圍／限制 |
|---|---|---|
| G-A1 | ready | 18 秒 Teaser＋12 秒版；完整 F 的 199 幀、GT、BEV、誤差曲線。 |
| G-B1 | partial | 三個既有視角同 ID 配對；缺追車視角，3 處時間／幀號異常，嚴格同步未驗證。 |
| G-C1 | partial | 近中遠三張、各七步 PNG＋JSON；目前只有前視，缺斜側；sedan 為強制設定而非分類結果。 |
| G-E1 | audit_preview | 四方法前視／BEV 各 18 秒＋12 秒版；歷史基準設定未核實，禁止作公平排行榜。 |
| G-F1 | ready | 6 組同尺寸成對 PNG、影片與逐幀 CSV；A→D 只改補償，非完整 F。 |
| G-D1 | partial | 7200 筆模型比例網格可供互動圖；缺原始高度資料與 360° 實測掃描。 |
| G-G1 | ready | 各影片下方可切換方法的BEV／3D線框檢視，支援旋轉；不是稠密場景重建。 |
| G-H1 | blocked | 舊 165 筆來源混不同 GT，不能製成可信排行榜；見 historical_165_audit.md。 |
| G-I1 | partial | 深度分箱、逐幀觀測角與誤差 CSV、分析 PNG；缺受控 pitch 敏感度。 |
| G-M1 | ready | 100 幀實際計時及同次預測；RTX 3060 共享，89.241ms／11.206fps；影片為離線播放。 |
| G-K1 | partial | 15 例失敗圖＋3 張 tightfit 對照。強制 SUV 是人工干預，不是真實分類器誤判。 |
| G-J1 | blocked | 缺可核實 S1/S2/S4/S5 場景腳本與新捕捉；單一 approach 不冒充四情境。 |
| G-J2 | blocked | 缺 S3/S6/S7/S8–S10 場景捕捉。 |
| G-L1 | blocked | 缺路口監控捕捉與數位孿生對應資料。 |
| G-R1 | blocked | 缺有時間資訊的真實 KITTI raw/tracking 連續序列。 |

原始整體架構圖任務 C 依使用者要求跳過；G-C1 是本次新增的逐步輸出素材，兩者不同。

## v2 互動呈現

逐幀曲線支援點擊定位、影格滑桿；以影片映射表定位，非假設每來源幀都佔1/30秒。互動BEV／3D線框可切換方法與旋轉。這是既有框的幾何檢視，不是稠密場景重建。A/D/F消融表可排序；未製造跨方法排行榜。`print/`提供六張3200×520四幀橫排PNG，包括四方法BEV版。原12秒版為整段加速呈現；另有6支 `_highlight_short.mp4` 真正片段剪輯：固定擷取完整版3–13秒，加上2秒片段數據卡（重算該片段unique source frames的RMSE）。時段為預先固定規則，不依誤差挑選。

先執行原build_demo_catalog.py，它會自動呼叫enhance_demo_catalog.enhance；不要單獨重複套用enhance。互動資料由已交付CSV／geometry.json內嵌為JS，可file://離線開啟。
