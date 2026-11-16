# A–F 控制消融：Lincoln CARLA 199影格

## 重點摘要

- 15組控制設定每組199張推論完成；各174個預測、165配對，Precision94.83%、Recall82.91%，34個GT未配對。
- 針孔A→Rank-1 D：深度RMSE 1.694→0.762m。完整F反而1.305m，不能宣稱各模組都改善。
- F關閉tightfit的中心誤差0.471m，開啟後0.752m；10筆出現2D投影IoU上升但3D中心更差。
- 同組的165個配對不是原論文165清單；四種方法含歷史baseline之共同配對只有20筆。另附所有匹配與漏偵測統計。

| Variant | Matches | Depth RMSE m | MAE m | Bias m | Geometric-center error m | BEV IoU | Yaw error deg |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 165 | 1.693514 | 1.642990 | -1.531136 | 1.667135 | 0.357894 | 2.753433 |
| B | 165 | 1.349260 | 0.963862 | 0.590319 | 1.004355 | 0.502599 | 2.753433 |
| C | 165 | 1.431420 | 1.029012 | 0.766016 | 1.080256 | 0.489347 | 2.753433 |
| D | 165 | 0.762169 | 0.453590 | -0.009136 | 0.550693 | 0.560608 | 2.753433 |
| E | 165 | 0.762169 | 0.453590 | -0.009136 | 0.515797 | 0.560608 | 2.753433 |
| F | 165 | 1.305077 | 0.734919 | -0.387560 | 0.752493 | 0.529984 | 2.309610 |

## 設定差異與控制

A 無比例、無地面、bbox_bottom回投影；B加訓練網格平均比例；C加各角度平均比例；D加Rank-1；E加相機extrinsics推導的道路平面；F再開投影回饋3次與tightfit15/k50。F_no_tightfit保留回饋、只關tightfit。A–D完全不讀metadata；E/F僅以camera extrinsics推地面，使用已知模擬校正，不宣稱視覺估測未知路面。

全部用YOLO11n、EgoNet、conf0.25、imgsz1280、YOLO FP16，pred_center_source=bbox、label_path=None，沒有GT尺寸／高度／中心捷徑。相同偵測數與匹配集合已核對。

主實驗保留現有sedan尺寸映射1.52,1.64,3.86，H_used=1.511。F_cli_dims另強制CLI指定1.511,2.128,4.902，RMSE反而2.134m；它是尺寸干預，不能不經其他條件核實就稱為精度修復。錯誤車型測試同時替換車型尺寸、高度先驗與補償模型，沒有重新訓練，是配置敏感度，不等於分類器真實誤判率。

## 指標與精度

按Car類別、2D IoU≥0.5由高至低一對一匹配，不設深度誤差篩選；全部預測含未匹配另列。中心誤差使用幾何中心(x,y−h/2,z)，另保留底部中心誤差；yaw以wrap到±π的絕對誤差。BEV採KITTI的長沿局部X、寬沿Z、相機Y旋轉，交集由OpenCV凸多邊形求得（float32），四個已知幾何案例驗證。投影IoU是3D框投影對偵測2D框，不是GT投影IoU。

統計使用輸出KITTI TXT的原有小數精度，CSV保留重算浮點值，不能宣稱比來源TXT更高精度。predictions.json保存所有比較方法預測；manifest包含逐檔雜湊、影格清單、指令、有效設定。baseline為歷史結果，原score門檻及訓練設定未完全核實，因此只能說檔案輸出的計數，不能宣稱公平SOTA排名。MonoAMNet保留所有現有候選，低precision可能受閾值影響，未為美化而另調閾值。

## 重現

在repo根目錄以mono3d Python依序執行：

```
python run_controlled_suite.py --output benchmark_output/controlled_20261116
python run_controlled_suite.py --output benchmark_output/poly_direct_20261116 --variants poly2_direct
python evaluate_controlled_suite.py --run benchmark_output/controlled_20261116
python build_experiment_reports.py
python summarize_controlled_suite.py
```

推論拒絕覆寫既有variant目錄。SOURCE/DATA路徑見腳本，環境與SHA256在controlled_20261116/manifest.json。舊影片、舊推論與模型核心保持原樣。原論文同資料／同165清單驗證仍需補來源，不能把此替代實驗標成論文完整重現。
