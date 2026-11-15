# AI 協作交接

更新日期：2026-11-15（Asia/Taipei）。數值與證據以 [RESULTS.md](../RESULTS.md) 為準。

## 目前狀態

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
