# -*- coding: utf-8 -*-
"""把 GEMO3D 的 KITTI 格式預測畫成連續 demo 影片：左為相機影像（藍：GEMO3D 3D 框；橘虛線：真值），
右為鳥瞰圖（1 m 格線）與逐車深度誤差。

用法（KITTI 格式資料夾：image_2/、calib/、label_2/ 可選）：
  python render_sequence_video.py --kitti_root <.../training> --pred_dir <OUT>/pred/data \
      --frames 000000-000300 --fps 10 --out results/GEMO3D_demo_sequence.mp4
  # 或以 ImageSets 指定：--split_file <.../ImageSets/val.txt>
無 label_2 時（例如真實道路影片）只畫預測。
"""
import os, argparse, subprocess, shutil, json, functools, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont


def ids():
    if a.split_file: return [l.strip() for l in open(a.split_file) if l.strip()]
    if a.frames:
        s, e = a.frames.split('-'); n = len(s); return [str(i).zfill(n) for i in range(int(s), int(e) + 1)]
    return sorted(f[:-4] for f in os.listdir(a.pred_dir) if f.endswith('.txt'))

def P2(fid):
    for l in open(os.path.join(a.kitti_root, 'calib', fid + '.txt')):
        if l.startswith('P2:'): return np.array(l.split()[1:], float).reshape(3, 4)

def objs(path):
    out = []
    if not os.path.exists(path): return out
    for l in open(path):
        v = l.split()
        if len(v) < 15 or v[0] in ('DontCare',): continue
        h, w, L, x, y, z, ry = map(float, v[8:15]); out.append(dict(t=v[0], h=h, w=w, l=L, x=x, y=y, z=z, ry=ry, box=list(map(float, v[4:8]))))
    return out

def corners(o):
    l, w, h = o['l'], o['w'], o['h']
    xc = [l/2, l/2, -l/2, -l/2, l/2, l/2, -l/2, -l/2]; yc = [0, 0, 0, 0, -h, -h, -h, -h]; zc = [w/2, -w/2, -w/2, w/2, w/2, -w/2, -w/2, w/2]
    R = np.array([[np.cos(o['ry']), 0, np.sin(o['ry'])], [0, 1, 0], [-np.sin(o['ry']), 0, np.cos(o['ry'])]])
    return R @ np.array([xc, yc, zc]) + np.array([[o['x']], [o['y']], [o['z']]])

EDGES = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]

def draw_box(img, o, P, color, dashed=False):
    c = corners(o)
    if (c[2] < 0.1).any(): return
    p = P @ np.vstack([c, np.ones(8)]); p = (p[:2] / p[2]).T.astype(int)
    for i, j in EDGES:
        if dashed:
            n = 10
            for k in range(0, n, 2):
                a_ = p[i] + (p[j] - p[i]) * k / n; b_ = p[i] + (p[j] - p[i]) * (k + 1) / n
                cv2.line(img, tuple(a_.astype(int)), tuple(b_.astype(int)), color, 2, cv2.LINE_AA)
        else:
            cv2.line(img, tuple(p[i]), tuple(p[j]), color, 3, cv2.LINE_AA)

def match(preds, gts):
    # Class-aware one-to-one 2D IoU matching; depth remains an independent metric.
    candidates = []
    for i, p in enumerate(preds):
        for j, g in enumerate(gts):
            if p['t'].lower() != g['t'].lower(): continue
            x1, y1, x2, y2 = p['box']; u1, v1, u2, v2 = g['box']
            inter = max(0, min(x2, u2)-max(x1, u1))*max(0, min(y2, v2)-max(y1, v1))
            union = max(0, x2-x1)*max(0, y2-y1)+max(0, u2-u1)*max(0, v2-v1)-inter
            iou = inter/union if union > 0 else 0
            if iou >= 0.5: candidates.append((iou, i, j))
    assignments = {}; used = set()
    for _, i, j in sorted(candidates, reverse=True):
        if i not in assignments and j not in used:
            assignments[i] = gts[j]; used.add(j)
    return [(p, assignments.get(i)) for i, p in enumerate(preds)]

