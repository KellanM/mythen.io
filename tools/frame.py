# mythen.io's jungle as a frame: a few huge, simple shapes growing in from the screen's
# corners (a proscenium round the sheet), two depths, flat colour, sprayed edges.
# Uses the shape kit in bold.py. Writes corner-top-*.svg and corner-bottom-*.svg (the
# right-hand corners are these, mirrored by the page). python tools/frame.py
import math, random, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from bold import blade, trunk, spray, pt, smooth, OCHRE
from bold import frond as _frond
from stipple import spray as droplets, dots_only, kusama, kusama2, kusama3, kusama4, kusama6

def frond(base, ang, L, W, teeth=8, curl=0.0):
    return _frond(base, ang, L, W, teeth=teeth, curl=curl)

def leaf(c, ang, s):
    # a broad leaf with a pointed tip, Matisse-like: wide near the stalk, drawn to a point
    pts = [pt(c, ang, s * u, s * v) for u, v in ((0, 0), (0.25, 0.42), (0.6, 0.5), (1.0, 0.36), (1.45, 0.12), (1.7, 0), (1.45, -0.12), (1.0, -0.36), (0.6, -0.5), (0.25, -0.42))]
    return smooth(pts)
heart = leaf
OUT = os.environ.get('OUT') or os.path.join(os.path.dirname(__file__), '..')
# the edges: 'stipple' (clean shapes and an overspray of real round droplets, tools/stipple.py) or 'spray'
# (the old SVG filter: a displaced edge and a noise speckle, which read as JPEG noise). STIPPLE tunes the droplets.
STYLE = os.environ.get('STYLE', 'kusama')   # Kellan's pick, 2026-10-28: every leaf filled with dots, after Kusama's pumpkin
DROPS = dict(reach=18, density=0.5)
KUSAMA = dict(k=0.8, gap=6, rmin=4)   # the medium, even gap (Kellan's pick) - 'kusama': rows of graded dots following each shape's outline (tools/stipple.py); KUSAMA env as k=v,k=v
if os.environ.get('KUSAMA'): KUSAMA.update({k: float(v) for k, v in (kv.split('=') for kv in os.environ['KUSAMA'].split(','))})
DOTS = {}   # 'dots': the whole shape as droplets (tools/stipple.py dots_only); DOTS env as k=v,k=v
if os.environ.get('DOTS'): DOTS.update({k: float(v) for k, v in (kv.split('=') for kv in os.environ['DOTS'].split(','))})
if os.environ.get('STIPPLE'): DROPS.update({k: float(v) for k, v in (kv.split('=') for kv in os.environ['STIPPLE'].split(','))})
BACK, FRONT = '#7f9a4a', '#2f4426'
S = 800   # each corner is drawn in an 800 x 800 box, anchored at its corner
E = 600   # and runs on E past the screen's edge: Safari (iOS 26) draws the page under its bars, so the plants carry on under them

