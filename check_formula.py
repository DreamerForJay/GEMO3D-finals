"""Recompute actual calibration/ratio examples; preserve unrounded values and input hashes."""
import csv
import hashlib
import json
from pathlib import Path
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parent
SOURCE = Path('/home/e114/Desktop/mono3d/GEMO3D')
DATA = Path('/home/e114/KITTI_ROOT/sed_lincoln_fr_T1R8/data/KITTIDataset_Carla/training')
sys.path.insert(0, str(SOURCE))
from submodule.compensation import _load_models, _predict_rank_ratio

def main():
    model_path = SOURCE / 'comp/sed_rank_ratio_linear_model.pkl'
    model = _load_models(str(model_path))
    meta = ROOT / 'results/formula_pred_meta.csv'
    records = list(csv.DictReader(meta.open(encoding='utf-8-sig')))
    assert len(records) == 3
    inputs = [meta, model_path, SOURCE/'submodule/compensation.py', SOURCE/'submodule/pipeline.py', SOURCE/'submodule/config.py', SOURCE/'submodule/geometry.py']
    rows = []
    for r in records:
        frame = r['image_id']
        calib, label, image = [DATA / folder / (frame+ext) for folder,ext in [('calib','.txt'),('label_2','.txt'),('image_2','.png')]]
        inputs.extend([calib,label,image])
        p2 = [float(v) for line in calib.read_text().splitlines() if line.startswith('P2:') for v in line.split()[1:]]
        labels = [line.split() for line in label.read_text().splitlines() if line.split()[0]=='Car']
        assert len(labels)==1 and float(r['gt_match_iou2d']) >= .5
        gt = float(labels[0][13]); height = 1.511
        raw = p2[5]*height/float(r['pred_bbox_h_px'])
        assert abs(raw-float(r['z_est'])) < 1e-9
        ratio = _predict_rank_ratio(float(r['yaw_comp_deg_final']), raw, model)
        corrected = raw*ratio
        assert abs(corrected-(raw-float(r['comp_final']))) < 1e-9
        final = float(r['z_final'])
        rows.append(dict(frame=frame,fy=p2[5],cy=p2[6],H_used=height,h_2D=float(r['pred_bbox_h_px']),Z_raw=raw,r_hat=ratio,Z_corr=corrected,Z_final=final,GT_z=gt,corr_signed_error=corrected-gt,final_signed_error=final-gt,pred_h=float(r['pred_h']),pred_w=float(r['pred_w']),pred_l=float(r['pred_l']),iou=float(r['gt_match_iou2d']),P2=p2,image_size=Image.open(image).size))
    hashes = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    result = dict(rows=rows,input_sha256=hashes,height_sensitivity={str(z):-z*z/(721.5377*1.511) for z in (20,30)})
    (ROOT/'results/formula_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    columns=['frame','fy','H_used','h_2D','Z_raw','r_hat','Z_corr','Z_final','GT_z','corr_signed_error','final_signed_error']
    table='| '+' | '.join(columns)+' |\n| '+' | '.join(['---']*len(columns))+' |\n'
    for row in rows: table+='| '+' | '.join(f'{row[c]:.6f}' if isinstance(row[c],float) else row[c] for c in columns)+' |\n'
    text='''# CARLA 公式查核（2026-11-16，issue #1）

## 實際校正

三張影像的 P2 相同，影像 1242×375。f_y=721.537700 px、c_y=172.854000 px。這是資料集校正檔實值，雖與 KITTI 常見數值相同，不能用其他假設值替換；尚未獨立核對 CARLA 產生器的相機設定。

```
P2 = [[721.537700, 0, 609.559300, 0],
      [0, 721.537700, 172.854000, 0],
      [0, 0, 1, 0]]
```

## 近、中、遠距新推論

依 GT 距離最接近 10、20、30 m 選 000170、000110、000043，沒有依預測誤差挑選。每張 1 個 GT、1 個預測，2D IoU 均 ≥ 0.5。只用 GT 選距離與事後評估，不用 GT 推論。原 timing 的前 100 張不涵蓋 10 m，故另跑 3 張；這不是整體效能評估。單位：高度與深度 m，框高與焦距 px；誤差為預測減 GT。

'''+table+'''
## 方向與中心定義

- pipeline.py：固定尺寸模式下 H_used 取 CLI `--height_m 1.511`，不是 metadata 的 pred_h。Z_raw=f_y H_used/h_2D。
- compensation.py 的模型載入註解定義 r=h_2D/h3D_proj；推論使用 Z_corr=Z_raw*r，內部以 comp=Z_raw*(1-r) 儲存，故 Z_corr=Z_raw-comp。comp_final 是公尺差值，不是比例。
- 三筆均獨立重新插值模型的 r(theta_final,Z_raw)，確認乘法與 metadata 相差 <1e-9。此為最後一次角度對應的純補償深度；Z_final 含後續平移求解、tightfit，不能替代為 Z_corr。
- 若 h3D_proj 指理想直立高度 f_y H/Z，則由代數得 r=h_2D/h_ideal，應乘 r；若改定義為倒數才應除。建模腳本 plot_rank1_ratio_linear_svd.py 未在本機找到，因此訓練端分母的幾何定義尚未獨立驗證，N3 不標全部完成。
- geometry.py 定義 KITTI (x,y,z) 為底部中心，幾何中心為 (x,y-h/2,z)，本實作兩者 Z 相同；不能把 y 的 h/2 差誤套到 Z。Blender 建模端中心尚待原始腳本核對。

## 新發現：CLI 尺寸與實際尺寸不同

傳入 fixed_dims_hwl=1.511,2.128,4.902，但 config.py 的 resolve_fixed_dims_hwl_for_k 依 sedan 映射覆蓋為 **1.52,1.64,3.86**，三筆 pred_h/w/l 均證實。H_used 仍為 1.511。先前計時文件所列 Lincoln 尺寸只是 CLI 輸入，不代表實際建框尺寸；本報告更正此解讀。為保持可比較性，本次未修改模型核心或重寫舊結果；後續消融須明確控制車型尺寸映射。

## 一像素敏感度

對 Δh=+1 px，ΔZ≈−Z²/(f_y H)；H=1.511 m：
'''
    for z,v in result['height_sensitivity'].items(): text+=f'- {z} m：{v:.9f} m/px（框越高，估計深度越小）。\n'
    text+='''
這是針孔原始深度的局部線性近似，未包含比例模型、角度或 tightfit 的導數，不是最終系統誤差保證。

## 重現與限制

在 repo 根目錄執行 `bash results/reproduce_formula.sh`，將該腳本輸出的 pred_meta.csv 複製為 results/formula_pred_meta.csv，再以 mono3d Python 執行 `check_formula.py`。JSON 保存全精度數值與輸入、模型、來源碼 SHA-256。

GEMO3D commit 3dd8e9a404d425ebee8bad40040659ddcdc64757；RTX 3060、PyTorch 2.6.0+cu124、驅動550.144.03；imgsz1280、FP16、投影3次、tightfit15/k50。完整 CLI 見 reproduce_formula.sh。GPU 共享（CARLA 約4120 MiB、當時使用率97%），本次沒有量測速度。原論文參數對應與訓練端定義未核實，issue #1 保留待核對部分。
'''
    (ROOT/'results/formula_check.md').write_text(text)
    print(table)

if __name__=='__main__': main()
