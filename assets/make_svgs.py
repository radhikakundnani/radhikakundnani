"""Generates the profile art: an off-white paper look where the sky itself is drawn in ASCII
characters, with soft halftone patches of dusty blue, black four-point sparkles and an ASCII
skyline. Type: Dotemp 8bit. Deterministic. Run: python3 assets/make_svgs.py"""
import base64
import math
import random
from pathlib import Path

OUT = Path(__file__).parent
FONTS = OUT / "fonts"
PAPER = "#eeede8"
GRID = "#dcdbd5"
INK = "#111111"
GREY = "#7d7c78"
SOFT = "#a9a8a2"
BLUE = "#9cc3df"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
RAMP = " .,:;-=+*%#@"


def font_face(name, file):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return f"@font-face{{font-family:'{name}';src:url(data:font/ttf;base64,{data}) format('truetype');}}"


def defs():
    return f'''<defs><style>{font_face("dt", "dotemp-8bit.ttf")}</style>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{GRID}" stroke-width=".6"/></pattern>
</defs>'''


class Noise:
    """Small value-noise so clouds look organic."""
    def __init__(self, seed):
        r = random.Random(seed)
        self.g = {(i, j): r.random() for i in range(64) for j in range(64)}

    def _v(self, x, y):
        i, j = int(math.floor(x)) % 64, int(math.floor(y)) % 64
        fx, fy = x - math.floor(x), y - math.floor(y)
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        a, b = self.g[(i, j)], self.g[((i + 1) % 64, j)]
        c, d = self.g[(i, (j + 1) % 64)], self.g[((i + 1) % 64, (j + 1) % 64)]
        top = a + (b - a) * sx
        return top + ((c + (d - c) * sx) - top) * sy

    def __call__(self, x, y):
        return sum(self._v(x * f, y * f) / f for f in (1, 2, 4)) / 1.75


def ascii_sky(seed, w, h, cw=9, ch=13, scale=0.035, mask=None, color=GREY, size=12):
    """The sky as ASCII: denser characters where the cloud field is thicker.
    One <text> per row, widths locked with textLength."""
    n = Noise(seed)
    rows = []
    for r in range(int(h / ch) + 1):
        y = r * ch + ch
        line = []
        for c in range(int(w / cw)):
            x = c * cw
            v = n(x * scale, y * scale * 1.6)
            if mask:
                v *= mask(x, y)
            k = max(0, min(len(RAMP) - 1, int((v - .54) * 3.4 * len(RAMP))))
            line.append(RAMP[k])
        s = "".join(line)
        if s.strip():
            rows.append(f'<text x="0" y="{y}" textLength="{len(line) * cw}" lengthAdjust="spacing" xml:space="preserve">{s}</text>')
    return f'<g font-family="{MONO}" font-size="{size}" fill="{color}">' + "".join(rows) + "</g>"


def halftone(seed, w, h, step=7, scale=0.012, thresh=.5, color=BLUE, mask=None):
    """Soft dusty-blue halftone patches (dot size follows a second noise field)."""
    n = Noise(seed)
    out = []
    for x in range(0, w, step):
        for y in range(0, h, step):
            v = n(x * scale, y * scale)
            if mask:
                v *= mask(x, y)
            if v > thresh:
                r = min(step * .55, (v - thresh) * 14)
                out.append(f'<rect x="{x - r / 2:.1f}" y="{y - r / 2:.1f}" width="{r:.1f}" height="{r:.1f}" fill="{color}"/>')
    return "".join(out)


def sparkle(x, y, R, spin=False, color=INK):
    """A black concave four-point star, like the collage reference."""
    c = R * .12
    d = (f"M {x} {y - R} Q {x + c} {y - c} {x + R} {y} Q {x + c} {y + c} {x} {y + R} "
         f"Q {x - c} {y + c} {x - R} {y} Q {x - c} {y - c} {x} {y - R} Z")
    anim = ""
    if spin:
        anim = (f'<animateTransform attributeName="transform" type="rotate" values="0 {x} {y};12 {x} {y};0 {x} {y}" '
                f'dur="7s" repeatCount="indefinite"/>')
    return f'<path d="{d}" fill="{color}">{anim}</path>'


