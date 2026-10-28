# Flat vine silhouettes for mythen.io: a stem along a cubic path, almond leaves
# alternating along it (turned to the stem), and a few curling tendrils.
import math, random, sys
def cubic(p0,p1,p2,p3,t):
    u=1-t; return tuple(u*u*u*a+3*u*u*t*b+3*u*t*t*c+t*t*t*d for a,b,c,d in zip(p0,p1,p2,p3))
def deriv(p0,p1,p2,p3,t):
    u=1-t; return tuple(3*u*u*(b-a)+6*u*t*(c-b)+3*t*t*(d-c) for a,b,c,d in zip(p0,p1,p2,p3))
def leaf(x,y,ang,L,W):
    # an almond: two quadratic curves from base to tip
    ca,sa=math.cos(ang),math.sin(ang)
    P=lambda u,v:(x+u*ca-v*sa, y+u*sa+v*ca)
    b=P(0,0); t=P(L,0); c1=P(L*0.45,W); c2=P(L*0.55,-W)
    return f"M{b[0]:.1f},{b[1]:.1f} Q{c1[0]:.1f},{c1[1]:.1f} {t[0]:.1f},{t[1]:.1f} Q{c2[0]:.1f},{c2[1]:.1f} {b[0]:.1f},{b[1]:.1f}Z"
def tendril(x,y,ang,r,turns,side):
    pts=[]; n=28
    for i in range(n+1):
        k=i/n; a=ang+side*k*turns*2*math.pi; rr=r*(1-0.85*k)
        pts.append((x+ (k*r*1.6)*math.cos(ang) + rr*math.cos(a)-r*math.cos(ang), y+(k*r*1.6)*math.sin(ang)+rr*math.sin(a)-r*math.sin(ang)))
    return "M"+" L".join(f"{a:.1f},{b:.1f}" for a,b in pts)
def vine(segs,seed,leaf_every=34,L=(18,30),W=(6,10)):
    random.seed(seed); stem=[]; leaves=[]; tend=[]; side=1; dist=0; last=None
    d="M%.1f,%.1f"%segs[0][0]
    for (p0,p1,p2,p3) in segs:
        d+=" C%.1f,%.1f %.1f,%.1f %.1f,%.1f"%(*p1,*p2,*p3)
        for i in range(1,121):
            t=i/120; p=cubic(p0,p1,p2,p3,t)
            if last: dist+=math.dist(p,last)
            last=p
            if dist>=leaf_every:
                dist=0; dx,dy=deriv(p0,p1,p2,p3,t); a=math.atan2(dy,dx)
                if random.random()<0.12: tend.append(tendril(p[0],p[1],a+side*1.0,random.uniform(7,11),1.3,side))
                else: leaves.append(leaf(p[0],p[1],a+side*random.uniform(0.7,1.1),random.uniform(*L),random.uniform(*W)))
                side=-side
    return d," ".join(leaves),tend
