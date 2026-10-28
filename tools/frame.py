# mythen.io's jungle as a frame: a few huge, simple shapes growing in from the screen's
# corners (a proscenium round the sheet), two depths, flat colour, sprayed edges.
# Uses the shape kit in bold.py. Writes corner-top-*.svg and corner-bottom-*.svg (the
# right-hand corners are these, mirrored by the page). python tools/frame.py
import math, random, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from bold import blade, trunk, spray, pt, smooth, OCHRE
from bold import frond as _frond

def frond(base, ang, L, W, teeth=8, curl=0.0):
    return _frond(base, ang, L, W, teeth=teeth, curl=curl)

def leaf(c, ang, s):
    # a broad leaf with a pointed tip, Matisse-like: wide near the stalk, drawn to a point
    pts = [pt(c, ang, s * u, s * v) for u, v in ((0, 0), (0.25, 0.42), (0.6, 0.5), (1.0, 0.36), (1.45, 0.12), (1.7, 0), (1.45, -0.12), (1.0, -0.36), (0.6, -0.5), (0.25, -0.42))]
    return smooth(pts)
heart = leaf
OUT = os.path.join(os.path.dirname(__file__), '..')
BACK, FRONT = '#7f9a4a', '#2f4426'
S = 800   # each corner is drawn in an 800 x 800 box, anchored at its corner

def save(name, colour, shapes, fid, halo, rough, under=''):
    body = f'<g filter="url(#{fid})"><path d="{" ".join(shapes)}" fill="{colour}"/></g>'
    open(f"{OUT}/{name}.svg", "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}" aria-hidden="true">'
        f'<defs>{spray(fid, colour, halo, rough)}</defs>{under}{body}</svg>')

# top-left: fronds pour in from the corner and arch down; a long liana with big leaves
def top(seed, n, L, Wd, liana):
    random.seed(seed); sh = []
    for k in range(n):
        a = 0.15 + k * (1.25 / max(1, n - 1))           # from along the top edge to down the side
        sh.append(frond((-40, -40), a, L * random.uniform(0.85, 1.05), Wd, curl=0.45))
    for x, ln in liana:
        sh.append(trunk(x, -10, ln, 16, 12, 18))
        for j, t in enumerate((0.45, 0.75, 1.0)):
            sh.append(heart((x + 18 * t, ln * t), math.pi / 2 + (0.9 if j % 2 else -0.9), 92))
    return sh

# bottom-left: fronds and big leaves rising from an ochre mound
def bottom(seed, n, L, Wd, leaves):
    random.seed(seed); sh = []
    for k in range(n):
        a = -0.12 - k * (1.3 / max(1, n - 1))           # from along the bottom edge to up the side
        sh.append(frond((-30, S + 30), a, L * random.uniform(0.85, 1.05), Wd, curl=-0.4))
    for x, s, a in leaves:
        stalk_top = pt((x, S), a, s * 1.3, 0)
        sh.append(trunk(x, S + 10, stalk_top[1], 18, 12, stalk_top[0] - x))
        sh.append(heart(stalk_top, a, s))
    return sh

mound = ''.join(f'<path d="M-10,{S+10} Q{120+i*40},{S-150+i*45} {420-i*50},{S+10}Z" fill="{c}"/>' for i, c in enumerate(OCHRE))

save('corner-top-back', BACK, top(3, 5, 640, 92, [(430, 470)]), 'b', 2, 6)
save('corner-top-front', FRONT, top(7, 3, 470, 78, [(250, 330)]), 'f', 7, 7)
save('corner-bottom-back', BACK, bottom(5, 5, 620, 92, [(470, 120, -1.2)]), 'b', 2, 6)
save('corner-bottom-front', FRONT, bottom(9, 3, 460, 80, [(300, 100, -1.0)]), 'f', 7, 7, under=mound)
print('ok')