def save(name, colour, shapes, fid, halo, rough, under='', edge='top'):
    vb = f"0 {-E} {S} {S + E}" if edge == 'top' else f"0 0 {S} {S + E}"
    if STYLE in ('dots', 'kusama'):
        y0 = -E if edge == 'top' else 0
        box = (-200, y0 - 200, S + 400, S + E + 400); sd = len(name) * 7 + ord(name[7])
        dots = (({'2': kusama2, '3': kusama3, '4': kusama4, '6': kusama6}.get(os.environ.get('K2', '6'), kusama))(shapes, box, seed=sd, **KUSAMA) if STYLE == 'kusama' else dots_only(shapes, box, seed=sd, **DOTS))[0]
        open(f"{OUT}/{name}.svg", "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{S}" height="{S + E}" aria-hidden="true">{under}<path d="{dots}" fill="{colour}"/></svg>')
        return
    if STYLE == 'stipple':
        y0 = -E if edge == 'top' else 0
        dots, _ = droplets(shapes, (-200, y0 - 200, S + 400, S + E + 400), seed=len(name) * 7 + ord(name[7]), tilt=(0.5, -0.5), **DROPS)
        body = f'<path d="{" ".join(shapes)}" fill="{colour}"/><path d="{dots}" fill="{colour}"/>'
        open(f"{OUT}/{name}.svg", "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{S}" height="{S + E}" aria-hidden="true">{under}{body}</svg>')
        return
    body = f'<g filter="url(#{fid})"><path d="{" ".join(shapes)}" fill="{colour}"/></g>'
    open(f"{OUT}/{name}.svg", "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{S}" height="{S + E}" aria-hidden="true">'
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
        sh.append(trunk(x, S + E, stalk_top[1], 18, 12, stalk_top[0] - x))
        sh.append(heart(stalk_top, a, s))
    return sh

mound = ''.join(f'<path d="M-10,{S+E} L-10,{S+10} Q{120+i*40},{S-150+i*45} {420-i*50},{S+10} Q{440-i*50},{S+120} {560-i*50},{S+E}Z" fill="{c}"/>' for i, c in enumerate(OCHRE))

# four different corners, weighted on the diagonal (Kellan, 2026-10-28: asymmetry, the
# rule of thirds): heavy top-left and bottom-right, light top-right and bottom-left. The
# right-hand corners are drawn as left ones and mirrored by the page, but each is its own.
save('corner-tl-back', BACK, top(3, 6, 680, 96, []), 'b', 2, 6)
save('corner-tl-front', FRONT, top(7, 3, 500, 82, []), 'f', 7, 7)
save('corner-tr-back', BACK, top(13, 3, 520, 84, []), 'b', 2, 6)
save('corner-tr-front', FRONT, top(17, 2, 380, 70, []), 'f', 7, 7)
save('corner-bl-back', BACK, bottom(15, 3, 500, 84, [(330, 90, -1.1)]), 'b', 2, 6, edge='bottom')
save('corner-bl-front', FRONT, bottom(19, 2, 360, 70, []), 'f', 7, 7, under=mound, edge='bottom')
save('corner-br-back', BACK, bottom(5, 6, 660, 96, [(470, 120, -1.2), (560, 96, -0.7)]), 'b', 2, 6, edge='bottom')
save('corner-br-front', FRONT, bottom(9, 3, 480, 82, [(300, 104, -1.0)]), 'f', 7, 7, under=mound, edge='bottom')
print('ok')

# ---------------------------------------------------------------- the top: a fringe of big leaves, and two vines
# swinging from the top out to the right edge, each its own colour (Kellan, 2026-10-28)
TW, TH = 1600, 420
TE = 200   # the top, too, runs on above the screen, under Safari's status bar
def swag(p0, p1, p2, width, n_leaves, size, seed):
    """a vine as a thick ribbon along a quadratic swing, big leaves hanging off it"""
    random.seed(seed); sh = []
    pts = [((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0], (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]) for t in (i/40 for i in range(41))]
    sh.append("M" + " L".join(f"{x:.1f},{y - width/2:.1f}" for x, y in pts) + " L" + " L".join(f"{x:.1f},{y + width/2:.1f}" for x, y in pts[::-1]) + "Z")
    for k in range(n_leaves):
        x, y = pts[int((k + 0.5) / n_leaves * 40)]
        a = math.pi / 2 + random.uniform(-0.9, 0.9)               # hanging, each at its own angle
        sh.append(heart((x, y), a, size * random.uniform(0.8, 1.15)))
    return sh

def layer_svg(name, groups, halo, rough):
    if STYLE in ('dots', 'kusama'):
        box = (-200, -TE - 200, TW + 400, TH + TE + 400)
        body = ''.join(f'<path d="{(({'2': kusama2, '3': kusama3, '4': kusama4, '6': kusama6}.get(os.environ.get('K2', '6'), kusama))(sh, box, seed=31 + i, **KUSAMA) if STYLE == "kusama" else dots_only(sh, box, seed=31 + i + len(name), **DOTS))[0]}" fill="{c}"/>' for i, (c, sh) in enumerate(groups))
        open(f"{OUT}/{name}.svg", "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-TE} {TW} {TH + TE}" width="{TW}" height="{TH + TE}" preserveAspectRatio="xMidYMin slice" aria-hidden="true">{body}</svg>')
        return
    if STYLE == 'stipple':
        body = ''
        for i, (c, sh) in enumerate(groups):
            dots, _ = droplets(sh, (-200, -TE - 200, TW + 400, TH + TE + 400), seed=31 + i + len(name), tilt=(0.5, 0.5), **DROPS)
            body += f'<path d="{" ".join(sh)}" fill="{c}"/><path d="{dots}" fill="{c}"/>'
        open(f"{OUT}/{name}.svg", "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-TE} {TW} {TH + TE}" width="{TW}" height="{TH + TE}" preserveAspectRatio="xMidYMin slice" aria-hidden="true">{body}</svg>')
        return
    defs = ''.join(spray(f'g{i}', c, halo, rough) for i, (c, _) in enumerate(groups))
    body = ''.join(f'<g filter="url(#g{i})"><path d="{" ".join(sh)}" fill="{c}"/></g>' for i, (c, sh) in enumerate(groups))
    open(f"{OUT}/{name}.svg", "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-TE} {TW} {TH + TE}" width="{TW}" height="{TH + TE}" preserveAspectRatio="xMidYMin slice" aria-hidden="true"><defs>{defs}</defs>{body}</svg>')

random.seed(41); fringe = []
for x in range(60, TW - 100, 110):                               # big leaves along the top edge, thick on the left
    w = max(0.0, 1 - x / (TW * 0.72))                            # 1 at the left, nothing past ~70% across
    if random.random() > w * 1.25: continue
    for k in range(1 + int(w * 3)):
        fringe.append(heart((x + random.uniform(-40, 40), random.uniform(-30, 10)), math.pi/2 + random.uniform(-0.7, 0.7), random.uniform(70, 110)))
for x in range(40, int(TW * 0.75), 90):                          # and more above them, under the status bar
    if random.random() > 1.1 - x / TW: fringe.append(heart((x + random.uniform(-30, 30), random.uniform(-190, -110)), math.pi/2 + random.uniform(-0.8, 0.8), random.uniform(80, 120)))
VINE_A, VINE_B = '#9a5530', '#9db45a'                             # red-ochre brown; a light, sunlit olive
layer_svg('top-back', [(BACK, fringe)], 2, 6)   # the red-ochre vine is gone (Kellan, 2026-10-28)
vine = swag((520, -20), (1050, 380), (TW + 40, 40), 12, 8, 70, 47)
vine.append("M514,-20 L496,-230 L508,-230 L526,-20Z")         # where it hangs from, above the screen
layer_svg('top-front', [(VINE_B, vine)], 6, 6)
print('top ok')
