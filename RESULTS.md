# 決賽實驗更新 — 2026-11-15

依 GEMO3D-finals `d9bf54e6e46bfbad471b0fffaeb7617e9a679e66` 執行。獨立工作目錄 `/home/e114/Desktop/GEMO3D-finals`。既有 AMNet 程式與資料未修改。

## 任務 A｜CARLA 連續序列：完成

- 影片：[GEMO3D_demo_sequence.mp4](results/GEMO3D_demo_sequence.mp4)，1920×1080、H.264、10 FPS、199 張、19.9 秒。
- 資料：`/home/e114/KITTI_ROOT/sed_lincoln_fr_T1R8/data/KITTIDataset_Carla/training`。
- 預測：`/home/e114/eval_kitti/build/results/sed_lincoln_fr_T1R8/SVD/pred/data`，直接重用歷史結果，未重跑此影片的推論。
- 影格：000000–000198，沒有缺號；GT 深度由 35.773440 m 降至 5.157685 m，相鄰最大差 0.179245 m。10 FPS 是展示播放速度，未宣稱為錄製原始 FPS。
- 影片呈現相機 3D 框、GT、鳥瞰圖與深度誤差。
- 命令：`bash results/reproduce_videos.sh`；完整參數保存在該腳本。
- 歷史推論的完整命令、權重版本及原始 pred_meta.csv 未在該輸出目錄找到，不能宣稱與 README 論文設定完全一致。現有預測尺寸約 1.51×2.13×4.90 m，屬 Lincoln sedan；README 範例的 1.52×1.64×3.86 m 不應直接替換為本次結果來源。

| 指標 | 值 |
|---|---:|
| 預測 / GT 車輛數 | 199 / 199 |
| 配對數 | 187 |
| 未配對預測 / GT | 12 / 12 |
| 配對深度 MAE | 0.266660 m |
| 配對深度 RMSE | 0.358734 m |

## 任務 B｜KITTI 真實影像：完成樣本展示，連續序列仍缺

- 影片：[GEMO3D_demo_kitti.mp4](results/GEMO3D_demo_kitti.mp4)，1920×1080、H.264、1 FPS、30 張、30 秒。
- 資料：`/home/e114/KITTI_ROOT/training`；預測：`/home/e114/eval_kitti/build/results/kitti/unknown_hwl/pred/data`。
- 選取排序後前 30 個預測 ID，沒有依誤差挑選；明細見 `results/kitti_demo_frames.txt`。這是 KITTI object detection 非連續影像，影片標題已明確註明，不能充當真實行車連續序列。
- 使用 `unknown_hwl` 既有結果，避開名稱為 `base_gt_hwl` 的 GT 尺寸實驗。完整歷史推論命令及權重版本仍未核實；名稱本身不構成無 GT 輔助的充分證據。保留原始 metadata 中所選影格至 `results/kitti_pred_meta.csv`。

| 指標 | 值 |
|---|---:|
| 預測 / GT 車輛數 | 121 / 99 |
| 配對數 | 75 |
| 未配對預測 / GT | 46 / 24 |
| 配對深度 MAE | 18.672400 m |
| 配對深度 RMSE | 26.542384 m |

誤差顯著，僅能展示流程及失效案例，不能據此宣稱 KITTI 精度或產品化驗證已完成。需有時序對應的 KITTI raw/tracking 資料，並以可追溯設定重新推論，才能完成原要求的連續影片。

## 誤差定義與繪圖修正

按類別相同、2D IoU ≥ 0.5，依 IoU 由高到低做一對一貪婪配對；未配對不計入 MAE/RMSE，並另列數量。這不是 KITTI 官方 AP，也不是論文完整評估。修正原腳本「以 3D 距離 < 3 m 篩選、可重複配對 GT」造成大深度誤差被排除的問題。所有配對均計入統計，畫面最多顯示五列。

另外加入缺圖／缺預測／缺 P2 提前失敗、參數驗證、Linux 字型、字型快取、H.264 編碼、JSON 統計，並讓模組可安全 import 供測試。

## 任務 C｜跳過

使用者明確表示已有，無需處理。本次未生成、放大或替換架構圖。

## 任務 D｜RTX 3060 計時：完成，範圍如下

