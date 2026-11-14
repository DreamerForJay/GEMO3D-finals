# -*- coding: utf-8 -*-
"""GEMO3D demo：串接既有之論文成果視覺化（CARLA 輸入、針孔深度、比例補償、3D 重建、10/20/30 m 預測），加中文說明。"""
import os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
G = r'C:\Users\clyan\OneDrive\Desktop\EX\paper\GEMO3D'
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, 'GEMO3D_demo.mp4')
FONT = r'C:\Windows\Fonts\msjhbd.ttc'
fb = ImageFont.truetype(FONT, 46); fm = ImageFont.truetype(FONT, 32); fs = ImageFont.truetype(FONT, 24)
W, Hh, FPS = 1920, 1080, 30
vw = cv2.VideoWriter(OUT, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (W, Hh))
BG = (18, 28, 48)

def frame_with(img_bgr, cap, step):
    canvas = Image.new('RGB', (W, Hh), BG); dr = ImageDraw.Draw(canvas)
    dr.text((60, 30), step, font=fm, fill=(255, 190, 120))
    ih, iw = img_bgr.shape[:2]; sc = min((W - 120) / iw, (Hh - 260) / ih)
    im = cv2.resize(img_bgr, (int(iw * sc), int(ih * sc)))
    canvas.paste(Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)), ((W - im.shape[1]) // 2, 110))
    w = dr.textlength(cap, font=fm); dr.text(((W - w) / 2, Hh - 120), cap, font=fm, fill=(255, 255, 255))
    return cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)

def card(lines, sec):
    im = Image.new('RGB', (W, Hh), BG); dr = ImageDraw.Draw(im); y = 380
    for t, f, c in lines:
        w = dr.textlength(t, font=f); dr.text(((W - w) / 2, y), t, font=f, fill=c); y += f.size + 28
    fr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    for _ in range(int(FPS * sec)): vw.write(fr)

def clip(path, cap, step, loops=1):
    for _ in range(loops):
        c = cv2.VideoCapture(path)
        while True:
            ok, x = c.read()
            if not ok: break
            vw.write(frame_with(x, cap, step))

def still(path, cap, step, sec):
    x = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR); fr = frame_with(x, cap, step)
    for _ in range(int(FPS * sec)): vw.write(fr)

card([('GEMO3D 單目 3D 車輛偵測 系統展示', fb, (255, 255, 255)),
      ('一顆前視相機 → 車輛 3D 位置、尺寸與朝向', fm, (190, 210, 240))], 3)
clip(os.path.join(G, r'video\gemo3d-intro\assets\carla.mp4'), '輸入：CARLA 模擬之車載前視相機影像（單張 RGB）', 'STEP 0　輸入影像')
clip(os.path.join(G, r'docs\assets\loop-pinhole.mp4'), '針孔模型：由車高 H 與 2D 框高度 h 計算初始深度 Z_raw = f·H / h', 'STEP 1–2　2D 偵測與初始深度')
clip(os.path.join(G, r'docs\assets\loop-ratio.mp4'), 'Rank-1 投影高度比例模型：依觀測角與深度校正 Z_corr', 'STEP 3　深度補償')
clip(os.path.join(G, r'docs\assets\loop-reconstruct.mp4'), '反投影、道路平面約束、投影一致性修正 → 3D 車框', 'STEP 4　3D 重建')
for d in (10, 20, 30):
    still(os.path.join(G, rf'docs\assets\prediction-{d}m.webp'), f'約 {d} m 之車輛：藍色為 GEMO3D 3D 框，鳥瞰圖橘色虛線為真實位置', 'CARLA 評估序列結果', 3.5)
still(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img', 'gc_13.png'), '同一車輛由近至遠：GEMO3D 於 CARLA 序列輸出之 3D 車框', 'CARLA 評估序列結果', 4)
card([('CARLA 雙向道路 · 165 個共同樣本（5–35 m）', fm, (190, 210, 240)),
      ('3D 中心誤差 0.25 m　·　BEV IoU 0.82　·　31.12 FPS（RTX 3060）', fb, (255, 255, 255)),
      ('3D 位置由相機幾何計算，每一步可檢驗', fm, (255, 190, 120))], 4)
vw.release(); print(OUT)
