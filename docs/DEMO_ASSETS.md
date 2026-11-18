# GEMO3D Demo 素材需求（網頁＋簡報，目前最優先）

> **目前最優先（2026-11-18）**：網頁（GitHub Pages）與簡報都會用到以下影片／圖表素材。請實驗室依 P0 → P1 → P2 順序產出，完成一項就更新本文件狀態欄並推上 GitHub。
> 原則：畫面上出現的每個數字都必須來自同一次推論的輸出檔（`results/`），附上產生腳本；結果不佳的情境如實呈現。未量測的項目不放上網頁與簡報。

## 一、參考專案頁的素材類型（2026-11-18 逐頁檢視）

| 專案頁 | 用到的素材與呈現方式 |
|---|---|
| MoGe-3（qft-333.github.io/moge3page） | Teaser 影片；結果畫廊（點縮圖切換場景）＋互動 3D 檢視器；方法步驟滑桿（Coarse → Refined 逐步）；**與其他方法比較時可切換方法**的 3D 檢視；零樣本定量比較表；重點結論（Takeaways） |
| Scal3R（linjohnss.github.io/scal3r） | 長序列「輸入影像／BEV／結果」三支影片**同步播放**；與基準方法並排；互動點雲檢視；魯棒性分析 |
| GaMO（yichuanh.github.io/GaMO） | 2×3 拼貼 Teaser；每個場景「基準 vs. Ours」**拖曳滑桿影片**，多場景可切換 |
| BRDFusion（shigon255.github.io/brdfusion-page） | 多場景 Teaser 輪播；**同一場景 4 欄同步影片**（3 個比較方法＋Ours）；應用情境格狀影片 |
| RL-AWB（ntuneillee.github.io/research/rl-awb） | 首頁輸入／輸出拖曳對照；逐步改善動畫；**逐方法切換比較**；結果表 |
| DF3DV-1K（johnnylu305.github.io/df3dv1k_web） | YouTube 介紹影片；**排行榜表格**（排名、方法、指標、論文／程式碼連結、發表年份與會議）；資料集展示影片 |
| JanusMesh（siang1105.github.io/JanusMesh.github.io） | Teaser；依類別分組的結果影片牆 |
| VCD Analysis（yilunlee.github.io/VCD_Analysis） | 定量結果表＋多張**分析圖**（分布、熵、行為統計）＋可視化範例 |

## 二、常見素材清單（本作品對應）

| 代號 | 素材類型 | 呈現方式（網頁／簡報） |
|---|---|---|
| A | Teaser 影片（≤ 20 s） | 網頁首屏自動靜音循環；簡報封面後或系統展示頁 |
| B | 拍攝角度／相機配置 | 相機位置示意圖＋第三人稱視角影片，讓評審知道「相機裝在哪、看到什麼」 |
| C | 實際輸入 → 輸出 | 原始影格 → 中間結果 → 最終輸出，同一張影像逐步顯示 |
| D | 方法步驟滑桿 | 拖曳滑桿看每一步的變化（參考 MoGe-3 Coarse→Refined） |
| E | 多方法同步比較影片 | 同一輸入、同一幀號，2×2 或 1×4 格狀；本作品格子加框標示 |
| F | 前後拖曳對照 | 補償前／後、原始／旋轉等成對畫面（參考 GaMO、RL-AWB） |
| G | 互動檢視 | GEMO3D：BEV／3D 框可切換方法；CA-DFDS：距離儀表＋清晰度熱圖切換 |
| H | 定量比較表（排行榜式） | 方法名附年份與會議、最佳值粗體、本作品列標色、可排序 |
| I | 分析圖表 | 誤差 vs. 距離／角度／車色、逐幀誤差曲線、魯棒性 |
| J | 結果牆 | 依情境分組的小影片格（跟車、超車、對向…） |
| K | 失敗案例 | 每例一張圖＋一句原因 |
| L | 應用情境影片 | 對應海報「應用」的實際畫面 |
| M | 即時性 | 畫面角落顯示 FPS／每幀處理時間（需與 timing 結果一致） |

## 三、Demo 比較與數據的呈現設計（網頁與簡報共用）

