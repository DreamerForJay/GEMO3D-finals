# AI 協作交接

## 最新交接：展示審閱預覽

使用者要求先看頁面再決定正式整合。新增results/review_preview/index.html、app.js、data.js，媒體相對引用../bilingual_demo/。勿直接部署正式網站。8項補拍建議不是已完成任務；4視角圖為概念，模型仍只用前視。data.js由現有summary.json產生，沒有重新推論。validate_review_preview.cjs已通過，截圖preview.png。使用者回饋後再整理正式頁內容；未追蹤PitchLab與tests保持不動。


> **中英文大字版已上傳**：[下載42.18MB素材包](https://drive.google.com/file/d/1vmbj7Oe3oZ_O9CdCQ_GumZJSS_IOVH9T/view?usp=drivesdk)（28支影片／離線頁）。內容commit `04960df`，42,182,897 bytes，ZIP、本機SHA256與Drive回讀檔名／大小／資料夾已核對；遠端checksum未提供。播放可離線，重建需完整專案與原始資料。舊版保留。

## 最新交接：中英文大字版

使用 `results/bilingual_demo/index.html`，28片分開選語言／主題。build_bilingual_demo.py、build_bilingual_catalog.py生成；validate_bilingual_demo.py、validate_bilingual_page.cjs驗證。原clean不覆蓋。朝向影片為固定Z10m長方體精確投影，不是實測旋轉；h_ideal=fyH/Z不冒稱已核實原Blender h3D,proj。黃支撐點、青車頭、方向盤；不能把合成yaw_geometry.csv混入實測CSV。原轉角實測與訓練分母限制仍在。


> **清爽版雲端已更新**：[下載21.93MB素材包](https://drive.google.com/file/d/1vDXZd7Y4cbov-cxtOhR-fQdA01PjWCUs/view?usp=drivesdk)（12片＋獨立圖表＋離線頁）。內容commit `0b631d2`，21,927,181 bytes；ZIP與本機SHA256、Drive回讀檔名／大小／資料夾已核對，遠端checksum未提供。舊包與分享範圍保留。

## 2026-11-18 最新：清爽比較為預設入口

使用者拒絕資訊密集影片；改用 `results/clean_demo/index.html`。12片只有方法名及一個指標，曲線另外放。不要把曲線、BEV示意、三項誤差再塞回同片。綠虛線GT／紅實線預測。

- 實際top_camera影像已用前後相機外參投影。統一GT底部Y平面繪製footprint（非車頂），數字仍為metric XZ IoU。來源 controlled_20261116，不是新推論。
- `build_clean_demo.py` → `build_clean_catalog.py` 可重建；`validate_clean_demo.py`完整解碼與幾何核對、`validate_clean_page.cjs`離線互動測試均通過。
- 199 image IDs全保留，三處metadata重複未修飾；缺實際轉彎因果影片、多情境等既有限制不變。Full是F全管線。
- 舊v1/v2/explained版本保留；未追蹤PitchLab與tests不在本次提交或雲端包。


更新日期：2026-11-18（Asia/Taipei）。數值與證據以 [RESULTS.md](../RESULTS.md) 為準。

## 2026-11-18 最新交接：分開解說

`results/explained_demo/`是新增的獨立交付，不覆蓋v2素材。4支配置獨立片＋3支誤差片，共7片。build_explained_demo.py／validate_explained_demo.py可重建與驗證；來源仍是controlled_20261116。

1. Full＝完整F流程，不等於full矩陣補償。四支曲線同尺度，可公平目視同序列消融，但仍受既有尺寸映射限制。
2. 藍框預測／橘虛線GT、Z與ry數值、三種誤差已分清。yaw_observed是觀測，不是受控轉彎／轉換錯誤因果證據。
3. yaw_geometry只使用GT固定中心與尺寸人工旋轉。mapping的source_frame固定000110，simulation_sample另列，不冒充121張真實影像。角點RMS不是模型準確率。
4. tightfit_failure以失敗說明挑前31幀，不是代表性整體排名；保留漏檢，從同幀F_no_tightfit／F比對。仍缺可核實實際轉角序列。
5. [7片雲端包](https://drive.google.com/file/d/12tqZDcKPr3Qzl1ICrto0_j_lHEvQsg_c/view?usp=drivesdk)已回讀核對（13,440,768 bytes，內容commit 2d01bdb）；[收據](../results/cloud_upload_2026-11-18_explained.json)。既有v1/v2不覆寫；未追蹤PitchLab附件仍不屬本次包。

## 2026-11-18 最新交接：互動 v2

先讀 [參考頁／A–M對照](DEMO_REFERENCE_REVIEW.md)。新增6個曲線與幾何互動面板、6支真精華剪輯、6張四幀橫排圖及可排序消融表。所有主影片與原測量未更動。

- 新精華 `*_highlight_short.mp4` 是固定3–13秒＋2秒片段卡；只可引用相應 `*_highlight_summary.json` 的數字，不能拿全199幀摘要冒充片段數據。
- build_demo_highlights.py處理剪輯，build_demo_catalog.py自動呼叫enhance_demo_catalog.py。勿直接反覆enhance；先重建base。demo_interactions.js是來源，results/demo/interactions.js為複本。
- 互動以frame_mapping查來源幀，seek採輸出幀中心防止時間量化錯前一幀；缺值保持null。互動與影片驗證紀錄分開保存，manifest排除這兩份後生成驗證報告。
- 18支影片、60 PNG、23 JPG；G-G1可用，正式跨方法排行榜、多情境捕捉仍未完成。[v2雲端ZIP](https://drive.google.com/file/d/1Cgbtkw47FfzurnFNdHKa9XPaHhx1RqnX/view?usp=drivesdk)／[收據](../results/cloud_upload_2026-11-18_demo_v2.json)已驗證；內容commit b199216，79,758,680 bytes，保留v1。

## 2026-11-18 v1交接：Demo 素材

雲端交付完成：[ZIP](https://drive.google.com/file/d/1iRgBjb9RdAtCWrnTYF72UfBBu0S2FfvC/view?usp=drivesdk)（68,178,454 bytes，內容commit `77431e1`）；[回讀驗證紀錄](../results/cloud_upload_2026-11-18_demo.json)。ZIP 是不可變快照，不包含本次上傳收據，請另讀最新 GitHub。未更動分享權限；遠端checksum未提供。

先讀 [素材總表](../results/demo/README.md) 和 [catalog.json](../results/demo/catalog.json)。12 支 MP4、54 PNG、23 JPG、逐幀 CSV／JSON、離線 index.html 已產生並驗證。重建腳本 build_demo_assets.py → build_demo_catalog.py → validate_demo_assets.py。

- 可直接使用 G-A1、G-F1、G-M1；G-E1須保留「歷史設定未核實／非公平比較」標示。
- G-C1強制sedan，不能呈現為分類器成功；G-F1為A→D而非全流程；計時100幀的RMSE與199幀F不同。
- 捕捉 metadata 在000091→000092、000094→000095、000097→000098有重複時間或幀號，嚴格同步未證實。不能把側視audit相機標成追車。
- G-H1原165排行榜需原始同資料同設定證據；多情境／pitch／360原始高度／KITTI時序仍缺。後續需新增獨立捕捉或取得來源，不能改動共享CARLA世界。
- 當前基於上游4bf3a08；原推論證據dca5aa6。所有輸出是既有數據重製，不是新一輪推論。整體架構圖仍跳過。
- 本機未追蹤PitchLab與tests保持原狀，不屬此包。

## 2026-11-16 接手重點

15組×199張新控制推論與4組×100張分段計時已完成並同步；先讀RESULTS.md頂部摘要、results/ablation.md、results/historical_165_audit.md。可執行工作已推進到實際測量，不再停在三張公式例子。

- 深度RMSE A1.694、D0.762、F1.305m；tightfit不保證改善，10筆2D更好而3D更差。
- 精簡除錯視角I/O：134.017→89.241ms，100張預測完全一致；可用benchmark_stages.py --production-io，不已部署於核心repo。
- 舊四方法pairs混不同GT，同ID交集128但GT一致0；不要沿用這些CSV宣稱重現165。
- 新模型比例網格可重建Rank1/2/3/full；訓練原CSV仍缺，使用者已被詢問路徑，尚未收到。
- 繼續需：建模原始來源、論文計時命令、獨立CARLA受控捕捉環境、KITTI raw/tracking資料。不要動正在跑的CARLA世界／actor來湊獨佔條件。
- PitchLab未核准附件繼續留本機；不要把其他實驗同步授權解讀為可繞過原審核。
- 回報先列重點摘要，再給詳細連結，依使用者要求。

## 原有展示狀態

| 項目 | 狀態與限制 |
|---|---|
| A CARLA | 完成：199 張、19.9 秒；歷史預測重繪，187 配對，深度 MAE 0.267 m |
| B KITTI | 部分完成：30 張非連續樣本展示；MAE 18.67 m，不能代表連續道路影片或正式精度驗證 |
| C 架構圖 | 使用者要求跳過，認為已有 |
| D 計時 | 完成：RTX 3060、100 張；暖機後 153.56 ms/張，整次含初始化／暖機 27.69 秒；詳細計時範圍見報告 |
| 雲端交付 | 已上傳原 ZIP；Drive metadata 已核對檔名與 8,090,793 bytes；私人存取 |

## 成果入口

- [Drive 成果 ZIP](https://drive.google.com/file/d/1pZv85YbiBR9JTaJ24XN0BopSRfpYNidn/view?usp=drivesdk)
- [上傳機器紀錄](../results/cloud_upload_2026-11-15.json)
- 實驗成果 commit：`fdec776f629e9d41ac55d1b197cf0eb8817d1d80`。
- ZIP 不包含之後新增的上傳紀錄／協作文件；接手時需讀 GitHub 最新文件。
- 本機 repo：`/home/e114/Desktop/GEMO3D-finals`。
- 本機 ZIP：`/home/e114/Desktop/gemo3d_results_2026-11-15.zip`。
- Python：`/home/e114/anaconda3/envs/mono3d/bin/python`。
- GEMO3D 本體：`/home/e114/Desktop/mono3d/GEMO3D`，計時版本 `3dd8e9a404d425ebee8bad40040659ddcdc64757`。

## 已驗證

四項幾何／配對測試通過；兩支影片完整解碼 199/199、30/30；單影格 smoke test 及缺檔失敗檢查完成。原 ZIP testzip 通過。雲端僅驗證 metadata，未驗證遠端 checksum。

## 待辦與接續方式

1. 若繼續 B：先找／取得有時間對應的 KITTI raw 或 tracking 影像、校正與序列資訊；不能把 object detection ID 排序當連續行車。使用可追溯的權重／命令重新推論。
2. 釐清 KITTI 既有結果誤差大的來源，再談性能改善；保留所有失效案例，不只挑選漂亮結果。
3. 若需要論文同設定重現，先追溯 A 歷史推論命令及權重；目前不具備完整證據。
4. 新實驗須另存結果，記錄資料、權重 checksum、命令、環境與計時範圍；不要覆寫歷史 demo 或原 ZIP。
5. 每次實質更動後依 [AGENTS.md](../AGENTS.md) 同步報告、狀態與 GitHub。無任何背景監控／自動輪詢已啟用。

## 本次動作

2026-11-15：依使用者要求上傳原成果包至新建的 Drive `GEMO3D-finals` 資料夾，核對 metadata，新增上傳記錄、README 入口、AGENTS.md 與本交接。未重跑實驗、未更動既有數值、未擴大雲端權限。


## 2026-11-16 接續更新

- 最新上游已讀至 f9fe4a7，包含 docs/NEXT_EXPERIMENTS.md；issues #1–#8 已盤點，見 ISSUE_REVIEW_2026-11-16.md。
- PitchLab 已定位「GUI 舊座標全部配對 vs 新報告水平座標共同位置」差異；兩套統計各自加總一致，不能混用。
- 已直接修正研究主機 mono3d-pitch-study GUI 的字體、來源標示、缺值處理；修補檔與來源雜湊保留在研究主機本機，尚未發布。其他私有複本未修改。需重新開啟 GUI 才生效；無完整桌面 UI 驗證。
- 優先等待使用者定位其特定錯誤圖；現有可重現問題已修。issue #6 仍未完成全部整理／跨條件實驗。
- 下一階段優先 #1（實際內參與公式方向）及 #2（11/18 速度重測）；不可為獨佔 GPU 擅自終止其他工作。#8 整體架構圖仍依使用者要求不重做。

- 新查核包上傳被自動審核拒絕，待使用者確認分享範圍。完整本機成果保存在本機分支 codex/pitchlab-audit-local-20261116；該分支未推送。GitHub 本次只同步文字摘要，不以其他方式繞過附件上傳限制。


## 2026-11-16 本次公式查核交接

已同步 check_formula.py 與 results/formula_*、reproduce_formula.sh。issue #1三距離新推論與乘法核對完成，惟 Blender 訓練分母／中心定義缺原腳本，維持部分完成。重要：config.py 依車型覆蓋 fixed_dims_hwl，歷史計時實際建框為1.52,1.64,3.86；H_used仍1.511。後續消融／計時必須同時驗證有效設定。

#2 nvidia-smi顯示CARLA佔用且97%利用率，未跑獨佔計時；見 results/timing_breakdown.md。下一步先取得建模腳本及原論文計時參數，再於GPU空閒時重測，不擅自停止其他行程。#3–#8仍待後續實驗，C繼續跳過。PitchLab本機附件未發布。
