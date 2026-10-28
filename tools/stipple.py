# A spray can's overspray as real droplets: crisp round dots scattered round a shape,
# thinning out with distance from its edge, mostly tiny with a few bigger, never clumped
# (blue-noise dart throwing). Returned as one SVG path of circles, so they stay sharp at
# any size. Used by frame.py; numpy, scipy and Pillow.
import math, random, re
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt

def _polys(d):
    """flatten an M/L/Q/Z path into polygons"""
    out, cur, pos, start = [], [], (0, 0), (0, 0)
    toks = re.findall(r'[MLQZ]|-?\d+(?:\.\d+)?', d)
    i, cmd = 0, None
    num = lambda: float(toks[i])
    while i < len(toks):
        if toks[i] in 'MLQZ':
            cmd = toks[i]; i += 1
            if cmd == 'Z':
                if len(cur) > 2: out.append(cur)
                cur, pos = [], start
                continue
        if cmd == 'M':
            if len(cur) > 2: out.append(cur)
            pos = start = (float(toks[i]), float(toks[i + 1])); i += 2; cur = [pos]; cmd = 'L'
        elif cmd == 'L':
            pos = (float(toks[i]), float(toks[i + 1])); i += 2; cur.append(pos)
        elif cmd == 'Q':
            c = (float(toks[i]), float(toks[i + 1])); e = (float(toks[i + 2]), float(toks[i + 3])); i += 4
            for k in range(1, 7):
                t = k / 6
                cur.append(((1 - t) ** 2 * pos[0] + 2 * (1 - t) * t * c[0] + t * t * e[0], (1 - t) ** 2 * pos[1] + 2 * (1 - t) * t * c[1] + t * t * e[1]))
            pos = e
        else:
            i += 1
    if len(cur) > 2: out.append(cur)
    return out

