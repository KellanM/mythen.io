# mythen.io's Paleolithic jungle (Sendak's Wild Things forest, cave pigments, coal-age
# plants), drawn as flat shapes: no outlines, no veins, solid colour per depth, sprayed
# edges on the near plants. python tools/paleo.py  (writes into the site's root)
#   far-l.svg / far-r.svg   a colonnade of thin trunks and tree-fern crowns; repeats down the page
#   canopy.svg             lianas hanging from the top edge, thickest at the corners
#   border.svg             the fern border: sword ferns, horsetails, cycads on stepped ochre earth
#   front-l.svg / front-r.svg   the clumps standing in front of the sheet's lower corners
#   hand.svg               a red-ochre negative hand stencil (the signature)
#   dab.svg                an ochre finger-dab (the bullets)
import math, random, os
OUT = os.path.join(os.path.dirname(__file__), '..')
SKY, FAR, MID, NEAR = '#ebeedb', '#9aa68a', '#6f8f3a', '#3d4f2a'
OCHRE = ['#c98f4a', '#b0622f', '#8f4630']   # yellow, burnt, red ochre: the earth's bands, top to bottom

def P(x, y, ang, u, v):
    return (x + u * math.cos(ang) - v * math.sin(ang), y + u * math.sin(ang) + v * math.cos(ang))

def blade(x, y, ang, L, W):
    b, t = P(x, y, ang, 0, 0), P(x, y, ang, L, 0)
    c1, c2 = P(x, y, ang, L * .45, W), P(x, y, ang, L * .55, -W)
    return f"M{b[0]:.1f},{b[1]:.1f}Q{c1[0]:.1f},{c1[1]:.1f} {t[0]:.1f},{t[1]:.1f}Q{c2[0]:.1f},{c2[1]:.1f} {b[0]:.1f},{b[1]:.1f}Z"

def quad_pts(p0, p1, p2, n=24):
    return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0], (1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in (i/n for i in range(n+1))]

def frond(base, tip, bend, leaflet, density=16, stiff=False):
    """a pinnate frond: a curved rachis from base to tip, leaflet pairs shrinking to the tip"""
    mid = ((base[0]+tip[0])/2 + bend[0], (base[1]+tip[1])/2 + bend[1])
    pts = quad_pts(base, mid, tip, density)
    stem = f"M{base[0]:.1f},{base[1]:.1f}Q{mid[0]:.1f},{mid[1]:.1f} {tip[0]:.1f},{tip[1]:.1f}"
    leaves = []
    for i in range(2, len(pts)-1):
        (x, y), (x2, y2) = pts[i], pts[i+1]
        a = math.atan2(y2-y, x2-x); k = 1 - i/len(pts)
        L = leaflet * (0.35 + 0.75 * k)
        spread = 1.0 if stiff else 1.15
        for s in (1, -1):
            leaves.append(blade(x, y, a + s * spread, L, L * (0.12 if stiff else 0.22)))
    return stem, leaves

