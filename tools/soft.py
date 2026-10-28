# Gravity for mythen.io's plants: each frond and leaf is an elastic rod (an elastica)
# clamped at its stalk, stiff at the base and limp at the tip, carrying its own weight; each
# vine is a heavy chain pinned at both ends, sagging under itself and the leaves it carries.
# The shapes are drawn along the rods once they settle. Used by frame.py when SIM is set.
import math
from bold import pt, smooth

def elastica(base, ang, L, flop, curl=0.0, n=40, width=None, stiff=2.0, load=0.0):
    """the settled spine of a cantilever: n+1 points from base, clamped at angle ang.
    flop is weight over stiffness (0 = rigid); curl is the rod's own resting bend (radians
    over its length); width(t) weights it (leaf area); stiffness falls as (1-t)**stiff toward
    the tip; load is an extra weight hung at the tip."""
    width = width or (lambda t: 1.0)
    ds = 1.0 / n
    m = [width((i + 0.5) / n) * ds for i in range(n)]
    tot = sum(m); m = [v / tot for v in m]; m[-1] += load
    EI = [0.08 + (1 - (i + 0.5) / n) ** stiff for i in range(n)]
    rest = [ang + curl * (i + 0.5) / n for i in range(n)]
    th = rest[:]
    for _ in range(400):
        xs = [0.0]
        for a in th: xs.append(xs[-1] + math.cos(a) * ds)
        mid = [(xs[i] + xs[i + 1]) / 2 for i in range(n)]
        # the moment about each joint of the weight beyond it: turns the rod toward straight down
        new, bend = [], 0.0
        for i in range(n):
            M = sum(m[j] * (mid[j] - xs[i]) for j in range(i, n))
            bend += flop * M / EI[i] * ds
            new.append(rest[i] + bend)
        delta = max(abs(a - b) for a, b in zip(new, th))
        th = [a + 0.25 * (b - a) for a, b in zip(th, new)]
        if delta < 1e-5: break
    p = [base]
    for a in th: p.append((p[-1][0] + math.cos(a) * ds * L, p[-1][1] + math.sin(a) * ds * L))
    return p

def chain(p0, p1, length, loads=(), n=60, stiff=0.15, iters=3000):
    """a heavy vine of the given length, pinned at p0 and p1, settled under gravity (position-
    based dynamics: distance links, a little bending stiffness). loads: (t, weight) hung along it"""
    seg = length / n
    P = [(p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n + 40 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    w = [1.0] * (n + 1)
    for t, kg in loads:
        w[min(n - 1, max(1, round(t * n)))] += kg
    inv = [0.0] + [1 / v for v in w[1:-1]] + [0.0]
    prev = P[:]
    for it in range(iters):
        damp = 0.98
        Q = [(x + (x - px) * damp, y + (y - py) * damp + 0.4 * (1 if inv[i] else 0)) for i, ((x, y), (px, py)) in enumerate(zip(P, prev))]
        prev = P
        for _ in range(8):
            for i in range(n):
                a, b = Q[i], Q[i + 1]; dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy) or 1e-9
                s = inv[i] + inv[i + 1]
                if not s: continue
                c = (d - seg) / d / s
                Q[i] = (a[0] + dx * c * inv[i], a[1] + dy * c * inv[i]); Q[i + 1] = (b[0] - dx * c * inv[i + 1], b[1] - dy * c * inv[i + 1])
            for i in range(n - 1):   # bending: keep each pair of links from folding
                a, b = Q[i], Q[i + 2]; dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy) or 1e-9
                s = inv[i] + inv[i + 2]
                if not s or d >= 2 * seg: continue
                c = stiff * (d - 2 * seg) / d / s
                Q[i] = (a[0] + dx * c * inv[i], a[1] + dy * c * inv[i]); Q[i + 2] = (b[0] - dx * c * inv[i + 2], b[1] - dy * c * inv[i + 2])
        P = Q
    return P

def along(p, t):
    """the point and heading at fraction t of a polyline's length"""
    seg = [math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1]) for i in range(len(p) - 1)]
    want = max(0.0, min(1.0, t)) * sum(seg)
    for i, s in enumerate(seg):
        if want <= s or i == len(seg) - 1:
            f = want / s if s else 0
            a = math.atan2(p[i + 1][1] - p[i][1], p[i + 1][0] - p[i][0])
            return (p[i][0] + (p[i + 1][0] - p[i][0]) * f, p[i][1] + (p[i + 1][1] - p[i][1]) * f), a
        want -= s
    return p[-1], 0.0

def bend(spine, L, local):
    """map points drawn straight along +u (u in 0..L, v across) onto the curved spine"""
    out = []
    for u, v in local:
        c, a = along(spine, u / L)
        if u > L: c = (c[0] + math.cos(a) * (u - L), c[1] + math.sin(a) * (u - L))
        out.append(pt(c, a, 0, v))
    return out

def frond(base, ang, L, W, teeth=8, curl=0.0, flop=1.0):
    """bold.frond's lobed blade, drawn along its own settled spine"""
    w = lambda t: math.sin(math.pi * min(1, t * 1.15)) ** 0.8 + 0.15
    spine = elastica(base, ang, L, flop, curl=curl * 0.4, width=w)
    left, right = [], []
    for i in range(teeth * 2 + 1):
        t = i / (teeth * 2)
        c, a = along(spine, t)
        wd = W * math.sin(math.pi * min(1, t * 1.15)) ** 0.8 * (1.0 if i % 2 else 0.55)
        left.append(pt(c, a, 0, wd)); right.append(pt(c, a, 0, -wd))
    tip, a = along(spine, 1.0)
    tip = (tip[0] + math.cos(a) * L * 0.02, tip[1] + math.sin(a) * L * 0.02)
    return smooth([base] + left + [tip] + right[::-1])

LEAF = ((0, 0), (0.25, 0.42), (0.6, 0.5), (1.0, 0.36), (1.45, 0.12), (1.7, 0), (1.45, -0.12), (1.0, -0.36), (0.6, -0.5), (0.25, -0.42))
def leaf(c, ang, s, flop=1.2, vine=None):
    """frame.py's broad pointed leaf, its blade drooping from the stalk under its own weight.
    vine=(points, width): the stem it grows from; if the settled blade would lie on or through
    the stem (it can't: they're solid), returns None so the caller can hang it another way"""
    L = 1.7 * s
    w = lambda t: 0.25 + math.sin(math.pi * min(1, t * 1.6)) * (1 - t)
    spine = elastica(c, ang, L, flop, width=w, stiff=1.5)
    if vine and touches(spine, s, *vine): return None
    return smooth(bend(spine, L, [(s * u, s * v) for u, v in LEAF]))

def touches(spine, s, stem, width):
    """does the blade (past its stalk) come within its own half-width of the stem?"""
    for i, (x, y) in enumerate(spine):
        t = i / (len(spine) - 1)
        if t < 0.15: continue
        half = s * 0.5 * min(1, math.sin(math.pi * min(1, t * 1.15)) + 0.2)
        if min(math.hypot(x - a, y - b) for a, b in stem) < width / 2 + half * 0.8: return True
    return False

def ribbon(p, width):
    """a polyline as a thick band"""
    l, r = [], []
    for i in range(len(p)):
        a, b = p[max(0, i - 1)], p[min(len(p) - 1, i + 1)]
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        l.append(pt(p[i], ang, 0, width / 2)); r.append(pt(p[i], ang, 0, -width / 2))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in l + r[::-1]) + "Z"
