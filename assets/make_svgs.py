"""Generates the profile art: a daytime-sky, point-and-shoot look (dot-matrix clouds,
a dotted skyline, a sun flare and an orange digicam date stamp), set in Dotemp 8bit.
Deterministic (seeded). Run: python3 assets/make_svgs.py"""
import base64
import random
from pathlib import Path

OUT = Path(__file__).parent
FONTS = OUT / "fonts"
SKY_TOP = "#3f8fe0"
SKY_MID = "#79b7f0"
SKY_LOW = "#cfe6fb"
NAVY = "#0d2340"
INK = "#14304f"
CLOUD = "#ffffff"
STAMP = "#ff9d2e"
CITY = "#5d7593"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def font_face(name, file):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return f"@font-face{{font-family:'{name}';src:url(data:font/ttf;base64,{data}) format('truetype');}}"


def defs(h):
    return f'''<defs><style>{font_face("dt", "dotemp-8bit.ttf")}</style>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{SKY_TOP}"/><stop offset=".55" stop-color="{SKY_MID}"/><stop offset="1" stop-color="{SKY_LOW}"/></linearGradient>
  <radialGradient id="sun"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset=".12" stop-color="#fff" stop-opacity=".95"/>
    <stop offset=".35" stop-color="#fffbe6" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <filter id="soft"><feGaussianBlur stdDeviation="1.2"/></filter>
  <filter id="stampglow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="1.4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>'''


def dither_cloud(rng, cx, cy, w, h, grid=5, size=2.6):
    """A dot-matrix cumulus: a few overlapping puffs, dithered into a grid of dots."""
    puffs = [(cx + rng.uniform(-w * .6, w * .6), cy + rng.uniform(-h * .35, h * .2), rng.uniform(h * .55, h * .95)) for _ in range(10)]
    out = []
    for gx in range(int(cx - w), int(cx + w), grid):
        for gy in range(int(cy - h), int(cy + h), grid):
            d = min(((gx - px) ** 2 + (gy - py) ** 2) ** .5 / pr for px, py, pr in puffs)
            if d < 1 and gy < cy + h * .4:
                if rng.random() < (1 - d) * 2.6 + .15:
                    out.append(f'<rect x="{gx}" y="{gy}" width="{size}" height="{size}" fill="{CLOUD}" opacity="{min(1, .45 + (1 - d)):.2f}"/>')
    return "".join(out)


def drifting(cloud_svg, dx, dur):
    return (f'<g>{cloud_svg}<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{dx} 0;0 0" dur="{dur}s" repeatCount="indefinite"/></g>')


def skyline(rng, w, base, grid=5, tower_x=None):
    """A dotted skyline: windows as dots, plus a needle tower with a pod."""
    out = []
    x = 0
    while x < w:
        bw = rng.choice([30, 40, 50, 60, 70])
        bh = rng.choice([30, 45, 60, 80, 100, 120])
        for gx in range(x, x + bw - 6, grid):
            for gy in range(base - bh, base, grid):
                if rng.random() < .72:
                    out.append(f'<rect x="{gx}" y="{gy}" width="2.4" height="2.4" fill="{CITY}" opacity="{rng.uniform(.35, .8):.2f}"/>')
        x += bw + rng.choice([4, 8, 12])
    if tower_x:
        top = base - 230
        for gy in range(top, base, grid):  # needle
            out.append(f'<rect x="{tower_x}" y="{gy}" width="2.6" height="2.6" fill="{INK}" opacity=".75"/>')
        for gy in range(base - 150, base, grid):  # legs
            spread = (gy - (base - 150)) * .08
            for sx in (-spread, spread):
                out.append(f'<rect x="{tower_x + sx:.1f}" y="{gy}" width="2.6" height="2.6" fill="{INK}" opacity=".7"/>')
        for gx in range(tower_x - 14, tower_x + 17, grid):  # pod
            for gy in range(base - 172, base - 158, grid):
                out.append(f'<rect x="{gx}" y="{gy}" width="2.6" height="2.6" fill="{INK}" opacity=".8"/>')
    return "".join(out)


