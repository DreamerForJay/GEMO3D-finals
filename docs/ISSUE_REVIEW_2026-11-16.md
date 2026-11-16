# 新增 issues 檢視 — 2026-11-16

已讀取 GitHub #1–#8 與上游 f9fe4a7 的 NEXT_EXPERIMENTS.md。本次先處理使用者提出的 PitchLab 圖表查核，沒有將閱讀 issues 視為所有實驗已完成。

| Issue | 主題 | 接續重點 |
|---|---|---|
| [#1](https://github.com/DreamerForJay/GEMO3D-finals/issues/1) | CARLA 實際內參與公式手算 | 11/18 前優先；核對 P2、補償方向、中心定義，找近中遠三例。現有計時 metadata 僅前100張，不可假定涵蓋10m近距。 |
| [#2](https://github.com/DreamerForJay/GEMO3D-finals/issues/2) | 論文設定與獨佔 GPU 速度重測 | 11/18 前優先；分段計時、關閉 tightfit、FP16；先確認歷史設定與GPU工作，不擅自終止其他行程。 |
| [#3](https://github.com/DreamerForJay/GEMO3D-finals/issues/3) | A–F 模組消融 | 先確認165共同樣本協定及完整樣本來源；目前 pair 檔不一定能重建165集合。 |
| [#4](https://github.com/DreamerForJay/GEMO3D-finals/issues/4) | Rank-k／查表／多項式比較 | 需建模比例矩陣與相同測試集；能量占比不能直接代替深度精度。 |
| [#5](https://github.com/DreamerForJay/GEMO3D-finals/issues/5) | 公平性、Precision／Recall、資料切分 | 需要全部預測及GT，不能只用已配對CSV計算召回。 |
| [#6](https://github.com/DreamerForJay/GEMO3D-finals/issues/6) | PitchLab 整理及坡度／焦距／高度 | 本次完成顯示查核與統計對照；全部資料搬入及新條件實驗仍待辦。 |
| [#7](https://github.com/DreamerForJay/GEMO3D-finals/issues/7) | 失敗案例、tightfit、車型誤判 | 需同批樣本受控比較，保留漏偵測與失效案例。 |
| [#8](https://github.com/DreamerForJay/GEMO3D-finals/issues/8) | 模組原圖及KITTI連續影片 | 整體架構圖已存在、使用者曾要求跳過；模組放大圖與KITTI時序另列待辦，不把非連續樣本當完成。 |

協作狀態：本次未留言、關閉 issue 或宣稱新 GPU 實驗完成。每項完成時仍依專案規則回填結果、來源、限制與同步紀錄。