def svg(w,h,vines,fill):
    # spray paint: the edges roughened, and a speckled overspray just outside them
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-12 -12 {w+24} {h+24}" width="{w+24}" height="{h+24}" aria-hidden="true">',
      '<defs><filter id="spray" x="-10%" y="-10%" width="120%" height="120%">'
      '<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="4" result="grain"/>'
      '<feDisplacementMap in="SourceGraphic" in2="grain" scale="2.6" xChannelSelector="R" yChannelSelector="G" result="rough"/>'
      '<feGaussianBlur in="SourceAlpha" stdDeviation="3.2" result="halo"/>'
      '<feTurbulence type="fractalNoise" baseFrequency="1.9" numOctaves="1" seed="9" result="dots"/>'
      '<feColorMatrix in="dots" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 9 -5.2" result="dotmask"/>'
      '<feComposite in="halo" in2="dotmask" operator="in" result="speckle"/>'
      f'<feFlood flood-color="{fill}"/><feComposite in2="speckle" operator="in" result="paint"/>'
      '<feMerge><feMergeNode in="paint"/><feMergeNode in="rough"/></feMerge></filter></defs>',
      '<g filter="url(#spray)">']
    for d,lv,tend,sw in vines:
        out.append(f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{sw}" stroke-linecap="round"/>')
        out.append(f'<path d="{lv}" fill="{fill}"/>')
        for t in tend: out.append(f'<path d="{t}" fill="none" stroke="{fill}" stroke-width="1.6" stroke-linecap="round"/>')
    out.append('</g></svg>'); return "\n".join(out)
F="#cdE1a4".lower()
# Where the Wild Things Are scale: thick hanging vines and big leaves, framing the page
def tapered(segs,seed,w0,w1,**kw):
    # the stem drawn as pieces that thin towards the tip, leaves along it
    d,lv,tend=vine(segs,seed,**kw); out=[]
    n=len(segs)
    for k,(p0,p1,p2,p3) in enumerate(segs):
        w=w0+(w1-w0)*k/max(1,n-1)
        out.append((f"M{p0[0]:.1f},{p0[1]:.1f} C{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}", w))
    return out,lv,tend
def svg2(w,h,parts,fill):
    o=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -20 {w+40} {h+40}" width="{w+40}" height="{h+40}" aria-hidden="true">',
      '<defs><filter id="spray" x="-10%" y="-10%" width="120%" height="120%">'
      '<feTurbulence type="fractalNoise" baseFrequency="0.55" numOctaves="2" seed="4" result="grain"/>'
      '<feDisplacementMap in="SourceGraphic" in2="grain" scale="5" xChannelSelector="R" yChannelSelector="G" result="rough"/>'
      '<feGaussianBlur in="SourceAlpha" stdDeviation="6" result="halo"/>'
      '<feTurbulence type="fractalNoise" baseFrequency="1.3" numOctaves="1" seed="9" result="dots"/>'
      '<feColorMatrix in="dots" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 10 -5.4" result="dotmask"/>'
      '<feComposite in="halo" in2="dotmask" operator="in" result="speckle"/>'
      f'<feFlood flood-color="{fill}"/><feComposite in2="speckle" operator="in" result="paint"/>'
      '<feMerge><feMergeNode in="paint"/><feMergeNode in="rough"/></feMerge></filter></defs><g filter="url(#spray)">']
    for stems,lv,tend in parts:
        for d,sw in stems: o.append(f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{sw:.1f}" stroke-linecap="round"/>')
        o.append(f'<path d="{lv}" fill="{fill}"/>')
        for t in tend: o.append(f'<path d="{t}" fill="none" stroke="{fill}" stroke-width="3.5" stroke-linecap="round"/>')
    o.append('</g></svg>'); return "\n".join(o)
big=dict(leaf_every=58,L=(46,78),W=(15,26))
def frond(x,y,h,lean,seed,fill):
    # a fern frond: a curved stem rising from (x,y), leaflets in pairs that shrink towards the tip
    random.seed(seed); p0=(x,y); p3=(x+lean,y-h); p1=(x+lean*0.1,y-h*0.45); p2=(x+lean*0.7,y-h*0.85)
    stem=f"M{p0[0]:.1f},{p0[1]:.1f} C{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}"; lv=[]
    n=14
    for i in range(2,n):
        t=i/n; px,py=cubic(p0,p1,p2,p3,t); dx,dy=deriv(p0,p1,p2,p3,t); a=math.atan2(dy,dx)
        size=(1-t)*0.55+0.15
        for side in (1,-1): lv.append(leaf(px,py,a+side*1.25,h*0.22*size,h*0.05*size))
    return stem," ".join(lv)
def layer(name,w,h,specs,fill,soft=False):
    parts=[tapered(segs,seed,w0,w1,**kw) for segs,seed,w0,w1,kw in specs]
    open(sys.argv[1]+f'/{name}.svg','w').write(svg2(w,h,parts,fill))
# far layer (palest): the big hanging vines from before
far_l=[([((-20,60),(140,0),(260,150),(420,70)),((420,70),(520,20),(600,110),(700,40))],3,16,7,big),
       ([((60,-20),(10,200),(150,330),(60,560)),((60,560),(0,760),(130,880),(50,1100)),((50,1100),(10,1260),(90,1360),(40,1500))],5,18,6,big),
       ([((170,40),(230,170),(140,260),(210,400)),((210,400),(250,480),(170,560),(220,640))],7,9,4,dict(leaf_every=46,L=(36,58),W=(12,20)))]
far_r=[([((560,-20),(420,220),(600,380),(470,620)),((470,620),(380,820),(560,960),(450,1200)),((450,1200),(400,1380),(520,1480),(470,1700))],8,18,6,big),
       ([((600,160),(500,240),(560,350),(420,420)),((420,420),(330,470),(380,560),(300,600))],11,10,4,dict(leaf_every=44,L=(34,56),W=(11,19)))]
layer('far-left',720,1520,far_l,"#d3e6b0"); layer('far-right',620,1720,far_r,"#d3e6b0")
# mid layer: closer, thicker, a fuller green
mid_l=[([((-20,-20),(120,180),(40,340),(160,520)),((160,520),(240,660),(90,820),(170,1000))],21,24,8,dict(leaf_every=66,L=(58,92),W=(19,30))),
       ([((-20,300),(90,330),(150,420),(260,400))],23,12,5,dict(leaf_every=50,L=(44,70),W=(14,22)))]
mid_r=[([((520,-20),(380,160),(500,330),(380,520)),((380,520),(300,680),(460,800),(360,980))],25,24,8,dict(leaf_every=66,L=(58,92),W=(19,30))),
       ([((540,640),(440,660),(400,760),(300,760))],27,12,5,dict(leaf_every=50,L=(44,70),W=(14,22)))]
layer('mid-left',520,1040,mid_l,"#b9d48c"); layer('mid-right',540,1000,mid_r,"#b9d48c")
# near layer: short, dark vines that spill over the sheet's edges
near_l=[([((-20,40),(80,60),(150,20),(240,90)),((240,90),(300,140),(280,220),(330,260))],31,14,5,dict(leaf_every=48,L=(40,64),W=(13,21)))]
near_r=[([((300,-20),(230,90),(300,170),(200,260)),((200,260),(140,320),(170,400),(110,450))],33,14,5,dict(leaf_every=48,L=(40,64),W=(13,21)))]
layer('near-left',360,300,near_l,"#93b866"); layer('near-right',320,480,near_r,"#93b866")
# the ground: ferns rising from the earth, across the bottom (tiles across)
random.seed(41); stems=[]; leaves=[]
for k in range(16):
    x=k*100+random.uniform(-25,25); hh=random.uniform(150,260); lean=random.uniform(-70,70)
    st,lv=frond(x,330,hh,lean,100+k,"#7f9f58"); stems.append(st); leaves.append(lv)
o=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 340" width="1600" height="340" preserveAspectRatio="xMidYMax slice" aria-hidden="true">',
   svg2(1,1,[],"#7f9f58").split('<g filter')[0].split('aria-hidden="true">')[1], '<g filter="url(#spray)">']
o+= [f'<path d="{st}" fill="none" stroke="#7f9f58" stroke-width="5" stroke-linecap="round"/>' for st in stems]
o+= [f'<path d="{lv}" fill="#7f9f58"/>' for lv in leaves]
o.append('</g></svg>'); open(sys.argv[1]+'/ground.svg','w').write("\n".join(o))
print('ok')