def ascii_skyline(seed, w, base, cw=9, ch=13, tower_col=None, size=12, cap=None):
    """cap(x) -> max building height (rows) at pixel x, so buildings stay below text."""
    rng = random.Random(seed)
    cols = int(w / cw)
    heights, c = [0] * cols, 0
    while c < cols:
        bw, bh = rng.choice([3, 4, 5, 6, 7]), rng.choice([2, 3, 4, 5, 6, 8])
        for k in range(c, min(cols, c + bw)):
            heights[k] = bh
        c += bw + rng.choice([0, 1, 1, 2])
    if cap:
        heights = [min(h, cap(k * cw)) for k, h in enumerate(heights)]
    lines = []
    for r in range(max(heights) + 1, 0, -1):
        s = []
        for k in range(cols):
            if heights[k] >= r:
                edge = k == 0 or heights[k - 1] < r or k == cols - 1 or heights[k + 1] < r
                s.append("|" if edge else rng.choice(["#", "=", ":", "#", "."]))
            else:
                s.append(" ")
        lines.append(s)
    if tower_col is not None:  # a needle tower with a pod
        for _ in range(9):
            lines.insert(0, [" "] * cols)
        for r in range(len(lines)):
            lines[r][tower_col] = "|"
        for k in range(tower_col - 2, tower_col + 3):
            lines[4][k] = "@"
        lines[3][tower_col - 1:tower_col + 2] = ["(", "o", ")"]
    out = []
    top = base - len(lines) * ch
    for i, s in enumerate(lines):
        txt = "".join(s)
        if txt.strip():
            out.append(f'<text x="0" y="{top + (i + 1) * ch - 3}" textLength="{cols * cw}" lengthAdjust="spacing" xml:space="preserve">{txt}</text>')
    return f'<g font-family="{MONO}" font-size="{size}" fill="{INK}" opacity=".75">' + "".join(out) + "</g>"


def banner():
    W, H = 1200, 440
    clear = lambda x, y: 0.25 if (x < 640 and 70 < y < 370) else 1.0
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="radhika kundnani. designer or developer? yes.">
{defs()}
<rect width="{W}" height="{H}" fill="{PAPER}"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
{halftone(3, W, H, mask=clear)}
{ascii_sky(7, W, H - 70, mask=clear)}
{ascii_skyline(5, W, H, tower_col=112, cap=lambda x: 4 if x < 700 else 99)}
{sparkle(1080, 92, 46, spin=True)}{sparkle(760, 150, 18)}{sparkle(880, 300, 24, spin=True)}{sparkle(680, 60, 9)}
<text x="60" y="92" font-family="{MONO}" font-size="13" letter-spacing="2.5" fill="{GREY}">~/radhika · bangalore</text>
<text x="56" y="200" font-family="dt" font-size="104" fill="{INK}">radhika</text>
<text x="56" y="298" font-family="dt" font-size="104" fill="{INK}">kundnani.</text>
<text x="60" y="350" font-family="dt" font-size="34" fill="{INK}" opacity=".8">designer or developer? yes.</text>
<text x="{W - 32}" y="34" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{GREY}">24.11.2026 · 14:40</text>
</svg>'''
    (OUT / "banner.svg").write_text(svg)


def header(slug, title, index):
    W, H = 1200, 104
    clear = lambda x, y: 0.2 if x < 520 else 1.0
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}">
{defs()}
<rect width="{W}" height="{H}" rx="14" fill="{PAPER}"/>
<rect width="{W}" height="{H}" rx="14" fill="url(#grid)"/>
{halftone(len(slug) * 13, W, H, step=6, thresh=.5, mask=clear)}
{ascii_sky(len(slug) * 7, W, H, scale=.05, mask=clear, color=SOFT, size=11)}
{sparkle(W - 70, 52, 20, spin=True)}
<text x="36" y="68" font-family="dt" font-size="46" fill="{INK}">{title}</text>
<text x="{W - 110}" y="58" text-anchor="end" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{GREY}">{index}</text>
</svg>'''
    (OUT / f"h-{slug}.svg").write_text(svg)


def footer():
    W, H = 1200, 280
    clear = lambda x, y: 0.25 if (250 < x < 950 and 50 < y < 190) else 1.0
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="let's make something.">
{defs()}
<rect width="{W}" height="{H}" rx="14" fill="{PAPER}"/>
<rect width="{W}" height="{H}" rx="14" fill="url(#grid)"/>
{halftone(21, W, H, mask=clear)}
{ascii_sky(17, W, H - 60, mask=clear)}
{ascii_skyline(9, W, H, tower_col=118, cap=lambda x: 6 if 230 < x < 970 else 99)}
{sparkle(150, 80, 30, spin=True)}{sparkle(1040, 70, 16)}
<text x="{W / 2}" y="125" text-anchor="middle" font-family="dt" font-size="68" fill="{INK}">let's make something.</text>
<text x="{W / 2}" y="170" text-anchor="middle" font-family="dt" font-size="26" fill="{INK}" opacity=".75">radhikakundnani1@gmail.com</text>
</svg>'''
    (OUT / "footer.svg").write_text(svg)


banner()
header("built", "things i've made", "01")
header("stack", "my toolbox", "02")
header("signal", "showing up daily", "03")
footer()
print("ok")
