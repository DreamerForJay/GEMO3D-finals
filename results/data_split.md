# 資料切分與來源查核（2026-11-16）

## 重點摘要

本次新實驗的15組設定使用完全相同的199張Lincoln CARLA影像；偵測框逐張一致。舊四方法pairs卻混有不同GT，不能用相同影格ID連接成公平比較。原訓練CSV尚缺，因此**尚不能證明完整訓練／測試無洩漏**。

| 項目 | 補償建模來源 | 本次測試 |
|---|---|---|
| 車型 | 模型used_columns記錄SED_SUPB/angle_depth_sweep/sed_pose_log_with_corners.csv；原CSV未取得 | metadata blueprint=vehicle.lincoln.mkz_2017 |
| 尺寸 | 原CAD尺寸未核實 | metadata L/W/H約4.901683/2.128324/1.510746m；KITTI標註取三位小數 |
| 相機 | 建模原始內參／高度未核實 | P2及metadata均fy=721.5377，cy=172.854；1242×375 |
| 距離 | 模型depth_grid 3.1651–40.0913，metadata稱推論raw深度軸 | GT Z約5.158–35.773m，完整199影格 |
| 角度 | 90格、0–180度；4916建模資料列（模型自述，未重讀CSV） | 此序列GT yaw近90度；不是全角度驗證 |
| 切分 | 無原訓練清單，CAD是否同源仍需核對 | 固定val清單，沒有按誤差挑選；全部漏偵測保留 |

模型PKL已包含R_original_grid、R_reconstructed_grid、b_theta、奇異值與used_columns。本次B/C/Rank2/Rank3/Full/poly僅從已存在的原模型網格計算，沒有用本次CARLA GT擬合；此事不等於證明原模型訓練來源完全無洩漏。

## 四方法公平性限制

新評估使用同一Lincoln標註、IoU≥0.5、一對一配對，199個GT：GEMO3D F為174預測／165匹配；MonoDETR歷史檔88／80；MonoDGP174／115；MonoAMNet3152／143。Precision/Recall見detection_stats.csv。

三個歷史baseline的val_dataset/training符號連結目前指向同一Lincoln資料夾；但缺完整歷史訓練權重／置信度閾值／生成命令及當時輸入雜湊，不能保證歷史檔在同一操作點生成。特別是MonoAMNet候選數很多，沒有為美化precision自行加分數門檻。因此這是現存輸出檔的計數核對，尚非同設定SOTA公平比較。

另外舊mono3d_comparison_fr的GEMO3D與其他三方法GT不同，詳見historical_165_audit.md；舊0.70→0.82摘要只保留為未重新驗證歷史數字。新四方法共同集合20筆、新控制實驗共同165筆、舊論文165筆三者不能混稱。

## 後續必需資料

原Blender建模腳本、CAD/尺寸清單、sweep CSV及訓練清單；原論文165個共同物件的完整來源；各baseline生成指令／權重及分數閾值。取得後才能完成無洩漏證明與原論文同條件比較。