1. **同步格狀比較**：同一段序列，各方法一格（標題「方法名（年份）」），所有格子同一幀號；本作品格子用主題色細框。每格左下角疊加該幀誤差（例：中心誤差 0.21 m）。
2. **影片下方逐幀誤差曲線**：x 軸幀號、y 軸誤差，各方法一條線，游標隨影片移動；曲線資料由 `per_frame.csv` 產生，網頁可互動。
3. **片尾數據卡**：影片最後 2 秒顯示該段 RMSE／平均誤差（與 `results/` 一致），方法名附年份。
4. **前後拖曳對照**：成對 PNG 或影片，左右同尺寸、同裁切。
5. **簡報用法**：每支影片另輸出 10–15 秒精華版（1080p、循環）；**列印版**用同一段的 3–4 張關鍵影格橫排取代影片。
6. **網頁用法**：每個情境一個分頁（tab）；上方影片、下方曲線與數據卡；另放完整排行榜表。

## 四、交付格式（每項素材一個資料夾）

```
results/demo/<代號>/
  video.mp4        1920×1080、30 fps、H.264（-crf 23 -pix_fmt yuv420p），≤ 25 MB
  video_short.mp4  簡報用 10–15 s 精華版
  poster.jpg       首幀
  keyframes/       列印版用 3–4 張關鍵影格（PNG）
  per_frame.csv    幀號、GT、各方法預測與誤差（網頁畫曲線用）
  summary.json     該段的彙總數字（RMSE、平均誤差、幀數、距離範圍）
  README.md        資料來源、設定、權重、產生指令
```
大於 25 MB 的原始影片放雲端，連結寫入 `docs/MATERIALS_NEEDED.md`。

## 五、GEMO3D 素材清單與優先順序

| 代號 | 優先 | 素材 | 內容與規格 | 比較／數據 | 狀態 |
|---|---|---|---|---|---|
| G-A1 | P0 | Teaser | CARLA 連續序列：左前視影像＋3D 框（藍：GEMO3D、橘虛線：GT），右 BEV；≤ 20 s | 角落顯示逐幀深度誤差 | ✅ [Teaser](../results/demo/G-A1/README.md)：18s＋12s；完整 F 新控制預測、逐幀 GT 誤差／曲線 |
| G-B1 | P0 | 拍攝角度 | ①前視相機（高 1.65 m、與論文內參相同）②第三人稱追車視角 ③俯視全景；同一段同步三視角 | 標註相機位置、視野範圍 | 🔄 [同 ID 三視角](../results/demo/G-B1/README.md)；缺追車；3 處時間／幀號異常，嚴格同步未證實 |
| G-C1 | P0 | 輸入→輸出 | 3 張代表影像（近／中／遠、正面／斜側）：原圖 → YOLOv11 2D 框 → 車型＋觀測角 → Z_raw → r̂ → Z_corr → 3D 框 | 每步顯示數值（JSON） | 🔄 [3 張×7 步 PNG／JSON](../results/demo/G-C1/README.md)；近中遠前視完成，斜側缺；車型為強制 sedan |
| G-E1 | P0 | 方法同步比較 | 同序列 2×2：MonoDETR（2023）、MonoDGP（2025）、MonoAMNet（2025）、GEMO3D；前視＋BEV 各一版 | 每格疊加中心誤差；下方逐幀曲線；片尾 RMSE 卡 | 🔄 [前視＋BEV 查核預覽](../results/demo/G-E1/README.md)：各18s＋12s；基準設定未核實，非公平排名 |
| G-F1 | P0 | 補償前後對照 | 同影像 Z_raw vs. Z_corr 的 3D 框與 BEV（含 GT），6 組成對圖＋1 段影片 | 顯示深度誤差前後值 | ✅ [6 組 PNG＋影片](../results/demo/G-F1/README.md)；A→D 只改 Rank-1，不是完整 F |
| G-J1 | P1 | 情境結果牆 | S1 同向跟車、S2 被超車、S4 對向來車、S5 路口轉彎（各 10–20 s） | 每段 per_frame.csv | ⬜ |
| G-D1 | P1 | 方法步驟滑桿 | 觀測角 0–360° 掃描：h₂D 與 h₃D,proj 比例曲線即時變化 | 曲線數據 CSV | 🔄 [7,200 筆模型比例網格](../results/demo/G-D1/README.md)；0–180°，原始高度／360°實測仍缺 |
| G-H1 | P1 | 排行榜表 | 165 共同樣本：深度 RMSE、中心誤差、BEV IoU、朝向角誤差、FPS；方法附年份與會議 | 與論文表 3 一致 | ⚠️ 舊 165 摘要未核實，現有 pairs 混不同 GT；[查核](../results/historical_165_audit.md)，不可作可信排行榜 |
| G-I1 | P1 | 分析圖 | 誤差 vs. 深度區間、誤差 vs. 觀測角（補償前後）、俯仰角敏感度 | 由 results 產生 | 🔄 [深度分箱／觀測角 CSV＋圖](../results/demo/G-I1/README.md)；受控 pitch 仍缺 |
| G-M1 | P1 | 即時性 | 影片角落顯示每幀處理時間；需註明 GPU 與是否共享 | 與 timing 結果一致 | ✅ [同次100幀計時＋預測](../results/demo/G-M1/README.md)；共享 RTX3060，89.241ms；播放非推論 FPS |
| G-K1 | P2 | 失敗案例 | 遮擋、截斷、車型誤判、遠距離小框 | 每例一句原因 | 🔄 [15 失敗例＋3 對照](../results/demo/G-K1/README.md)；強制 SUV 非實際分類器誤判 |
| G-J2 | P2 | 次要情境 | S3 本車超車、S6 前車切入、S7 多車同時、S8–S10 | — | ⬜ |
| G-L1 | P2 | 應用情境 | 路口監控視角（高架相機）數位孿生示意 | 需註明為模擬 | ⬜ |
| G-R1 | 待量測 | 真實道路 | KITTI 連續序列（同 N10） | — | ⬜ |