def main():
    global a
    ap = argparse.ArgumentParser()
    ap.add_argument('--kitti_root', required=True); ap.add_argument('--pred_dir', required=True)
    ap.add_argument('--frames', default=''); ap.add_argument('--split_file', default='')
    ap.add_argument('--fps', type=int, default=10); ap.add_argument('--out', default='results/GEMO3D_demo_sequence.mp4')
    ap.add_argument('--title', default='GEMO3D 單目 3D 車輛偵測')
    ap.add_argument('--summary_json', default='')
    ap.add_argument('--font', default='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'); ap.add_argument('--bev_range', type=float, default=40)
    a = ap.parse_args()
    if a.fps <= 0 or a.bev_range <= 0: ap.error('fps and bev_range must be positive')
    if a.frames and a.split_file: ap.error('choose frames OR split_file')
    if not a.out.endswith('.mp4'): ap.error('out must end with .mp4')

    @functools.lru_cache()
    def font(size): return ImageFont.truetype(a.font, size)
    font(22)
    frame_ids = ids()
    if not frame_ids or len(frame_ids) != len(set(frame_ids)): raise ValueError('empty or duplicate frame IDs')
    for fid in frame_ids:
        if not fid.isdigit(): raise ValueError('frame IDs must be numeric')
        for directory, suffix in [('image_2', '.png'), ('calib', '.txt')]:
            path = os.path.join(a.kitti_root, directory, fid+suffix)
            if not os.path.isfile(path): raise FileNotFoundError(path)
        path = os.path.join(a.pred_dir, fid+'.txt')
        if not os.path.isfile(path): raise FileNotFoundError(path)
        if P2(fid) is None: raise ValueError('missing P2: '+fid)
    W, H = 1920, 1080; tmp = a.out.replace('.mp4', '_raw.mp4'); os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*'mp4v'), a.fps, (W, H)); errs = []; rows = []; pred_count = 0; gt_count = 0
    if not vw.isOpened(): raise RuntimeError('Cannot open video writer')
    for fid in frame_ids:
        ip = os.path.join(a.kitti_root, 'image_2', fid + '.png')
        if not os.path.exists(ip): raise FileNotFoundError(ip)
        img = cv2.imread(ip); P = P2(fid)
        preds = objs(os.path.join(a.pred_dir, fid + '.txt')); gts = objs(os.path.join(a.kitti_root, 'label_2', fid + '.txt'))
        gts = [g for g in gts if g['t'] in ('Car', 'Van', 'Truck', 'car')]
        for g in gts: draw_box(img, g, P, (40, 140, 255), dashed=True)
        for p in preds: draw_box(img, p, P, (255, 120, 30))
        sc = min(1300 / img.shape[1], 1000 / img.shape[0]); im = cv2.resize(img, (int(img.shape[1] * sc), int(img.shape[0] * sc)))
        cv = Image.new('RGB', (W, H), (245, 247, 250)); cv.paste(Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)), (20, 70))
        d = ImageDraw.Draw(cv); d.text((20, 15), f'{a.title}　影格 {fid}', font=font(32), fill=(20, 43, 76))
        d.text((20, 75 + im.shape[0]), '藍：GEMO3D 3D 框　橘色虛線：真值', font=font(22), fill=(80, 90, 105))
        bx, by, bw, bh = 1360, 70, 540, 640; d.rectangle([bx, by, bx + bw, by + bh], fill='white', outline=(180, 190, 200))
        R = a.bev_range; s2 = bh / R
        for m in range(0, int(R) + 1, 1):
            y = by + bh - m * s2; d.line([bx, y, bx + bw, y], fill=(225, 230, 236) if m % 5 else (190, 198, 208))
        d.text((bx + 6, by + 4), f'鳥瞰圖（前方 {int(R)} m，1 m 格線）', font=font(18), fill=(80, 90, 105))
        cam = (bx + bw / 2, by + bh); d.polygon([cam, (cam[0] - 8, cam[1] - 14), (cam[0] + 8, cam[1] - 14)], fill=(20, 43, 76))
        def foot(o, col, w_):
            c = corners(o)[[0, 2]][:, :4].T; pts = [(cam[0] + x * s2, cam[1] - z * s2) for x, z in c]; d.polygon(pts + [pts[0]], outline=col, width=w_)
        for g in gts: foot(g, (255, 140, 40), 2)
        for p in preds: foot(p, (30, 120, 255), 3)
        y0 = by + bh + 20
        pairs = match(preds, gts); pred_count += len(preds); gt_count += len(gts)
        for p, g in pairs:
            if g:
                errs.append(abs(p['z']-g['z']))
                rows.append(dict(frame_id=fid, pred_z=p['z'], gt_z=g['z'], depth_error_m=p['z']-g['z']))
        for p, g in pairs[:5]:
            if g: e = p['z'] - g['z']; t = f'深度 {p["z"]:.2f} / GT {g["z"]:.2f} m　ΔZ {e:+.2f} m'
            else: t = f'預測深度 {p["z"]:.2f} m'
            d.text((bx, y0), t, font=font(18), fill=(20, 43, 76)); y0 += 34
        vw.write(cv2.cvtColor(np.array(cv), cv2.COLOR_RGB2BGR))
    vw.release()
    ff = shutil.which('ffmpeg')
    if not ff:
        try:
            import imageio_ffmpeg
            ff = imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError: pass
    if ff:
        subprocess.run([ff, '-y', '-loglevel', 'error', '-i', tmp, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', a.out], check=True); os.remove(tmp)
    else: os.replace(tmp, a.out)
    print('saved', a.out, '| matched objects', len(errs), '| mean |depth err| %.3f m' % (np.mean(errs) if errs else float('nan')))

    summary = dict(frames=len(frame_ids), fps=a.fps, duration_s=len(frame_ids)/a.fps,
                   first_frame=frame_ids[0], last_frame=frame_ids[-1],
                   kitti_root=os.path.abspath(a.kitti_root), pred_dir=os.path.abspath(a.pred_dir),
                   predictions=pred_count, ground_truth=gt_count, matched_objects=len(errs),
                   matching='class-aware greedy one-to-one 2D IoU >= 0.5; visualization only, not AP',
                   depth_mae_m=float(np.mean(errs)) if errs else None,
                   depth_rmse_m=float(np.sqrt(np.mean(np.square(errs)))) if errs else None,
                   codec='h264' if ff else 'mp4v', frame_ids=frame_ids, matched_depths=rows)
    if a.summary_json:
        with open(a.summary_json, 'w') as f: json.dump(summary, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