def svg(w, h, body, defs='', extra=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" preserveAspectRatio="{extra or "xMidYMid meet"}" aria-hidden="true"><defs>{defs}</defs>{body}</svg>'

def spray(fid, colour, halo, rough):
    # sprayed pigment: a roughened edge and, for the near plants, a speckled halo of overspray
    sp = (f'<feGaussianBlur in="SourceAlpha" stdDeviation="{halo}" result="h"/>'
          '<feTurbulence type="fractalNoise" baseFrequency="1.5" numOctaves="1" seed="9" result="d"/>'
          '<feColorMatrix in="d" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 10 -5.4" result="m"/>'
          f'<feComposite in="h" in2="m" operator="in" result="s"/><feFlood flood-color="{colour}"/><feComposite in2="s" operator="in" result="p"/>') if halo else ''
    return (f'<filter id="{fid}" x="-10%" y="-10%" width="120%" height="120%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="4" result="g"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="g" scale="{rough}" xChannelSelector="R" yChannelSelector="G" result="r"/>'
            + sp + f'<feMerge>{"<feMergeNode in=\"p\"/>" if halo else ""}<feMergeNode in="r"/></feMerge></filter>')

def group(fid, colour, stems, fills, sw=3):
    s = ''.join(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{w}" stroke-linecap="round"/>' for d, w in stems)
    return f'<g filter="url(#{fid})">{s}<path d="{" ".join(fills)}" fill="{colour}"/></g>'

# ---------------------------------------------------------------- far: Sendak's colonnade
def colonnade(name, xs, seed):
    random.seed(seed); W, H = 460, 1600; stems, fills = [], []
    for x in xs:
        w = random.uniform(9, 16)
        # a thin trunk, top to bottom (seamless: the same x at both ends), slightly leaning mid-way
        lean = random.uniform(-14, 14)
        stems.append((f"M{x:.1f},-20 C{x+lean:.1f},{H*.33:.0f} {x-lean:.1f},{H*.66:.0f} {x:.1f},{H+20}", w))
        # tree-fern crowns at two heights, clear of the seam
        for cy in (random.uniform(220, 520), random.uniform(950, 1280)):
            n = random.randint(7, 9); R = random.uniform(120, 170)
            for k in range(n):
                a = -math.pi/2 + (k - (n-1)/2) * (math.pi*1.25/(n-1)) + random.uniform(-.08, .08)
                tip = (x + R*math.cos(a), cy + R*math.sin(a) + R*0.55*abs(math.sin(a/1.3)))
                st, lv = frond((x, cy), tip, (R*0.12*math.cos(a+1.4), -R*0.22), R*0.2, 12)
                stems.append((st, 3)); fills += lv
    body = group('f', FAR, stems, fills)
    open(f"{OUT}/{name}.svg", 'w').write(svg(W, H, body, spray('f', FAR, 0, 2)))
colonnade('far-l', (70, 250, 400), 3)
colonnade('far-r', (60, 210, 390), 5)

# ---------------------------------------------------------------- the canopy: lianas from the top edge
random.seed(11); W, H = 1600, 560; stems, fills = [], []
for k in range(26):
    x = random.uniform(0, W)
    edge = min(x, W - x) / (W / 2)             # 0 at the sides, 1 in the middle
    if random.random() < edge * 0.7: continue  # thinner over the middle
    L = random.uniform(160, 520) * (1.15 - 0.65 * edge)
    sway = random.uniform(-40, 40)
    stems.append((f"M{x:.1f},-10 C{x+sway:.1f},{L*.35:.0f} {x-sway:.1f},{L*.7:.0f} {x+sway*.4:.1f},{L:.0f}", random.uniform(3, 6)))
    y = 40
    while y < L - 20:
        s = random.choice((1, -1)); t = y / L
        px = x + sway * (3*t*(1-t)**2 - 3*t*t*(1-t)) + sway*.4*t**3
        fills.append(blade(px, y, math.pi/2 + s*random.uniform(0.6, 1.1), random.uniform(26, 44), random.uniform(10, 15)))
        y += random.uniform(30, 52)
# two great tree-fern crowns in the top corners, fronds arching down over the edge
for cx, side in ((40, 1), (W - 40, -1)):
    for k in range(9):
        a = math.pi/2 - side * (0.15 + k * 0.17)
        R = random.uniform(260, 360); tip = (cx + R*math.cos(a), 30 + R*math.sin(a))
        st, lv = frond((cx, -20), tip, (side*R*0.25, -R*0.1), R*0.17, 15)
        stems.append((st, 4)); fills += lv
open(f"{OUT}/canopy.svg", 'w').write(svg(W, H, group('m', MID, stems, fills), spray('m', MID, 3, 3.5), 'xMidYMin slice'))

# ---------------------------------------------------------------- the fern border on stepped ochre earth
def earth(W, H, base):
    bands = []
    for i, c in enumerate(OCHRE):
        top = base + i * 26
        pts = [(x, top + 7 * math.sin(x / 90 + i * 2) + 4 * math.sin(x / 23 + i)) for x in range(0, W + 41, 40)]
        d = f"M0,{H} L" + " L".join(f"{x:.0f},{y:.1f}" for x, y in pts) + f" L{W},{H}Z"
        bands.append(f'<path d="{d}" fill="{c}"/>')
    return ''.join(bands)

def plants(W, base, seed, colour, scale=1.0, xs=None):
    random.seed(seed); stems, fills = [], []
    xs = xs or [x for x in range(-20, W + 40, 70)]
    for x in xs:
        x += random.uniform(-20, 20); kind = random.random()
        if kind < 0.5:      # a sword-fern clump: fronds fanning up and out
            n = random.randint(5, 8); h = random.uniform(150, 260) * scale
            for k in range(n):
                a = -math.pi/2 + (k - (n-1)/2) * 0.32 + random.uniform(-.1, .1)
                tip = (x + h*math.cos(a)*1.1, base - 10 + h*math.sin(a))
                st, lv = frond((x, base), tip, (math.cos(a)*h*0.18, h*0.12), h*0.11, 16)
                stems.append((st, 3)); fills += lv
        elif kind < 0.78:   # horsetails: jointed stems with whorls of needles
            for k in range(random.randint(2, 4)):
                hx = x + random.uniform(-25, 25); h = random.uniform(160, 300) * scale
                stems.append((f"M{hx:.1f},{base} L{hx + random.uniform(-8, 8):.1f},{base - h:.1f}", 4))
                for j in range(1, 8):
                    yy = base - h * j / 8
                    for s in (1, -1):
                        for m in range(2):
                            fills.append(blade(hx, yy, -math.pi/2 + s*(0.5 + m*0.45), 26*scale*(1 - j/10), 2.6))
        else:               # a cycad: a short stout trunk, a crown of stiff fronds
            th = random.uniform(40, 80) * scale
            # a stout, tapering trunk, as a shape (a stroke this wide reads as a pill)
            w0, w1 = 13 * scale, 7 * scale
            fills.append(f"M{x-w0:.1f},{base+4} L{x-w1:.1f},{base-th:.1f} L{x+w1:.1f},{base-th:.1f} L{x+w0:.1f},{base+4}Z")
            for k in range(9):
                a = -math.pi/2 + (k - 4) * 0.36
                R = random.uniform(110, 160) * scale; tip = (x + R*math.cos(a), base - th + R*math.sin(a) + R*0.25*abs(math.cos(a)))
                st, lv = frond((x, base - th), tip, (0, -R*0.1), R*0.14, 12, stiff=True)
                stems.append((st, 3)); fills += lv
    return stems, fills

W, H, BASE = 1600, 440, 330
st, fl = plants(W, BASE + 8, 21, NEAR)
border = earth(W, H, BASE) + group('n', NEAR, st, fl)
open(f"{OUT}/border.svg", 'w').write(svg(W, H, border, spray('n', NEAR, 6, 4), 'xMidYMax slice'))
# the clumps that stand in front of the sheet's lower corners (placed on its corners by the page)
for name, seed in (('front-l', 31), ('front-r', 37)):
    st, fl = plants(360, 410, seed, NEAR, 0.95, xs=[120, 230])
    open(f"{OUT}/{name}.svg", 'w').write(svg(360, 440, group('n', NEAR, st, fl), spray('n', NEAR, 6, 4)))

# ---------------------------------------------------------------- the signature: a negative hand stencil
hand = ("M60,150 C52,128 50,108 48,90 C46,72 40,52 38,36 C37,28 46,26 49,34 C52,48 56,66 60,82 "
        "C60,60 58,36 58,18 C58,9 68,9 69,18 C70,38 70,62 72,80 C73,58 76,32 78,16 C79,7 89,8 88,18 "
        "C87,40 84,62 84,84 C88,66 94,46 98,34 C101,26 110,28 108,37 C104,54 98,78 96,100 "
        "C104,90 114,80 122,74 C129,69 136,76 130,83 C118,96 108,112 102,128 C96,146 84,156 72,156 Z")
defs = ('<mask id="hm"><rect width="160" height="180" fill="#fff"/><path d="' + hand + '" fill="#000"/></mask>'
        '<filter id="pig" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="1.3" numOctaves="2" seed="7" result="n"/>'
        '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 6 -2.6" result="m"/>'
        '<feComposite in="SourceGraphic" in2="m" operator="in"/></filter>'
        '<radialGradient id="cloud"><stop offset=".45" stop-color="#9b3f26" stop-opacity=".95"/><stop offset="1" stop-color="#9b3f26" stop-opacity="0"/></radialGradient>')
body = '<g mask="url(#hm)" filter="url(#pig)"><ellipse cx="86" cy="92" rx="86" ry="94" fill="url(#cloud)"/></g>'
open(f"{OUT}/hand.svg", 'w').write(svg(170, 190, body, defs))

# ---------------------------------------------------------------- the bullets: an ochre finger-dab
dab = ('<path d="M7.4 1.6C10.6 1.4 13 4 12.7 7.3c-.3 3.2-3.1 5.3-6.2 4.9C3.4 11.8 1.3 9.3 1.7 6.4 2.1 3.6 4.6 1.8 7.4 1.6z" fill="#a4502f" filter="url(#r)"/>')
open(f"{OUT}/dab.svg", 'w').write(svg(14, 14, dab, '<filter id="r"><feTurbulence type="fractalNoise" baseFrequency="1.2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="1.4"/></filter>'))
print('ok')
