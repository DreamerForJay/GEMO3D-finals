# 清爽比較素材（取代解說密集版作為預設入口）

開啟 index.html：一次只播放一種比較／視角。12 支 10 秒影片：四種設定各自前視、俯視，加上 A/D 與 F_no_tightfit/F 的前視、俯視比較。所有影片保留199來源影格，沒有圖表、說明段落、片尾卡；只留方法名與一個當幀指標。

- 綠色虛線＝GT；紅色實線＝預測。前視為3D框，俯視為同一水平面上的框底面投影，非車頂輪廓。
- 真實 CARLA top_camera RGB，利用每幀前視／俯視外參轉換，不是格線示意或生成影像。
- BEV IoU以公尺XZ平面計算，不能將影像像素IoU當正式指標；各框統一投影到GT底部Y，讓顯示對應BEV定義，忽略預測高度偏差。
- unmatched保留，不當0；所有預測框仍畫出。summary.json為全199張配對統計；per_frame.csv為配對明細，未配對數在summary保留。
- 誤差曲線獨立center_error.png，橫軸影格、縱軸3D幾何中心誤差m；缺值斷線。影片上3D error不等於深度RMSE。
- Full指F完整流程；來源controlled_20261116，並非新推論或公平跨模型比較。資料三處重複timestamp/frame仍保留；按image ID配對，不保證嚴格時間同步。
- 所有影片離線30fps重取樣、10秒，不是實測推論效能。沒有新增真實轉角因果影片。

重建：python build_clean_demo.py → python build_clean_catalog.py；驗證：python validate_clean_demo.py。前視比較上下排列以保留原始寬幅解析度；俯視左右排列。所有單方法片可單獨嵌入其他網頁。

參考：MoGe-3 分開展示、Scal3R 分視角、GaMO 方法切換、RL-AWB 前後比較。沿用 docs/DEMO_REFERENCE_REVIEW.md 八頁對照。
