# 分開看懂的 Demo

Full（F）、未補償（A）、純Rank-1（D）、停用tightfit分開各18秒，使用相同199個來源影格、相同0–40m BEV及0–5m深度誤差尺度（程式固定上限見來源）。其餘三片各12秒：實際tightfit失敗、實際朝向誤差觀察、人工yaw幾何示意。

藍色實線是該流程的預測3D框；橘色虛線是真值；框旁標Z與相機座標朝向ry（度）。Z是前向距離，不是歐氏距離。曲線橫軸來源影格，白線現在，縱軸絕對深度誤差m（yaw_observed則為角度°），斷線是未配對，不是零。

人工yaw_geometry是固定GT尺寸與位置、只改ry的幾何示意；藍框在此片代表人工旋轉，不是推論。不能用它宣稱角度轉換造成模型深度誤差。已查找Desktop、Videos、Downloads、mono3d_predictions等，尚未找到可核實的實際轉角影片及對應推論／GT組合。

來源results/controlled_20261116及results/tightfit_ablation.csv；不重跑推論、不修改原實驗。Full是F完整管線，不是full矩陣補償變體。既有相機時間異常與尺寸映射限制仍適用。

重建：python build_explained_demo.py。
