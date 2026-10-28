# mythen.io's jungle, bold: few, big, thick, simple shapes (Matisse's cut-outs, Primal's
# silhouettes), a solid colour per depth, sprayed edges on the near plants.
# Writes the same files the page uses: far-l/r, canopy, border, front-l/r. python tools/bold.py
import math, random, os
OUT = os.path.join(os.path.dirname(__file__), '..')
FAR, MID, NEAR = '#a3ae8c', '#6d8a3a', '#34492a'
OCHRE = ['#c98f4a', '#b0622f', '#8f4630']

def pt(o, ang, u, v):
    return (o[0] + u * math.cos(ang) - v * math.sin(ang), o[1] + u * math.sin(ang) + v * math.cos(ang))

def poly(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"

def smooth(pts):
    # a closed path through the points with soft corners (midpoint quadratics)
    n = len(pts); mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    d = f"M{mids[-1][0]:.1f},{mids[-1][1]:.1f}"
    for i in range(n):
        d += f" Q{pts[i][0]:.1f},{pts[i][1]:.1f} {mids[i][0]:.1f},{mids[i][1]:.1f}"
    return d + "Z"

def frond(base, ang, L, W, teeth=6, curl=0.0):
    """one chunky frond: a tapering blade whose edges are a few big rounded lobes"""
    left, right = [], []
    for i in range(teeth * 2 + 1):
        t = i / (teeth * 2)
        a = ang + curl * t
        spine = pt(base, ang, L * t, 0) if curl == 0 else pt(base, a, L * t, L * curl * t * t * 0.3)
        w = W * math.sin(math.pi * min(1, t * 1.15)) ** 0.8 * (1.0 if i % 2 else 0.55)   # lobe, notch, lobe…
        left.append(pt(spine, a, 0, w)); right.append(pt(spine, a, 0, -w))
    tip = pt(base, ang + curl, L * 1.02, 0)
    return smooth([base] + left + [tip] + right[::-1])

def heart(c, ang, s):
    """a big lobed leaf, Matisse-like: a heart with two deep notches"""
    pts = []
    for k in range(13):
        a = math.pi * 2 * k / 12
        r = s * (0.62 + 0.38 * math.cos(a)) * (0.7 if k in (4, 8) else 1.0)
        pts.append(pt(c, ang, r * math.cos(a) * 1.1 + s * 0.35, r * math.sin(a)))
    return smooth(pts)

def blade(base, ang, L, W):
    a, b = pt(base, ang, L * 0.45, W), pt(base, ang, L * 0.55, -W)
    t = pt(base, ang, L, 0)
    return f"M{base[0]:.1f},{base[1]:.1f}Q{a[0]:.1f},{a[1]:.1f} {t[0]:.1f},{t[1]:.1f}Q{b[0]:.1f},{b[1]:.1f} {base[0]:.1f},{base[1]:.1f}Z"

def trunk(x, y0, y1, w0, w1, sway=0):
    return poly([(x - w0 / 2, y0), (x - w1 / 2 + sway, y1), (x + w1 / 2 + sway, y1), (x + w0 / 2, y0)])

def spray(fid, colour, halo, rough):
    sp = (f'<feGaussianBlur in="SourceAlpha" stdDeviation="{halo}" result="h"/>'
          '<feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="1" seed="9" result="d"/>'
          '<feColorMatrix in="d" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 10 -5.4" result="m"/>'
          f'<feComposite in="h" in2="m" operator="in" result="s"/><feFlood flood-color="{colour}"/><feComposite in2="s" operator="in" result="p"/>') if halo else ''
    return (f'<filter id="{fid}" x="-8%" y="-8%" width="116%" height="116%">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.5" numOctaves="2" seed="4" result="g"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="g" scale="{rough}" xChannelSelector="R" yChannelSelector="G" result="r"/>'
            + sp + '<feMerge>' + ('<feMergeNode in="p"/>' if halo else '') + '<feMergeNode in="r"/></feMerge></filter>')

def write(name, w, h, colour, shapes, fid, halo, rough, aspect="xMidYMid meet", extra=""):
    body = f'<g filter="url(#{fid})"><path d="{" ".join(shapes)}" fill="{colour}"/></g>'
    open(f"{OUT}/{name}.svg", "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" preserveAspectRatio="{aspect}" aria-hidden="true">'
        f'<defs>{spray(fid, colour, halo, rough)}</defs>{extra}{body}</svg>')

# ---------------------------------------------------------------- far: two tree ferns a side, repeating down the page
def far(name, xs, seed):
    random.seed(seed); H = 1600; S = []
    for x in xs:
        S.append(trunk(x, H + 20, -20, 34, 30))                       # one thick trunk, top to bottom
        for cy in (random.uniform(260, 420), random.uniform(1060, 1240)):
            for k in range(6):                                        # a crown of six big fronds
                a = -math.pi / 2 + (k - 2.5) * 0.52
                S.append(frond((x, cy), a, random.uniform(170, 220), 30, teeth=5, curl=0.5 * (1 if a > -math.pi / 2 else -1)))
    write(name, 460, H, FAR, S, 'f', 0, 3)
far('far-l', (110, 340), 3)
far('far-r', (120, 350), 5)

# ---------------------------------------------------------------- the canopy: a few thick lianas with big leaves
random.seed(11); W, H = 1600, 560; S = []
for x, L in ((60, 470), (190, 330), (330, 420), (1270, 400), (1410, 300), (1540, 480), (760, 170), (980, 220)):
    sway = random.uniform(-30, 30)
    # the vine as a thick ribbon
    pts = [(x + sway * math.sin(t * 2.4), t * L) for t in (i / 12 for i in range(13))]
    S.append(poly([(p[0] - 5, p[1]) for p in pts] + [(p[0] + 5, p[1]) for p in pts[::-1]]))
    for j, t in enumerate((0.3, 0.55, 0.8, 0.98)):
        if t * L < 60: continue
        p = (x + sway * math.sin(t * 2.4), t * L); s = random.uniform(30, 42)
        S.append(heart(p, math.pi / 2 + (0.7 if j % 2 else -0.7), s))
# a great frond crown at each top corner, arching down over the edge
for cx, side in ((20, 1), (W - 20, -1)):
    for k in range(5):
        a = math.pi / 2 - side * (0.25 + k * 0.3)
        S.append(frond((cx, -30), a, random.uniform(300, 380), 46, teeth=6, curl=-side * 0.35))
write('canopy', W, H, MID, S, 'm', 3, 4, 'xMidYMin slice')

# ---------------------------------------------------------------- the border: big plants on ochre earth
def plants(W, base, seed, xs, scale=1.0):
    random.seed(seed); S = []
    for i, x in enumerate(xs):
        kind = i % 4
        if kind == 0:     # a fern clump: five big fronds fanning up
            for k in range(5):
                a = -math.pi / 2 + (k - 2) * 0.42
                S.append(frond((x, base), a, random.uniform(170, 230) * scale, 30 * scale, teeth=5, curl=0.3 * (k - 2) / 2))
        elif kind == 1:   # big lobed leaves on short stalks
            for k in range(3):
                a = -math.pi / 2 + (k - 1) * 0.6
                stalk = pt((x, base), a, 70 * scale, 0)
                S.append(trunk(x, base, stalk[1], 10 * scale, 8 * scale, stalk[0] - x))
                S.append(heart(stalk, a, random.uniform(48, 64) * scale))
        elif kind == 2:   # horsetails: stacked fat segments with a few thick spikes
            for k in range(3):
                hx = x + (k - 1) * 34 * scale; h = random.uniform(170, 250) * scale; seg = 6
                for j in range(seg):
                    y0 = base - h * j / seg; y1 = base - h * (j + 1) / seg + 4
                    S.append(poly([(hx - 8 * scale, y0), (hx - 7 * scale, y1), (hx + 7 * scale, y1), (hx + 8 * scale, y0)]))
                    if 0 < j < seg - 1:
                        for s in (1, -1):
                            S.append(blade((hx, y1 + 2), -math.pi / 2 + s * 0.9, 34 * scale * (1 - j / seg), 5 * scale))
        else:             # a cycad: a stout trunk and a fan of wide blades
            th = 60 * scale
            S.append(trunk(x, base + 4, base - th, 30 * scale, 18 * scale))
            for k in range(7):
                a = -math.pi / 2 + (k - 3) * 0.38
                S.append(blade((x, base - th), a, random.uniform(130, 170) * scale, 18 * scale))
    return S

def earth(W, H, base):
    out = []
    for i, c in enumerate(OCHRE):
        top = base + i * 28
        pts = [(x, top + 8 * math.sin(x / 110 + i * 2)) for x in range(0, W + 81, 80)]
        out.append(f'<path d="M0,{H} L' + " L".join(f"{x:.0f},{y:.1f}" for x, y in pts) + f' L{W},{H}Z" fill="{c}"/>')
    return "".join(out)

W, H, BASE = 1600, 440, 330
write('border', W, H, NEAR, plants(W, BASE + 10, 21, list(range(40, W, 115))), 'n', 6, 5, 'xMidYMax slice', extra=earth(W, H, BASE))
for name, seed in (('front-l', 31), ('front-r', 37)):
    write(name, 360, 440, NEAR, plants(360, 420, seed, [130, 250], 1.0), 'n', 6, 5)
print('ok')
