"""Publish concise findings, scope and outstanding evidence next to full-precision CSVs."""
import csv,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from evaluate_controlled_suite import write_csv
ROOT=Path(__file__).resolve().parent

def main():
 out=ROOT/'results'
 metrics=list(csv.DictReader((out/'controlled_20261116/metrics.csv').open()));allrows={r['method']:r for r in metrics if r['scope']=='all_matched'}
 count=list(csv.DictReader((out/'detection_stats.csv').open()));timing=json.loads((out/'timing_breakdown.json').read_text());fast=json.loads((out/'timing_production_io.json').read_text())
 timing_rows=[]
 for name,v in {**timing['settings'],**fast['settings']}.items():timing_rows.append(dict(setting=name,**{k:v['means_ms'].get(k,0) for k in ['read','yolo','egonet','compensation','projection','tightfit','write','other_ms','total_ms']},fps=v['fps']))
 write_csv(out/'timing_breakdown.csv',timing_rows)
 table='| Setting | Read | YOLO | EgoNet | Comp | Projection | Tightfit | Write | Other | Total ms | FPS |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n'
 for r in timing_rows:table+='| '+r['setting']+' | '+' | '.join(f'{r[k]:.3f}' for k in list(r)[1:])+' |\n'
 (out/'timing_breakdown.md').write_text('''# 共享GPU分段計時（2026-11-16）

## 重點摘要

已量測三種設定各100張，另量測移除無用視角讀圖的FP16版本100張。獨佔GPU與論文原31.12FPS設定仍未核實；reference_fp32只是本次參考設定，不能標為論文設定。

'''+table+'''
## 計時與重現

`python benchmark_stages.py` 執行前三組；`python benchmark_stages.py --production-io` 執行精簡讀圖組。用mono3d環境，輸出資料夾存在時拒絕覆寫。新包含全部逐張時間JSON、CSV與程式。

RTX3060，torch2.6.0+cu124；驅動550.144.03。nvidia-smi前後快照在JSON，CARLA仍在執行，GPU共享。每張及各階段CUDA同步；原樣／插入計時版各推論一次確認預測逐位元一致，再額外暖機5次，接著100張。整次wall time含模型載入與額外7次推論，不能除以100當穩態延遲。

以AST在記憶體插入階段邊界，不改模型核心檔。計時使用exclusive時間：投影中的補償與tightfit扣除後另計，不重複加總；Other含未歸類處理、metadata列組裝與計時同步開銷。各階段之和等於總時間。總時間包含影像I/O與預測TXT寫入，不包含模型初始化、校正讀取、最終metadata CSV寫入。

FP16旗標作用於YOLO，未聲稱EgoNet也轉FP16。此為每設定一次的共享主機診斷，沒有多次獨立run信賴區間，不能單憑FP16差值作硬體性能定論。

## 可重現的讀圖改善

原程式在vis_dir未啟用時仍讀top_bev、fr_iou、side_iou圖；production-io只將三個未使用的視角路徑設None，保留正面影像與相機metadata。100/100個預測TXT與原FP16版本逐位元一致。總時間134.017→89.241ms（約33.4%下降，7.462→11.206FPS），讀取49.888→8.459ms。精簡行為已實作於benchmark_stages.py的可選模式，未悄悄改動使用中的核心repo。

相同100張與先前timing.json來源一致；CLI尺寸與有效尺寸差異仍按formula_check.md揭露。原始計時程式nearest_time_topbev_ncomp_timing.py已找到，但缺能對應論文數字的確切命令／版本，不能宣稱問題完全結案。
''')
 rows=[allrows[n] for n in 'ABCDEF']
 table='| Variant | Matches | Depth RMSE m | MAE m | Bias m | Geometric-center error m | BEV IoU | Yaw error deg |\n|---|---:|---:|---:|---:|---:|---:|---:|\n'
 for r in rows:table+='| '+r['method']+' | '+r['n']+' | '+' | '.join(f'{float(r[k]):.6f}' for k in ['depth_rmse','depth_mae','depth_bias','center_error','bev_iou','yaw_error_deg'])+' |\n'
 (out/'ablation.md').write_text('''# A–F 控制消融：Lincoln CARLA 199影格

## 重點摘要

- 15組控制設定每組199張推論完成；各174個預測、165配對，Precision94.83%、Recall82.91%，34個GT未配對。
- 針孔A→Rank-1 D：深度RMSE 1.694→0.762m。完整F反而1.305m，不能宣稱各模組都改善。
- F關閉tightfit的中心誤差0.471m，開啟後0.752m；10筆出現2D投影IoU上升但3D中心更差。
- 同組的165個配對不是原論文165清單；四種方法含歷史baseline之共同配對只有20筆。另附所有匹配與漏偵測統計。

'''+table+'''
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
''')
 fig,axes=plt.subplots(1,2,figsize=(11,4.2),constrained_layout=True)
 axes[0].bar([r['method'] for r in rows],[float(r['depth_rmse']) for r in rows],color=['#64748b']*3+['#167d9a','#167d9a','#b94c42'])
 axes[0].set(ylabel='Depth RMSE (m)',title='Controlled ablation: 165 matched / 199 GT',ylim=(0,2))
 for i,r in enumerate(rows):axes[0].text(i,float(r['depth_rmse'])+.04,f"{float(r['depth_rmse']):.3f}",ha='center')
 axes[1].barh([r['setting'] for r in timing_rows],[r['total_ms'] for r in timing_rows],color='#167d9a')
 axes[1].set(xlabel='Mean pipeline latency (ms)',title='100 frames per setting; shared RTX 3060')
 fig.savefig(out/'experiment_summary.png',dpi=160);plt.close(fig)

if __name__=='__main__':main()
