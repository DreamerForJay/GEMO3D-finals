# Demo 呈現參考與 v2 實作（2026-11-18）

## 重點

已重新閱讀使用者提供的八個官方專案頁。採用互動方式，未複製他們的圖片、影片、研究數據或網站原始碼。v2 是本專案離線素材預覽與整合元件，不代表已部署正式網站。

| 參考頁 | 本次查閱可確認的模式 | GEMO3D 對應 |
|---|---|---|
| [MoGe-3](https://qft-333.github.io/moge3page/) | refinement step 滑桿、場景縮圖、幾何檢視；部分比較素材標準備中 | G-C1七步、G互動BEV／3D框；不把框說成稠密幾何重建 |
| [Scal3R](https://linjohnss.github.io/scal3r/) | Input／BEV／3D與影片、互動檢視切換 | 同影格方法／視角切換；捕捉時間異常仍保留 |
| [GaMO](https://yichuanh.github.io/GaMO/) | 方法按鈕、逐場景比較、輸入overlay | G-E1方法選擇，G-F1六組對照 |
| [BRDFusion](https://shigon255.github.io/brdfusion-page/) | Method、Results、Application 分區 | 展示與應用分區；本次文字擷取不足以獨立驗證所有動態影片同步細節 |
| [RL-AWB](https://ntuneillee.github.io/research/rl-awb/) | Input／輸出拖曳比較 | G-F1同裁切PNG滑桿 |
| [DF3DV-1K](https://johnnylu305.github.io/df3dv1k_web/) | 資料集切換、Rank by指標、Paper／Code／Venue欄位 | 本次只排序已核實A/D/F消融；正式跨方法排行榜仍缺證據 |
| [JanusMesh](https://siang1105.github.io/JanusMesh.github.io/) | 按類型分區gallery、前後瀏覽 | 素材分類；不把單一approach當多種行車情境 |
| [VCD Analysis](https://yilunlee.github.io/VCD_Analysis/) | 定量結果與分析分區、指標與例圖對應 | G-I1逐幀／分箱、G-K1失敗案例與來源對照 |

## A–M 涵蓋與限制

| 類別 | 已有呈現 | 未滿足之處 |
|---|---|---|
| A Teaser | 18s＋短版、誤差曲線、數據卡 | 非即時推論錄影 |
| B 拍攝角度 | 前／頂／側同ID素材＋設定JSON | 缺第三人稱追車；3處時間／幀號異常 |
| C 輸入→輸出 | 近中遠×七步PNG／JSON | 缺斜側，sedan是強制設定 |
| D 步驟滑桿 | 七步切換；模型網格CSV | 缺360°原始高度影片 |
| E 同步比較 | 四格同ID、GEMO3D加框、中心誤差 | 歷史基準設定未核實，非公平排名 |
| F 前後對照 | 六對PNG拖曳、影片 | 比較A→D，不是完整F |
| G 互動檢視 | 方法切換、BEV／3D線框、旋轉、來源幀定位 | 無稠密mesh／點雲 |
| H 排行榜表 | A／D／F消融可排序，顯示漏檢 | 舊165跨方法排行榜仍不可核實 |
| I 分析圖 | 點擊曲線跳影片、滑桿、逐幀值、深度分箱 | 缺受控pitch測試 |
| J 情境牆 | 按已有素材分類 | 缺四種可核實行車情境，未冒稱完成 |
| K 失敗案例 | 15例＋3對照，保留來源 | 強制SUV不是觀測分類器誤判 |
| L 應用情境 | 待補狀態與需求 | 缺路口監控捕捉 |
| M 即時性 | 同次100幀timing、共享GPU標示 | 播放30fps非推論FPS |

## v2 的實質補強

1. 6個主影片面板都附真正的互動曲線。點曲線／滑桿會查 `*_frame_mapping.csv`，跳至該來源幀第一次出現的輸出影格中心，避免浮點／媒體時間取整錯到前一幀。未配對保留斷線與「未配對」。片尾改顯示數據卡狀態。
2. 同幀幾何檢視讀 `geometry.json`，可切換方法、BEV及可旋轉3D框；固定範圍裁切不刪除計數。
3. 6張3200×520的四影格橫排PNG供列印，包含四方法BEV版；原始四張keyframes仍保留。
4. 新增6支真正12秒精華版：固定擷取主片第3–13秒，保留原播放時間，再接2秒重新計算的片段RMSE卡。不是挑誤差較小的片段。原12秒整段加速版保留並區分；片段CSV／JSON可各自驗算。
5. 排序表只使用控制A/D/F同165配對。原始歷史基準缺設定，所以不製造SOTA排行榜或未量測FPS。

## 重建與驗證

原影片不用重跑推論：`python build_demo_highlights.py` → `python build_demo_catalog.py` → `python validate_demo_assets.py`。`build_demo_catalog.py`自動呼叫`enhance_demo_catalog.py`並更新素材manifest。

互動測試：`node validate_demo_interactions.cjs`（Playwright與Chrome；腳本目前記錄此研究主機的執行路徑）。涵蓋離線file://載入、來源幀定位、片尾狀態、方法／視角切換、表格排序、拖曳對照、七步滑桿與無JS錯誤。腳本使用獨立暫存瀏覽器profile，不讀使用者登入資料。
