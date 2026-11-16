# 模型儲存盤點（部分完成）

補償比較的runtime與理論因子儲存值見compensation_compare.csv。現有Rank-1推論載入完整90×80網格，不是只用低秩因子部署；不可拿理論430個值直接宣稱現在模型儲存只有430個值。

model_storage.json記錄本機MonoDGP／MonoDETR checkpoint大小、SHA256及model_state tensor元素數。MonoDGP為43,334,896個tensor元素、173,339,584bytes；MonoDETR為38,380,527個、153,522,108bytes。這些含buffer，不冒稱全部都是可訓練參數；checkpoint另外包含optimizer，檔案大小不等於部署權重大小。尚未單獨核實MonoDGP誤差頭參數量，N9仍是部分完成。

方法：以mono3d環境torch.load(path,map_location='cpu',weights_only=False)讀取既有可信模型檔，取model_state中的Tensor，累加numel及numel×element_size；未改權重，也未上傳checkpoint。
