# A flat, layered jungle for mythen.io: per side and per depth, one tile that repeats
# seamlessly down the page (trunks and vines enter at the top and leave at the bottom
# at the same x). Solid colour per layer, spray-painted edges. python jungle.py <outdir>
import math, random, sys
OUT = sys.argv[1]
H = 1600

def leaf(x, y, ang, L, W, cut=None):
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda u, v: (x + u * ca - v * sa, y + u * sa + v * ca)
    b, t = P(0, 0), P(L, 0)
    c1, c2 = P(L * 0.42, W), P(L * 0.58, -W)
    d = f"M{b[0]:.1f},{b[1]:.1f} Q{c1[0]:.1f},{c1[1]:.1f} {t[0]:.1f},{t[1]:.1f} Q{c2[0]:.1f},{c2[1]:.1f} {b[0]:.1f},{b[1]:.1f}Z"
    rib = None
    if cut:   # the midrib, cut through in the sky's colour: a flat leaf reads as a leaf
        m0, m1 = P(L * 0.08, 0), P(L * 0.86, 0)
        rib = f"M{m0[0]:.1f},{m0[1]:.1f} L{m1[0]:.1f},{m1[1]:.1f}"
    return d, rib

def banana(x, y, ang, L, W):
    # a long blade with a few torn slits: the big "card" leaves of a stylised jungle
    d, _ = leaf(x, y, ang, L, W)
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda u, v: (x + u * ca - v * sa, y + u * sa + v * ca)
    slits = []
    for k in range(3):
        u = L * (0.35 + 0.18 * k)
        for side in (1, -1):
            a, b = P(u, side * W * 0.15), P(u + L * 0.06, side * W * 0.9)
            slits.append(f"M{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f}")
    return d, " ".join(slits)

def vertical(x0, amp, phase, wobble=2):
    # a stem from top to bottom, the same x at both ends, so the tile repeats seamlessly
    pts = []
    for i in range(0, 41):
        y = -40 + (H + 80) * i / 40
        x = x0 + amp * math.sin(2 * math.pi * wobble * (y + 40) / (H + 80) + phase)
        pts.append((x, y))
    return pts

def path_of(pts):
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for a, b in zip(pts[1:-1:2], pts[2::2]):
        d += f" Q{a[0]:.1f},{a[1]:.1f} {b[0]:.1f},{b[1]:.1f}"
    return d

def spray_defs(fill, rough=4):
    return ('<defs><filter id="spray" x="-10%" y="-2%" width="120%" height="104%">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves="2" seed="4" result="grain"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="grain" scale="{rough}" xChannelSelector="R" yChannelSelector="G" result="rough"/>'
            '<feGaussianBlur in="SourceAlpha" stdDeviation="5" result="halo"/>'
            '<feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="1" seed="9" result="dots"/>'
            '<feColorMatrix in="dots" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 10 -5.6" result="dotmask"/>'
            '<feComposite in="halo" in2="dotmask" operator="in" result="speckle"/>'
            f'<feFlood flood-color="{fill}"/><feComposite in2="speckle" operator="in" result="paint"/>'
            '<feMerge><feMergeNode in="paint"/><feMergeNode in="rough"/></feMerge></filter></defs>')

