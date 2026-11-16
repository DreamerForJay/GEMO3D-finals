# 共享GPU分段計時（2026-11-16）

## 重點摘要

已量測三種設定各100張，另量測移除無用視角讀圖的FP16版本100張。獨佔GPU與論文原31.12FPS設定仍未核實；reference_fp32只是本次參考設定，不能標為論文設定。

| Setting | Read | YOLO | EgoNet | Comp | Projection | Tightfit | Write | Other | Total ms | FPS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| reference_fp32 | 58.159 | 16.835 | 35.396 | 0.456 | 1.291 | 28.858 | 0.111 | 1.328 | 142.434 | 7.021 |
| no_tightfit_fp32 | 52.405 | 16.205 | 34.956 | 0.299 | 0.891 | 0.000 | 0.102 | 0.675 | 105.533 | 9.476 |
| fp16 | 49.888 | 16.866 | 35.807 | 0.465 | 1.319 | 28.863 | 0.107 | 0.701 | 134.017 | 7.462 |
| production_io_fp16 | 8.459 | 16.282 | 33.866 | 0.452 | 1.231 | 28.144 | 0.106 | 0.702 | 89.241 | 11.206 |

## 計時與重現

`python benchmark_stages.py` 執行前三組；`python benchmark_stages.py --production-io` 執行精簡讀圖組。用mono3d環境，輸出資料夾存在時拒絕覆寫。新包含全部逐張時間JSON、CSV與程式。

RTX3060，torch2.6.0+cu124；驅動550.144.03。nvidia-smi前後快照在JSON，CARLA仍在執行，GPU共享。每張及各階段CUDA同步；原樣／插入計時版各推論一次確認預測逐位元一致，再額外暖機5次，接著100張。整次wall time含模型載入與額外7次推論，不能除以100當穩態延遲。

以AST在記憶體插入階段邊界，不改模型核心檔。計時使用exclusive時間：投影中的補償與tightfit扣除後另計，不重複加總；Other含未歸類處理、metadata列組裝與計時同步開銷。各階段之和等於總時間。總時間包含影像I/O與預測TXT寫入，不包含模型初始化、校正讀取、最終metadata CSV寫入。

FP16旗標作用於YOLO，未聲稱EgoNet也轉FP16。此為每設定一次的共享主機診斷，沒有多次獨立run信賴區間，不能單憑FP16差值作硬體性能定論。

## 可重現的讀圖改善

原程式在vis_dir未啟用時仍讀top_bev、fr_iou、side_iou圖；production-io只將三個未使用的視角路徑設None，保留正面影像與相機metadata。100/100個預測TXT與原FP16版本逐位元一致。總時間134.017→89.241ms（約33.4%下降，7.462→11.206FPS），讀取49.888→8.459ms。精簡行為已實作於benchmark_stages.py的可選模式，未悄悄改動使用中的核心repo。

相同100張與先前timing.json來源一致；CLI尺寸與有效尺寸差異仍按formula_check.md揭露。原始計時程式nearest_time_topbev_ncomp_timing.py已找到，但缺能對應論文數字的確切命令／版本，不能宣稱問題完全結案。
