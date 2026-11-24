"""Generates the profile's SVG art: a dot-matrix space banner, a divider and a footer.
Deterministic (seeded) so re-running gives the same stars. Run: python3 assets/make_svgs.py"""
import math
import random
from pathlib import Path

OUT = Path(__file__).parent
BG = "#06060c"
INDIGO = "#6c63ff"
LILAC = "#c7b8ff"
WHITE = "#e9e6ff"

# 5x7 dot font for the letters we need
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01111"],
    "' ": ["00000"] * 7,
    " ": ["000"] * 7,
}


def dot_text(text, x0, y0, pitch, r, color, glow=True):
    out, x = [], x0
    for ch in text:
        rows = FONT[ch]
        for j, row in enumerate(rows):
            for i, bit in enumerate(row):
                if bit == "1":
                    out.append(f'<circle cx="{x + i * pitch:.1f}" cy="{y0 + j * pitch:.1f}" r="{r}" fill="{color}"/>')
        x += (len(rows[0]) + 1) * pitch
    g = ' filter="url(#glow)"' if glow else ""
    return f'<g{g}>' + "".join(out) + "</g>", x - pitch


def width_of(text, pitch):
    return sum((len(FONT[c][0]) + 1) * pitch for c in text) - pitch


def stars(rng, w, h, n, twinkle_every=7):
    out = []
    for k in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.choice([0.6, 0.8, 1.0, 1.2, 1.6])
        col = rng.choice([WHITE, WHITE, LILAC, INDIGO])
        op = rng.uniform(0.25, 0.9)
        anim = ""
        if k % twinkle_every == 0:
            d = rng.uniform(2.5, 6)
            anim = (f'<animate attributeName="opacity" values="{op:.2f};0.05;{op:.2f}" dur="{d:.1f}s" '
                    f'begin="{rng.uniform(0, 4):.1f}s" repeatCount="indefinite"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" opacity="{op:.2f}">{anim}</circle>')
    return "".join(out)


def nebula_dots(rng, cx, cy, rx, ry, n, color):
    """A dithered dot cloud (the 'dot-matrix flower' texture), denser in the middle."""
    out = []
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        t = abs(rng.gauss(0, 0.45))
        x = cx + math.cos(a) * rx * t
        y = cy + math.sin(a) * ry * t
        x, y = round(x / 6) * 6, round(y / 6) * 6  # snap to a grid so it reads as dot-matrix
        out.append(f'<rect x="{x}" y="{y}" width="2.6" height="2.6" fill="{color}" opacity="{max(0.15, 0.9 - t):.2f}"/>')
    return "".join(out)


DEFS = f'''<defs>
  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <radialGradient id="haze" cx="78%" cy="40%" r="55%"><stop offset="0" stop-color="{INDIGO}" stop-opacity=".28"/>
    <stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
</defs>'''
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def banner():
    W, H = 1200, 330
    rng = random.Random(27)
    name1, name2 = "RADHIKA", "KUNDNANI"
    pitch, r = 9.2, 3.2
    t1, _ = dot_text(name1, 70, 70, pitch, r, WHITE)
    t2, _ = dot_text(name2, 70, 150, pitch, r, LILAC)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Radhika Kundnani: AI engineering and design">
{DEFS}
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#haze)"/>
{stars(rng, W, H, 260)}
{nebula_dots(rng, 940, 150, 260, 120, 900, INDIGO)}
{nebula_dots(rng, 960, 140, 150, 70, 380, LILAC)}
<g fill="none" stroke="{LILAC}" stroke-opacity=".55" stroke-width="1.2" stroke-dasharray="2 7">
  <ellipse cx="960" cy="150" rx="210" ry="46" transform="rotate(-14 960 150)">
    <animateTransform attributeName="transform" type="rotate" from="-14 960 150" to="346 960 150" dur="90s" repeatCount="indefinite"/></ellipse>
</g>
<circle cx="960" cy="150" r="34" fill="{BG}" stroke="{WHITE}" stroke-width="1.4" stroke-dasharray="1.5 4"/>
<circle r="4" fill="{WHITE}" filter="url(#glow)"><animateMotion dur="14s" repeatCount="indefinite" path="M 760 196 A 210 46 -14 1 1 1160 104 A 210 46 -14 1 1 760 196"/></circle>
{t1}
{t2}
<text x="72" y="250" font-family="{MONO}" font-size="17" letter-spacing="5" fill="{LILAC}">AI ENGINEERING  ·  PRODUCT  ·  DESIGN</text>
<text x="72" y="282" font-family="{MONO}" font-size="14" letter-spacing="3" fill="{WHITE}" opacity=".7">CS @ VIT VELLORE · BANGALORE · BUILDING THINGS PEOPLE ACTUALLY USE</text>
<rect x="1090" y="262" width="10" height="10" fill="none" stroke="{LILAC}"/>
<text x="1060" y="290" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{WHITE}" opacity=".6">AWAKEN</text>
</svg>'''
    (OUT / "banner.svg").write_text(svg)


def divider():
    W, H = 1200, 24
    rng = random.Random(5)
    dots = "".join(
        f'<rect x="{x}" y="{10 + rng.choice([-4, 0, 0, 4])}" width="3" height="3" fill="{rng.choice([INDIGO, LILAC, WHITE])}" opacity="{rng.uniform(.3, 1):.2f}"/>'
        for x in range(0, W, 9))
    (OUT / "divider.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="{BG}"/>{dots}</svg>')


def footer():
    W, H = 1200, 170
    rng = random.Random(9)
    text = "LETS BUILD"
    pitch, r = 7, 2.5
    w = width_of(text, pitch)
    t, _ = dot_text(text, (W - w) / 2, 40, pitch, r, WHITE)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Let's build something">
{DEFS}
<rect width="{W}" height="{H}" fill="{BG}"/>
{stars(rng, W, H, 140, 5)}
{t}
<text x="{W/2}" y="130" text-anchor="middle" font-family="{MONO}" font-size="14" letter-spacing="6" fill="{LILAC}">SOMETHING  ·  TOGETHER  □</text>
</svg>'''
    (OUT / "footer.svg").write_text(svg)


banner()
divider()
footer()
print("wrote banner.svg, divider.svg, footer.svg")