- 本機 GEMO3D commit：`3dd8e9a404d425ebee8bad40040659ddcdc64757`；PyTorch 2.6.0+cu124；GPU NVIDIA GeForce RTX 3060（12 GB）。GPU 為共享環境，未宣稱獨占或跨硬體可比。
- 100 張：同一 Lincoln CARLA 序列 000000–000099；固定尺寸 1.511,2.128,4.902 m。YOLO11n、EgoNet、sed_rank_ratio_linear_model.pkl、1280、FP16、投影回饋 3 次、tightfit max_nfev=15 / k=50。完整參數、權重路徑與 SHA-256 見 `results/reproduce_timing.sh`、`results/timing.json`、`results/input_manifest.json`。
- 相同第一張影像暖機 5 次，接著量測 100 張，每張 CUDA synchronize。量測包含讀圖、YOLO、EgoNet、補償、投影修正、tightfit、預測檔寫入；不含模型初始化、calib 讀取、最終 metadata CSV 寫入。另記錄涵蓋上述全部步驟及暖機的整次 wall time。

| 計時範圍 | 結果 |
|---|---:|
| 暖機後單張流程平均 | 153.560426 ms |
| 暖機後單張流程 FPS | 6.512094 |
| 整次 run wall time（含初始化、暖機、校正檔與 metadata I/O） | 27.685918 s |
| 整次 wall time / 100（含額外暖機成本） | 276.859182 ms/張 |
| 整次 100 張 / wall time | 3.611944 FPS |

這是本次實測，不替代論文原 31.12 FPS，也不宣稱參數與原量測完全一致。計時新推論與任務 A 的歷史預測分開保存；計時 metadata 在 `results/timing_pred_meta.csv`。

## 驗證及交付

- 四項單元測試通過：KITTI bottom-center 幾何、GT 不重複配對、較大深度誤差仍保留、類別與 IoU 條件。
- 兩支影片逐張解碼成功（199/199、30/30），並檢視中間影格確認中文字、3D 框、BEV 與數值可讀。預覽見 `results/preview_sequence.jpg`、`results/preview_kitti.jpg`。
- `results/carla_summary.json`、`results/kitti_summary.json` 包含完整影格清單與逐配對深度。
- `results/predictions/` 保存影片使用的預測檔；`results/input_manifest.json` 保存影像、標註、校正、預測及計時權重的來源與 SHA-256。
- 本機回傳包：`/home/e114/Desktop/gemo3d_results_2026-11-15.zip`（results、程式、測試、報告、改善計畫）。原始資料集與模型權重不重複打包。
- 影片均小於 95 MB，依 README 同步 GitHub。依賴：Python、numpy、opencv-python、Pillow、imageio-ffmpeg；Linux Noto CJK 字型。


## 雲端上傳與協作紀錄｜2026-11-15 08:34（Asia/Taipei）

依使用者要求，已將原成果壓縮檔上傳至 Google Drive：

- [成果壓縮檔下載](https://drive.google.com/file/d/1pZv85YbiBR9JTaJ24XN0BopSRfpYNidn/view?usp=drivesdk)
- [GEMO3D-finals 雲端資料夾](https://drive.google.com/drive/folders/1KhSc-MnMtK0IDHQUKcLMGUAKOs2ynonz)
- 檔名：`gemo3d_results_2026-11-15.zip`；大小：8,090,793 bytes。
- 本機 SHA-256：`8057ca05403736d9a26068f0df2306b3a7dce050c899f6859ef21d3f96d3c5b8`。
- 對應成果 commit：`fdec776f629e9d41ac55d1b197cf0eb8817d1d80`。
- 上傳成功後已透過 Drive metadata 回讀核對檔名、大小及父資料夾；連接器未回傳 checksum，未宣稱完成雲端逐位元校驗。下載後可用上述 SHA-256 驗證。
- 權限：私人／擁有者存取。GitHub 上的連結不代表公開下載；其他 AI 需使用已獲授權的 Drive 連線。此次未擴大分享權限。
- 原 ZIP 作為不可變更的實驗快照保留，內含原始實驗報告；本次上傳紀錄與後續協作文件以 GitHub 最新版本為準，不在原 ZIP 內。
- 機器可讀紀錄：`results/cloud_upload_2026-11-15.json`。

新增 `AGENTS.md` 與 `docs/HANDOFF.md`，記錄使用者的持續協作要求：每次實質修改、實驗、雲端交付或狀態變更，完成驗證後同步更新 GitHub 說明與交接，不只在聊天中回報。這是每次工作時的協作規則，不是背景輪詢服務。
