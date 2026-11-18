# 失敗案例

遠距取新CARLA完整流程中GT>30m的最大深度誤差3張；tightfit取2D投影IoU升但中心誤差增加最大的3張；車型敏感度為強制SUV配置的最大中心誤差3張，這是人為干預，**不是觀測到分類器真的誤判**。

CARLA本序列所有標註occlusion/truncation皆0，不能虛構遮擋案例。遮擋／截斷改用既有KITTI展示30張中的標註，依嚴重度取不同影格各3張。KITTI為歷史推論，原權重／完整參數未核實；僅供失敗展示，不納入CARLA消融。未配對以UNMATCHED呈現，不填造深度誤差。

全部tightfit前後數值在../../tightfit_ablation.csv；所有配對含較差結果在../../controlled_20261116/pairs.csv。
