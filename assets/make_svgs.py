"""Generates the profile's SVG art in the Trap typeface (fonts embedded, so GitHub renders them).
Deterministic (seeded) stars. Run: python3 assets/make_svgs.py

Display font: Dotemp 8bit (demo)."""
import base64
import math
import random
from pathlib import Path

OUT = Path(__file__).parent
FONTS = OUT / "fonts"
BG = "#06060c"
INDIGO = "#6c63ff"
LILAC = "#c7b8ff"
WHITE = "#ecebff"
DIM = "#8f8bb3"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def font_face(name, file):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    fmt = 'truetype' if file.endswith('.ttf') else 'opentype'
    mime = 'font/ttf' if file.endswith('.ttf') else 'font/otf'
    return f"@font-face{{font-family:'{name}';src:url(data:{mime};base64,{data}) format('{fmt}');}}"


def defs(*faces):
    css = "".join(font_face(n, f) for n, f in faces)
    return f'''<defs><style>{css}</style>
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <radialGradient id="haze" cx="80%" cy="45%" r="55%"><stop offset="0" stop-color="{INDIGO}" stop-opacity=".30"/>
    <stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
</defs>'''


def stars(rng, w, h, n, twinkle_every=6):
    out = []
    for k in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.choice([0.6, 0.8, 1.0, 1.2, 1.6])
        col = rng.choice([WHITE, WHITE, LILAC, INDIGO])
        op = rng.uniform(0.2, 0.85)
        anim = ""
        if k % twinkle_every == 0:
            anim = (f'<animate attributeName="opacity" values="{op:.2f};0.05;{op:.2f}" dur="{rng.uniform(2.5, 6):.1f}s" '
                    f'begin="{rng.uniform(0, 4):.1f}s" repeatCount="indefinite"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" opacity="{op:.2f}">{anim}</circle>')
    return "".join(out)


def dot_cloud(rng, cx, cy, rx, ry, n, color, grid=6, size=2.6):
    """Dithered dot-matrix texture, densest in the middle."""
    seen, out = set(), []
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        t = abs(rng.gauss(0, 0.45))
        x = round((cx + math.cos(a) * rx * t) / grid) * grid
        y = round((cy + math.sin(a) * ry * t) / grid) * grid
        if (x, y) in seen:
            continue
        seen.add((x, y))
        out.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{color}" opacity="{max(0.15, 0.9 - t):.2f}"/>')
    return "".join(out)


def planet(cx, cy, r, ring_rx, ring_ry, tilt):
    return f'''<g>
<ellipse cx="{cx}" cy="{cy}" rx="{ring_rx}" ry="{ring_ry}" transform="rotate({tilt} {cx} {cy})" fill="none" stroke="{LILAC}" stroke-opacity=".55" stroke-width="1.3" stroke-dasharray="2 7"/>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="{BG}" stroke="{WHITE}" stroke-width="1.4" stroke-dasharray="1.5 4"/>
<circle r="4.5" fill="{WHITE}" filter="url(#glow)"><animateMotion dur="16s" repeatCount="indefinite"
  path="M {cx - ring_rx} {cy} a {ring_rx} {ring_ry} 0 1 0 {2 * ring_rx} 0 a {ring_rx} {ring_ry} 0 1 0 {-2 * ring_rx} 0" /></circle>
</g>'''


def banner():
    W, H = 1200, 400
    rng = random.Random(27)
    cx, cy = 960, 175
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="radhika kundnani. designer or developer? yes.">
{defs(("dt", "dotemp-8bit.ttf"))}
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#haze)"/>
{stars(rng, W, H, 300)}
{dot_cloud(rng, cx, cy, 290, 140, 1100, INDIGO)}
{dot_cloud(rng, cx, cy, 150, 75, 420, LILAC)}
<g transform="rotate(-14 {cx} {cy})">{planet(cx, cy, 38, 220, 50, 0)}</g>
<circle cx="78" cy="70" r="5" fill="{LILAC}"><animate attributeName="opacity" values="1;.2;1" dur="2.4s" repeatCount="indefinite"/></circle>
<text x="94" y="75" font-family="{MONO}" font-size="14" letter-spacing="2.5" fill="{DIM}">~/radhika · online</text>
<text x="68" y="190" font-family="dt" font-size="96" fill="{WHITE}" filter="url(#glow)">radhika</text>
<text x="68" y="282" font-family="dt" font-size="96" fill="{WHITE}" filter="url(#glow)">kundnani<tspan fill="{INDIGO}">.</tspan></text>
<text x="72" y="336" font-family="dt" font-size="34" fill="{LILAC}">designer or developer? yes.</text>
<text x="73" y="370" font-family="{MONO}" font-size="13" letter-spacing="2.5" fill="{DIM}">ai engineering · product · design · bangalore</text>
<rect x="1110" y="342" width="10" height="10" fill="none" stroke="{LILAC}"/>
<text x="1062" y="372" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{DIM}">awaken</text>
</svg>'''
    (OUT / "banner.svg").write_text(svg)


def header(slug, title, index):
    W, H = 1200, 96
    rng = random.Random(hash(slug) % 1000)
    dots = "".join(
        f'<rect x="{x}" y="78" width="3" height="3" fill="{rng.choice([INDIGO, LILAC, WHITE])}" opacity="{rng.uniform(.25, .9):.2f}"/>'
        for x in range(40, W - 40, 10))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}">
{defs(("dt", "dotemp-8bit.ttf"))}
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
{stars(rng, W, H, 70, 5)}
<text x="40" y="58" font-family="dt" font-size="42" fill="{WHITE}"><tspan fill="{LILAC}">✦ </tspan>{title}</text>
<text x="{W - 40}" y="58" text-anchor="end" font-family="{MONO}" font-size="15" letter-spacing="3" fill="{DIM}">{index} □</text>
{dots}
</svg>'''
    (OUT / f"h-{slug}.svg").write_text(svg)


def footer():
    W, H = 1200, 230
    rng = random.Random(9)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="let's make something.">
{defs(("dt", "dotemp-8bit.ttf"))}
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
{stars(rng, W, H, 160, 5)}
{dot_cloud(rng, W / 2, 110, 420, 70, 500, INDIGO, grid=7)}
<text x="{W / 2}" y="118" text-anchor="middle" font-family="dt" font-size="66" fill="{WHITE}" filter="url(#glow)">let's make something<tspan fill="{INDIGO}">.</tspan></text>
<text x="{W / 2}" y="165" text-anchor="middle" font-family="dt" font-size="26" fill="{LILAC}">radhikakundnani1@gmail.com</text>
<text x="{W / 2}" y="205" text-anchor="middle" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{DIM}">made with stardust &amp; too many figma tabs □</text>
</svg>'''
    (OUT / "footer.svg").write_text(svg)


banner()
header("built", "things i've made", "01")
header("stack", "my toolbox", "02")
header("signal", "showing up daily", "03")
footer()
for old in ("divider.svg",):
    (OUT / old).unlink(missing_ok=True)
print("ok")