情境 S1–S10 的設定細節見 `docs/DEMO_PLAN.md` 第七節。

## 2026-11-18 交付入口

[完整素材清單與限制](../results/demo/README.md)；離線預覽 `results/demo/index.html`；網站整合讀 `catalog.json`、逐幀 CSV 與 geometry.json。所有影片 1080p／30fps／H.264，18秒完整版與12秒簡報版，皆含2秒數據卡。30fps僅為重取樣播放；數據維持原輸出精度、保留漏檢。

## 2026-11-18 雲端素材包

[下載 Demo 素材 ZIP](https://drive.google.com/file/d/1iRgBjb9RdAtCWrnTYF72UfBBu0S2FfvC/view?usp=drivesdk)：12支影片、54 PNG、23 JPG與CSV／JSON，內含離線預覽 `results/demo/index.html`。大小68,178,454 bytes；內容commit `77431e1`。[逐項狀態](../results/demo/README.md)／[上傳驗證紀錄](../results/cloud_upload_2026-11-18_demo.json)。G-E1只是歷史基準查核預覽；缺資料的項目仍標部分或待補，網站不可據此宣稱全部實驗完成。

## v2 呈現補強

已重新查閱八個參考頁，見[參考／A–M對照](DEMO_REFERENCE_REVIEW.md)。G-G1互動BEV／可旋轉3D框可用；每個主影片下方曲線可點擊跳至來源影格。6支 `_highlight_short.mp4` 才是真正固定3–13秒剪輯（加2秒片段數據卡），各有獨立CSV／摘要；原12秒版是整段加速。`results/demo/print/`有6張四幀橫排圖。18支影片已驗證；此互動預覽尚未部署正式網站。

### 最新v2下載

[互動素材v2 ZIP](https://drive.google.com/file/d/1Cgbtkw47FfzurnFNdHKa9XPaHhx1RqnX/view?usp=drivesdk)（79,758,680 bytes；內容commit b199216），含18支影片、60 PNG、23 JPG、離線互動頁與CSV／JSON。[上傳回讀紀錄](../results/cloud_upload_2026-11-18_demo_v2.json)。解壓開啟 results/demo/index.html；新精華影片名稱含 `_highlight_short`，數字對應各自的片段摘要。

## 最新：各配置分開＋誤差易讀解說

[7支獨立影片](../results/explained_demo/README.md)：Full／未補償／Rank-1／停用tightfit分開；中文框旁Z與ry、圖例、三種誤差與曲線解說。另有實際tightfit失敗、實測朝向誤差觀察、明確標示人工的yaw幾何示意。未取得實際轉角因果驗證素材，不以示意片充數。

[最新7支分開解說影片下載](https://drive.google.com/file/d/12tqZDcKPr3Qzl1ICrto0_j_lHEvQsg_c/view?usp=drivesdk)，13,440,768 bytes；[說明與來源](../results/explained_demo/README.md)。Full／A／D／停用tightfit各自獨立，另含實際失敗、朝向觀察及人工幾何示意；後者不是模型因果驗證。
