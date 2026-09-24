import math, os
OUT = "/sessions/gracious-epic-keller/mnt/sunrise/tropical-channel-system/assets"

# Palette: violet (23.44N, biggest delta, outermost) -> solar yellow (equator, calm core)
PAL = ["#4B2E83","#7B3FAB","#C026A0","#F05A28","#F78DA7","#FFCC00"]
LATS = [23.44, 19.0, 14.5, 10.0, 5.0, 0.8]

def sunrise_hour(lat_deg, day):
    decl = -23.44*math.cos(2*math.pi/365.0*(day+10))
    x = -math.tan(math.radians(lat_deg))*math.tan(math.radians(decl))
    x = max(-1,min(1,x))
    return 12 - math.degrees(math.acos(x))/15.0

def curve_points(lat, W, H, cy, amp, x0=0):
    pts=[]
    vals=[sunrise_hour(lat,d) for d in range(0,366,3)]
    mn,mx=min(vals),max(vals)
    base=[(v-6.0) for v in vals]  # delta from 6:00 equatorial sunrise
    n=len(vals)
    for i,v in enumerate(base):
        x = x0 + W*i/(n-1)
        y = cy - v*amp
        pts.append((x,y))
    return pts

def path(pts):
    d=f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    for x,y in pts[1:]:
        d+=f" L {x:.1f} {y:.1f}"
    return d

def mark_svg(W=900, H=520, bg=None, stroke=11, gap=30):
    cy = H*0.52
    layers=[]
    defs = '''<defs><filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
<feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'''
    body=""
    if bg: body += f'<rect width="{W}" height="{H}" fill="{bg}"/>'
    body += defs
    for i,(lat,col) in enumerate(zip(LATS,PAL)):
        amp = 85  # px per hour of delta
        offset = (i - (len(LATS)-1)/2) * gap
        pts = curve_points(lat, W*0.86, H, cy+offset, amp, x0=W*0.07)
        body += f'<path d="{path(pts)}" fill="none" stroke="{col}" stroke-width="{stroke}" stroke-linecap="round" opacity="0.28" filter="url(#glow)"/>'
        body += f'<path d="{path(pts)}" fill="none" stroke="{col}" stroke-width="{stroke}" stroke-linecap="round"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{body}</svg>'

# 1. mark transparent + black
open(f"{OUT}/jp-tropical-mark-transparent.svg","w").write(mark_svg())
open(f"{OUT}/jp-tropical-mark-black.svg","w").write(mark_svg(bg="#0A0A0A"))

# 2. latitude accent bar (6 segments)
W=1200;H=12
segs="".join(f'<rect x="{i*W/6:.0f}" y="0" width="{W/6:.0f}" height="{H}" fill="{c}"/>' for i,c in enumerate(PAL))
open(f"{OUT}/jp-tropical-latitude-bar.svg","w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{segs}</svg>')
# gradient variant
stops="".join(f'<stop offset="{i/5:.2f}" stop-color="{c}"/>' for i,c in enumerate(PAL))
open(f"{OUT}/jp-tropical-sweep-gradient-bar.svg","w").write(
 f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient></defs><rect width="{W}" height="{H}" fill="url(#g)"/></svg>')

# 3. avatar 800x800: tight crop of curves on black
def avatar(W=800,H=800):
    cy=H*0.55; body=f'<rect width="{W}" height="{H}" fill="#0A0A0A"/>'
    body+='<defs><filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
    for i,(lat,col) in enumerate(zip(LATS,PAL)):
        offset=(i-2.5)*46
        pts=curve_points(lat, W*1.4, H, cy+offset, 110, x0=-W*0.2)
        body+=f'<path d="{path(pts)}" fill="none" stroke="{col}" stroke-width="16" stroke-linecap="round" opacity="0.28" filter="url(#glow)"/>'
        body+=f'<path d="{path(pts)}" fill="none" stroke="{col}" stroke-width="16" stroke-linecap="round"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{body}</svg>'
open(f"{OUT}/jp-tropical-avatar.svg","w").write(avatar())

# 4. LinkedIn banner 1584x396
def banner(W=1584,H=396):
    cy=H*0.5; body=f'<rect width="{W}" height="{H}" fill="#0A0A0A"/>'
    body+='<defs><filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
    for i,(lat,col) in enumerate(zip(LATS,PAL)):
        offset=(i-2.5)*22
        pts=curve_points(lat, W*1.1, H, cy+offset, 55, x0=-W*0.05)
        body+=f'<path d="{path(pts)}" fill="none" stroke="{col}" stroke-width="8" stroke-linecap="round" opacity="0.25" filter="url(#glow)"/>'
        body+=f'<path d="{path(pts)}" fill="none" stroke="{col}" stroke-width="8" stroke-linecap="round"/>'
    body+=f'<text x="64" y="{H-48}" font-family="Georgia, serif" font-size="44" fill="#FFFFFF" font-style="italic">jean-paul</text>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{body}</svg>'
open(f"{OUT}/jp-tropical-banner-linkedin.svg","w").write(banner())
print("done", os.listdir(OUT))