def spray(shapes, box, seed=1, reach=18, density=0.5, rmin=2.2, rmax=7.5, gap=2.5, tilt=(0.0, 0.0), scale=0.5):
    """shapes: path strings; box: (x0, y0, w, h) in drawing units.
    reach: how far the overspray carries (units, the falloff's sigma); density: 0..1 at the edge;
    tilt: (dx, dy) a direction the can was moving, a little more spray on that side."""
    x0, y0, w, h = box
    W, H = int(w * scale), int(h * scale)
    img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
    for d in shapes:
        for p in _polys(d):
            dr.polygon([((x - x0) * scale, (y - y0) * scale) for x, y in p], fill=255)
    inside = np.array(img) > 0
    dist = distance_transform_edt(~inside) / scale                 # units from the nearest painted edge
    gy, gx = np.gradient(dist)                                     # points away from the paint
    rnd = random.Random(seed)
    cell = rmin * 2 + gap; grid = {}
    dots = []
    tries = int(w * h / (cell * cell) * 3)
    for _ in range(tries):
        x, y = rnd.uniform(x0, x0 + w), rnd.uniform(y0, y0 + h)
        px, py = int((x - x0) * scale), int((y - y0) * scale)
        if not (0 <= px < W and 0 <= py < H) or inside[py, px]: continue
        dd = dist[py, px]
        if dd < gap or dd > reach * 3: continue
        lean = 1 + 0.6 * (tilt[0] * gx[py, px] + tilt[1] * gy[py, px]) * scale
        p = density * math.exp(-(dd / reach) ** 2) * max(0.2, lean)
        if rnd.random() > p: continue
        near = math.exp(-(dd / reach) ** 2)                         # bigger droplets close in
        r = rmin + (rmax - rmin) * (rnd.random() ** 3) * (0.4 + 0.6 * near)
        gk = (int(x // cell), int(y // cell))
        clash = False
        for i in range(-2, 3):
            for j in range(-2, 3):
                for (ox, oy, orr) in grid.get((gk[0] + i, gk[1] + j), ()):
                    if (ox - x) ** 2 + (oy - y) ** 2 < (orr + r + gap) ** 2: clash = True; break
                if clash: break
            if clash: break
        if clash: continue
        grid.setdefault(gk, []).append((x, y, r)); dots.append((x, y, r))
    return " ".join(f"M{x - r:.1f},{y:.1f}a{r:.1f},{r:.1f} 0 1,0 {2 * r:.1f},0a{r:.1f},{r:.1f} 0 1,0 {-2 * r:.1f},0" for x, y, r in dots), len(dots)

def dots_only(shapes, box, seed=1, rin0=3.5, rin1=8.0, rout0=1.6, rout1=4.0, gap=1.4, reach=5.0, scale=0.5, tries_per=8):
    """the whole shape as droplets: packed inside, the biggest in the middle, smaller toward the edge,
    and a short feather just past it (reach, in units). Returns (path of circles, count)."""
    rin, rout = (rin0, rin1), (rout0, rout1)
    x0, y0, w, h = box
    W, H = int(w * scale), int(h * scale)
    img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
    for d in shapes:
        for p in _polys(d):
            dr.polygon([((x - x0) * scale, (y - y0) * scale) for x, y in p], fill=255)
    inside = np.array(img) > 0
    out_d = distance_transform_edt(~inside) / scale          # units outside the edge
    in_d = distance_transform_edt(inside) / scale             # units inside it
    rnd = random.Random(seed)
    cell = rin[1] * 2 + gap; grid = {}; dots = []
    ys, xs = np.nonzero(out_d < reach * 2.5)                  # only try where paint could land
    if not len(xs): return '', 0
    n = int(inside.sum() / (scale * scale) / (cell * cell) * tries_per * 4) + 2000
    for _ in range(n):
        k = rnd.randrange(len(xs)); px, py = xs[k], ys[k]
        x = x0 + (px + rnd.random()) / scale; y = y0 + (py + rnd.random()) / scale
        if inside[py, px]:
            t = min(1.0, in_d[py, px] / 14)                    # 0 at the edge, 1 a little way in
            r = rout[1] + (rin[0] - rout[1]) * t + (rin[1] - rin[0]) * t * rnd.random() ** 1.5
            r = min(r, in_d[py, px] + rout[1])                 # a dot may straddle the edge, not leap it
        else:
            dd = out_d[py, px]
            if rnd.random() > math.exp(-(dd / reach) ** 2) * 0.55: continue
            r = rout[0] + (rout[1] - rout[0]) * rnd.random() ** 2
        gk = (int(x // cell), int(y // cell)); clash = False
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for (ox, oy, orr) in grid.get((gk[0] + i, gk[1] + j), ()):
                    if (ox - x) ** 2 + (oy - y) ** 2 < (orr + r + gap) ** 2: clash = True; break
                if clash: break
            if clash: break
        if clash: continue
        grid.setdefault(gk, []).append((x, y, r)); dots.append((x, y, r))
    return " ".join(f"M{x - r:.1f},{y:.1f}a{r:.1f},{r:.1f} 0 1,0 {2 * r:.1f},0a{r:.1f},{r:.1f} 0 1,0 {-2 * r:.1f},0" for x, y, r in dots), len(dots)

def kusama(shapes, box, seed=1, rmin=3.0, rmax=16.0, growth=1.35, gapk=0.35, wobble=0.04, scale=0.5):
    """the shape as rows of dots that follow its outline, as on Yayoi Kusama's pumpkins: the
    smallest round the edge, each row in a little bigger toward the shape's fullest part,
    evenly spaced along the row, a clear gap between dots, nothing outside the shape.
    rmin/rmax: the edge's and the biggest dots' radius (units); growth: row-on-row size step;
    gapk: the gap as a share of the radius; wobble: a hand's unevenness. Returns (path, count)."""
    import contourpy
    x0, y0, w, h = box
    W, H = int(w * scale), int(h * scale)
    img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
    for d in shapes:
        for p in _polys(d):
            dr.polygon([((x - x0) * scale, (y - y0) * scale) for x, y in p], fill=255)
    inside = np.array(img) > 0
    in_d = distance_transform_edt(inside) / scale
    gen = contourpy.contour_generator(z=in_d)
    rnd = random.Random(seed)
    cell = rmax * 2.6; grid = {}; dots = []
    def free(x, y, r):
        gk = (int(x // cell), int(y // cell))
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for (ox, oy, orr) in grid.get((gk[0] + i, gk[1] + j), ()):
                    if (ox - x) ** 2 + (oy - y) ** 2 < (orr + r + gapk * min(r, orr)) ** 2: return False
        return True
    r, d = rmin, rmin * 1.05
    while True:
        lines = gen.lines(d)
        if not lines: break
        step = 2 * r * (1 + gapk)
        for ln in lines:
            pts = [(x0 + px / scale, y0 + py / scale) for px, py in ln]
            if len(pts) < 2: continue
            seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
            total = sum(seg)
            if total < step * 0.6:                        # a tiny ring: one dot at its middle
                cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
                if free(cx, cy, r): grid.setdefault((int(cx // cell), int(cy // cell)), []).append((cx, cy, r)); dots.append((cx, cy, r))
                continue
            n = max(1, round(total / step)); sp = total / n   # evenly round the row, no half-dot at the seam
            at, i, acc = rnd.random() * sp, 0, 0.0
            while at < total - 1e-6:
                while i < len(seg) - 1 and acc + seg[i] < at: acc += seg[i]; i += 1
                t = (at - acc) / seg[i] if seg[i] else 0
                x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t; y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t
                rr = r * (1 + wobble * (rnd.random() * 2 - 1))
                x += r * wobble * (rnd.random() * 2 - 1); y += r * wobble * (rnd.random() * 2 - 1)
                if free(x, y, rr):
                    grid.setdefault((int(x // cell), int(y // cell)), []).append((x, y, rr)); dots.append((x, y, rr))
                at += sp
        nr = min(rmax, r * growth)
        d += r * (1 + gapk) + nr
        r = nr
    return " ".join(f"M{x - r:.1f},{y:.1f}a{r:.1f},{r:.1f} 0 1,0 {2 * r:.1f},0a{r:.1f},{r:.1f} 0 1,0 {-2 * r:.1f},0" for x, y, r in dots), len(dots)

def kusama2(shapes, box, seed=1, rmin=4.0, rmax=24.0, k=0.6, steps=1.45, gapk=0.45, wobble=0.03, scale=0.5):
    """Kusama's pumpkin more than an outline: each dot's size set by how thick the shape is
    where it sits (the biggest down the middle of a leaf, the smallest at its edges and tips),
    sizes in a few set steps so neighbours match, the biggest laid first, a clear even gap,
    and the middle filled. Returns (path of circles, count)."""
    x0, y0, w, h = box
    W, H = int(w * scale), int(h * scale)
    img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
    for d in shapes:
        for p in _polys(d):
            dr.polygon([((x - x0) * scale, (y - y0) * scale) for x, y in p], fill=255)
    inside = np.array(img) > 0
    in_d = distance_transform_edt(inside) / scale
    sizes = [rmin]
    while sizes[-1] * steps <= rmax: sizes.append(sizes[-1] * steps)
    rnd = random.Random(seed)
    sp = max(1, int(rmin * 0.7 * scale))
    cand = []
    for py in range(0, H, sp):
        for px in range(0, W, sp):
            jx = min(W - 1, px + rnd.randrange(sp)); jy = min(H - 1, py + rnd.randrange(sp))
            dd = in_d[jy, jx]
            if dd < rmin * 0.9: continue
            want = min(rmax, max(rmin, k * dd))
            r = max(s for s in sizes if s <= want + 1e-6)
            r = min(r, dd * 0.98)
            cand.append((r, dd, x0 + (jx + 0.5) / scale, y0 + (jy + 0.5) / scale))
    cand.sort(key=lambda c: (-c[0], -c[1]))
    cell = rmax * 2.6; grid = {}; dots = []
    for r, _, x, y in cand:
        gk = (int(x // cell), int(y // cell)); ok = True
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for (ox, oy, orr) in grid.get((gk[0] + i, gk[1] + j), ()):
                    if (ox - x) ** 2 + (oy - y) ** 2 < (orr + r + gapk * min(r, orr)) ** 2: ok = False; break
                if not ok: break
            if not ok: break
        if not ok: continue
        rr = r * (1 + wobble * (rnd.random() * 2 - 1))
        grid.setdefault(gk, []).append((x, y, r)); dots.append((x, y, rr))
    return " ".join(f"M{x - r:.1f},{y:.1f}a{r:.1f},{r:.1f} 0 1,0 {2 * r:.1f},0a{r:.1f},{r:.1f} 0 1,0 {-2 * r:.1f},0" for x, y, r in dots), len(dots)

def kusama3(shapes, box, seed=1, rmin=3.0, k=0.85, gapk=0.2, wobble=0.03, scale=0.5, shared=None):
    """filled, after Kusama's pumpkin: each dot as big as the shape is thick where it sits, with
    no cap (a leaf's middle gets one great dot, its tips small ones), a small even gap; then the
    spaces left are filled, largest first, with the biggest dot that fits, down to rmin.
    Returns (path of circles, count)."""
    x0, y0, w, h = box
    W, H = int(w * scale), int(h * scale)
    img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
    for d in shapes:
        for p in _polys(d):
            dr.polygon([((x - x0) * scale, (y - y0) * scale) for x, y in p], fill=255)
    inside = np.array(img) > 0
    in_d = distance_transform_edt(inside) / scale
    rnd = random.Random(seed)
    sp = max(1, int(rmin * 0.6 * scale))
    pts = []
    for py in range(0, H, sp):
        for px in range(0, W, sp):
            jx = min(W - 1, px + rnd.randrange(sp)); jy = min(H - 1, py + rnd.randrange(sp))
            dd = in_d[jy, jx]
            if dd >= rmin: pts.append((dd, x0 + (jx + 0.5) / scale, y0 + (jy + 0.5) / scale))
    big = max([p[0] for p in pts], default=rmin) * k
    if shared is not None: cell, grid, dots = shared['cell'], shared['grid'], shared['dots']   # one packing across several shapes
    else: cell = max(rmin * 4, big * 2.2); grid = {}; dots = []
    def room(x, y):
        gk = (int(x // cell), int(y // cell)); best = 1e9
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for (ox, oy, orr) in grid.get((gk[0] + i, gk[1] + j), ()):
                    best = min(best, math.dist((ox, oy), (x, y)) - orr - gapk * max(rmin, min(orr, best)))
        return best
    def put(x, y, r):
        grid.setdefault((int(x // cell), int(y // cell)), []).append((x, y, r)); dots.append((x, y, r * (1 + wobble * (rnd.random() * 2 - 1))))
    # the graded dots, biggest first
    for dd, x, y in sorted(pts, key=lambda p: -p[0]):
        r = k * dd
        if room(x, y) >= r * (1 + gapk): put(x, y, r)
    # then the gaps, each filled with the biggest dot that fits (not past the shape's edge)
    for _ in range(2):
        for dd, x, y in sorted(pts, key=lambda p: -p[0]):
            r = min(room(x, y) / (1 + gapk), dd * 0.95, k * dd)
            if r >= rmin: put(x, y, r)
    return " ".join(f"M{x - r:.1f},{y:.1f}a{r:.1f},{r:.1f} 0 1,0 {2 * r:.1f},0a{r:.1f},{r:.1f} 0 1,0 {-2 * r:.1f},0" for x, y, r in dots), len(dots)

def kusama4(shapes, box, seed=1, **kw):
    """kusama3 leaf by leaf: each frond and leaf packed on its own, so a dot is sized by that
    leaf's thickness, not by a blob where several overlap. Returns (path, count)."""
    shared = {'cell': 130.0, 'grid': {}, 'dots': []}   # each leaf sized on its own, none overlapping another
    for i, d in enumerate(shapes):
        ps = _polys(d)
        if not ps: continue
        xs = [x for p in ps for x, _ in p]; ys = [y for p in ps for _, y in p]
        bx = (min(xs) - 10, min(ys) - 10, max(xs) - min(xs) + 20, max(ys) - min(ys) + 20)
        kusama3([d], bx, seed=seed * 101 + i, shared=shared, **kw)
    dots = shared['dots']
    return " ".join(f"M{x - r:.1f},{y:.1f}a{r:.1f},{r:.1f} 0 1,0 {2 * r:.1f},0a{r:.1f},{r:.1f} 0 1,0 {-2 * r:.1f},0" for x, y, r in dots), len(dots)

def kusama6(shapes, box, seed=1, rmin=4.0, k=0.8, gap=5.0, wobble=0.0, scale=0.5, passes=3):
    """kusama4 with one constant gap: every dot stops `gap` units short of its neighbours, the
    gaps are filled with the biggest dot that fits, and then each dot grows until it is exactly
    `gap` from the nearest one (or reaches its leaf's edge), so the paper between dots is even."""
    G = gap; cell = 130.0; grid = {}; dots = []      # dots: [x, y, r, bound]
    rnd = random.Random(seed)
    def near(x, y):
        gk = (int(x // cell), int(y // cell))
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                yield from grid.get((gk[0] + i, gk[1] + j), ())
    def room(x, y, skip=None):
        best = 1e9
        for d in near(x, y):
            if d is skip: continue
            best = min(best, math.dist((d[0], d[1]), (x, y)) - d[2] - G)
        return best
    def put(x, y, r, bound):
        d = [x, y, r, bound]; grid.setdefault((int(x // cell), int(y // cell)), []).append(d); dots.append(d)
    for si, sh in enumerate(shapes):
        ps = _polys(sh)
        if not ps: continue
        xs = [x for p in ps for x, _ in p]; ys = [y for p in ps for _, y in p]
        bx0, by0 = min(xs) - 10, min(ys) - 10
        W, H = int((max(xs) - bx0 + 10) * scale) + 1, int((max(ys) - by0 + 10) * scale) + 1
        img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
        for p in ps: dr.polygon([((x - bx0) * scale, (y - by0) * scale) for x, y in p], fill=255)
        in_d = distance_transform_edt(np.array(img) > 0) / scale
        sp = max(1, int(rmin * 0.5 * scale)); pts = []
        for py in range(0, H, sp):
            for px in range(0, W, sp):
                jx = min(W - 1, px + rnd.randrange(sp)); jy = min(H - 1, py + rnd.randrange(sp))
                dd = in_d[jy, jx]
                if dd >= rmin: pts.append((dd, bx0 + (jx + 0.5) / scale, by0 + (jy + 0.5) / scale))
        pts.sort(key=lambda p: -p[0])
        for dd, x, y in pts:                            # graded: as big as the leaf is thick
            r = k * dd
            if room(x, y) >= r: put(x, y, r, dd * 0.97)
        for _ in range(passes):                         # the gaps: the biggest dot that fits
            for dd, x, y in pts:
                r = min(room(x, y), dd * 0.97)
                if r >= rmin: put(x, y, r, dd * 0.97)
    for _ in range(4):                                  # grow each dot to the even gap
        for d in sorted(dots, key=lambda d: -d[2]):
            d[2] = max(d[2], min(d[3], room(d[0], d[1], skip=d)))   # room() is the radius that leaves exactly G
    out = []
    for x, y, r, _ in dots:
        r *= 1 + wobble * (rnd.random() * 2 - 1)
        out.append(f"M{x - r:.1f},{y:.1f}a{r:.1f},{r:.1f} 0 1,0 {2 * r:.1f},0a{r:.1f},{r:.1f} 0 1,0 {-2 * r:.1f},0")
    return " ".join(out), len(dots)
