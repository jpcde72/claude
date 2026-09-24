import os
OUT="/sessions/gracious-epic-keller/mnt/sunrise/tropical-channel-system/assets/ideograms"
os.makedirs(OUT,exist_ok=True)
PAL=["#4B2E83","#7B3FAB","#C026A0","#F05A28","#F78DA7","#FFCC00"]
W="#FFFFFF"
S='stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" fill="none"'

# Each ideogram: white line work + one accent in palette colour. 64x64 grid.
ICONS = {
 "horizon-sun": ('#FFCC00', f'''
  <line x1="8" y1="44" x2="56" y2="44" stroke="{W}" {S}/>
  <path d="M 20 44 A 12 12 0 0 1 44 44" stroke="ACC" {S}/>
  <line x1="32" y1="20" x2="32" y2="14" stroke="ACC" {S}/>
  <line x1="18" y1="26" x2="14" y2="22" stroke="ACC" {S}/>
  <line x1="46" y1="26" x2="50" y2="22" stroke="ACC" {S}/>'''),
 "delta-curve": ('#F05A28', f'''
  <path d="M 10 48 C 22 48 26 18 38 18 C 46 18 50 30 54 30" stroke="{W}" {S}/>
  <path d="M 10 40 C 20 40 24 28 32 28" stroke="ACC" {S} stroke-dasharray="1 7"/>
  <circle cx="54" cy="30" r="3" fill="ACC" stroke="none"/>'''),
 "strategy-compass": ('#C026A0', f'''
  <circle cx="32" cy="32" r="20" stroke="{W}" {S}/>
  <path d="M 24 40 C 28 36 30 26 42 22" stroke="ACC" {S}/>
  <circle cx="42" cy="22" r="3" fill="ACC" stroke="none"/>'''),
 "audience-horizons": ('#F78DA7', f'''
  <path d="M 10 24 C 20 18 44 18 54 24" stroke="{W}" {S}/>
  <path d="M 10 36 C 20 30 44 30 54 36" stroke="ACC" {S}/>
  <path d="M 10 48 C 20 42 44 42 54 48" stroke="{W}" {S}/>'''),
 "signal-arcs": ('#7B3FAB', f'''
  <circle cx="20" cy="44" r="4" fill="{W}" stroke="none"/>
  <path d="M 28 36 A 12 12 0 0 1 32 44" stroke="ACC" {S}/>
  <path d="M 34 28 A 22 22 0 0 1 42 44" stroke="ACC" {S}/>
  <path d="M 40 20 A 32 32 0 0 1 52 44" stroke="{W}" {S}/>'''),
 "growth-sunrise": ('#FFCC00', f'''
  <path d="M 10 50 C 26 50 34 22 54 16" stroke="{W}" {S}/>
  <path d="M 46 16 L 54 16 L 54 24" stroke="ACC" {S}/>'''),
 "network-latitudes": ('#C026A0', f'''
  <path d="M 10 32 C 24 22 40 42 54 32" stroke="{W}" {S}/>
  <circle cx="17" cy="27" r="3.5" fill="ACC" stroke="none"/>
  <circle cx="32" cy="32" r="3.5" fill="{W}" stroke="none"/>
  <circle cx="47" cy="37" r="3.5" fill="ACC" stroke="none"/>'''),
 "idea-radiant": ('#F05A28', f'''
  <circle cx="32" cy="30" r="9" stroke="ACC" {S}/>
  <path d="M 32 12 L 32 7 M 45 17 L 49 13 M 50 30 L 55 30 M 19 17 L 15 13 M 14 30 L 9 30" stroke="{W}" {S}/>
  <path d="M 27 44 C 27 50 37 50 37 44" stroke="{W}" {S}/>'''),
 "flow-channels": ('#7B3FAB', f'''
  <path d="M 10 20 C 24 20 40 12 54 16" stroke="{W}" {S}/>
  <path d="M 10 32 C 24 32 40 32 54 32" stroke="ACC" {S}/>
  <path d="M 10 44 C 24 44 40 52 54 48" stroke="{W}" {S}/>'''),
 "focus-zenith": ('#FFCC00', f'''
  <path d="M 10 46 C 22 46 28 20 54 18" stroke="{W}" {S}/>
  <circle cx="36" cy="27" r="6" stroke="ACC" {S}/>
  <circle cx="36" cy="27" r="1.5" fill="ACC" stroke="none"/>'''),
}
for name,(acc,body) in ICONS.items():
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">{body.replace("ACC",acc)}</svg>'
    open(f"{OUT}/jp-ideo-{name}.svg","w").write(svg)

# contact sheet on black for review
cells=""
for i,(name,(acc,body)) in enumerate(ICONS.items()):
    x=(i%5)*130+30; y=(i//5)*150+30
    cells+=f'<g transform="translate({x},{y})"><rect x="-12" y="-12" width="88" height="88" rx="14" fill="#161616"/>{body.replace("ACC",acc)}<text x="32" y="106" text-anchor="middle" font-family="Courier New" font-size="10" fill="#B0B0B0">{name}</text></g>'
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 710 330"><rect width="710" height="330" fill="#0A0A0A"/>{cells}</svg>'
open(f"{OUT}/jp-ideogram-sheet.svg","w").write(svg)
import cairosvg
cairosvg.svg2png(url=f"{OUT}/jp-ideogram-sheet.svg", write_to="/sessions/gracious-epic-keller/mnt/outputs/ideogram-sheet.png", output_width=900)
print("done", sorted(os.listdir(OUT)))