def tile(name, w, fill, sky, seed, trunks=(), vines=(), blades=0, blade_len=(120, 200), leaf_len=(40, 70), flip=False):
    random.seed(seed)
    shapes, strokes, cuts = [], [], []
    for (x0, width, amp) in trunks:
        pts = vertical(x0, amp, random.uniform(0, 6))
        strokes.append((path_of(pts), width))
        # branches with big blades, kept clear of the tile's seam
        for _ in range(4):
            y = random.uniform(160, H - 160)
            i = min(range(len(pts)), key=lambda k: abs(pts[k][1] - y)); bx, by = pts[i]
            side = random.choice((1, -1)) if not flip else 1
            a = (-math.pi / 2 + side * random.uniform(0.6, 1.2))
            L = random.uniform(*blade_len)
            d, sl = banana(bx, by, a, L, L * 0.22); shapes.append(d); cuts.append(sl)
    for (x0, width, amp, wob) in vines:
        pts = vertical(x0, amp, random.uniform(0, 6), wob)
        strokes.append((path_of(pts), width))
        side, y = 1, 80
        while y < H - 80:
            i = min(range(len(pts)), key=lambda k: abs(pts[k][1] - y)); px, py = pts[i]
            j = min(i + 1, len(pts) - 1); ang = math.atan2(pts[j][1] - py, pts[j][0] - px + 1e-6)
            L = random.uniform(*leaf_len)
            d, rib = leaf(px, py, ang + side * random.uniform(0.7, 1.15), L, L * 0.33, cut=True)
            shapes.append(d); cuts.append(rib); side = -side
            y += random.uniform(L * 0.7, L * 1.05)
    for _ in range(blades):   # loose big leaves, as if from plants just out of frame
        x = random.uniform(0, w) if not flip else random.uniform(0, w)
        y = random.uniform(200, H - 200)
        a = random.uniform(-math.pi * 0.95, -math.pi * 0.05)
        L = random.uniform(*blade_len)
        d, sl = banana(x, y, a, L, L * 0.24); shapes.append(d); cuts.append(sl)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {H}" width="{w}" height="{H}" aria-hidden="true">', spray_defs(fill), '<g filter="url(#spray)">']
    for d, sw in strokes:
        o.append(f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{sw}" stroke-linecap="round"/>')
    o.append(f'<path d="{" ".join(shapes)}" fill="{fill}"/>')
    o.append('</g>')
    o.append(f'<path d="{" ".join(c for c in cuts if c)}" fill="none" stroke="{sky}" stroke-width="2.2" stroke-linecap="round" opacity=".55"/>')
    o.append('</svg>')
    open(f"{OUT}/{name}.svg", "w").write("\n".join(o))

SKY = "#e7f1d2"
# far: pale trunks and long vines
tile("j-far-l", 520, "#cfe2ad", SKY, 1, trunks=[(90, 34, 18), (330, 22, 26)], vines=[(210, 5, 30, 2), (440, 4, 22, 3)], blades=4)
tile("j-far-r", 520, "#cfe2ad", SKY, 2, trunks=[(420, 34, 18), (180, 22, 26)], vines=[(300, 5, 30, 2), (70, 4, 22, 3)], blades=4)
# mid: a fuller green, bigger leaves
tile("j-mid-l", 440, "#adcb83", SKY, 3, trunks=[(60, 48, 14)], vines=[(190, 7, 34, 2), (330, 6, 28, 3)], blades=6, blade_len=(150, 240), leaf_len=(54, 86))
tile("j-mid-r", 440, "#adcb83", SKY, 4, trunks=[(380, 48, 14)], vines=[(250, 7, 34, 2), (110, 6, 28, 3)], blades=6, blade_len=(150, 240), leaf_len=(54, 86))
# near: dark, close, few but large
tile("j-near-l", 300, "#7da658", SKY, 5, vines=[(70, 9, 26, 2), (210, 7, 22, 3)], blades=4, blade_len=(170, 260), leaf_len=(64, 100))
tile("j-near-r", 300, "#7da658", SKY, 6, vines=[(230, 9, 26, 2), (90, 7, 22, 3)], blades=4, blade_len=(170, 260), leaf_len=(64, 100))
# thick: the jungle closing in as you scroll (faded in by scroll position)
tile("j-thick-l", 380, "#94b86b", SKY, 7, vines=[(40, 8, 20, 3), (150, 8, 30, 2), (270, 6, 26, 3)], blades=9, blade_len=(140, 230), leaf_len=(50, 84))
tile("j-thick-r", 380, "#94b86b", SKY, 8, vines=[(340, 8, 20, 3), (230, 8, 30, 2), (110, 6, 26, 3)], blades=9, blade_len=(140, 230), leaf_len=(50, 84))
print("ok")
