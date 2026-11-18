# 中英文大字版 + 朝向角機制分片

28支影片：原12種單方法／成對視角各有中文、英文版（24支10秒），另有支撐點／深度偏差兩支幾何示意各兩語（4支12秒）。index.html可切換影片與語言，保留播放時間。數值54px，放在專用142px標頭；實測影片不塞入圖表。

## 朝向機制與定義

- 藍色長方體代表車輛外接盒，不是真實車身mesh。固定尺寸H1.511/W2.128/L4.902m，中心Z10m，底部Y1.65m，fy721.5377px，無pitch，只掃yaw0–180°。本設定yaw亦為觀測角（X=0）；長方體幾何180°週期。
- h2D=max(v)-min(v)，由8角點精確透視投影得到；黃點標上下極值，重合極值只選一個頂點。淡藍車頭標記與方向盤顯示旋轉。h_ideal=fy*H/Z是同中心深度直立線段的投影高度，綠線為固定參考。
- r=h2D/h_ideal，Z_pinhole=fy*H/h2D=Z/r，bias=Z_pinhole-Z。第一片看高度比例，第二片看距離偏差，無曲線混入。
- 這不是原始Blender訓練資料的h3D,proj重現；其分母原始建模定義尚未核實。不使用GT比例校正來冒充模型改善，也不是實測轉角因果影片。不能推廣這個長方體的幅度／符號至所有車輛輪廓與相機姿態。
- yaw_geometry.csv是獨立合成數據；per_frame.csv/summary.json才是controlled_20261116實測輸出。實測數值和未配對計數均不變，既有同步／尺寸先驗限制保留。

## 重建與驗證

python build_bilingual_demo.py → python build_bilingual_catalog.py → python validate_bilingual_demo.py；網頁：node validate_bilingual_page.cjs。依賴既有build_clean_demo.py、build_demo_assets.py及原本資料根目錄。raw資料與權重不包含在包中。

## 名詞

針孔基準=Pinhole；Rank-1補償=Rank-1；完整流程=Full；停用貼合=no tightfit；俯視重疊率=BEV IoU；3D中心誤差=3D center error；上下支撐點=height supports；理想高度=ideal height；深度偏差=depth bias。