def sun(cx, cy, r):
    rays = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{cx + r * 1.25 * c}" y2="{cy + r * 1.25 * s}" stroke="#fff" stroke-opacity=".28" stroke-width="1"/>'
        for c, s in [(1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, -.7), (.7, -.7), (-.7, .7)])
    return (f'<g>{rays}<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#sun)">'
            f'<animate attributeName="r" values="{r};{r * 1.08};{r}" dur="5s" repeatCount="indefinite"/></circle></g>')


def stamp(x, y, text, size=26, anchor="end"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{MONO}" font-size="{size}" font-weight="700" '
            f'letter-spacing="2" fill="{STAMP}" filter="url(#stampglow)">{text}</text>')


def banner():
    W, H = 1200, 420
    rng = random.Random(11)
    clouds = [
        drifting(dither_cloud(rng, 800, 110, 170, 60), 30, 40),
        drifting(dither_cloud(rng, 1070, 200, 130, 48), -25, 34),
        drifting(dither_cloud(rng, 560, 240, 120, 44), 20, 46),
    ]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="radhika kundnani. designer or developer? yes.">
{defs(H)}
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{sun(700, 300, 90)}
{''.join(clouds)}
<g>{skyline(rng, W, H, tower_x=1000)}</g>
<text x="66" y="92" font-family="{MONO}" font-size="14" letter-spacing="2.5" fill="{NAVY}" opacity=".7">● ~/radhika · up in the clouds</text>
<text x="62" y="196" font-family="dt" font-size="100" fill="{NAVY}">radhika</text>
<text x="62" y="292" font-family="dt" font-size="100" fill="{NAVY}">kundnani<tspan fill="#fff">.</tspan></text>
<text x="66" y="346" font-family="dt" font-size="34" fill="#fff">designer or developer? yes.</text>
{stamp(W - 40, H - 28, "24/11/2026  14:40")}
</svg>'''
    (OUT / "banner.svg").write_text(svg)


def header(slug, title, index):
    W, H = 1200, 100
    rng = random.Random(len(slug) * 7)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}">
{defs(H)}
<rect width="{W}" height="{H}" rx="16" fill="url(#sky)"/>
{drifting(dither_cloud(rng, 880, 62, 150, 40, grid=5, size=2.4), 25, 30)}
{drifting(dither_cloud(rng, 560, 70, 100, 32, grid=5, size=2.3), -18, 26)}
<text x="40" y="64" font-family="dt" font-size="44" fill="{NAVY}">{title}</text>
{stamp(W - 36, 64, index, size=20)}
</svg>'''
    (OUT / f"h-{slug}.svg").write_text(svg)


def footer():
    W, H = 1200, 260
    rng = random.Random(4)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="let's make something.">
{defs(H)}
<rect width="{W}" height="{H}" rx="16" fill="url(#sky)"/>
{sun(220, 70, 60)}
{drifting(dither_cloud(rng, 980, 70, 120, 34), -20, 36)}
<g>{skyline(rng, W, H, tower_x=1090)}</g>
<text x="{W / 2}" y="112" text-anchor="middle" font-family="dt" font-size="66" fill="{NAVY}">let's make something<tspan fill="#fff">.</tspan></text>
<text x="{W / 2}" y="158" text-anchor="middle" font-family="dt" font-size="26" fill="{INK}">radhikakundnani1@gmail.com</text>
{stamp(36, H - 22, "see you up here", size=18, anchor="start")}
</svg>'''
    (OUT / "footer.svg").write_text(svg)


banner()
header("built", "things i've made", "01")
header("stack", "my toolbox", "02")
header("signal", "showing up daily", "03")
footer()
print("ok")
