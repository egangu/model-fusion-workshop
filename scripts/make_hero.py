from math import cos, sin, pi
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw, ImageFilter


OUT = Path(__file__).resolve().parents[1] / "assets" / "hero-fusion.png"
W, H = 1800, 760
rng = Random(42)


def lerp(a, b, t):
    return int(a + (b - a) * t)


def blend(c1, c2, t):
    return tuple(lerp(c1[i], c2[i], t) for i in range(3))


img = Image.new("RGB", (W, H), "#102028")
px = img.load()

top = (21, 95, 101)
mid = (33, 125, 111)
bottom = (238, 101, 84)
for y in range(H):
    ty = y / (H - 1)
    base = blend(top, mid, min(1, ty * 1.4)) if ty < 0.72 else blend(mid, bottom, (ty - 0.72) / 0.28)
    for x in range(W):
        tx = x / (W - 1)
        glow = int(28 * (1 - abs(tx - 0.38) * 1.7) * (1 - abs(ty - 0.42) * 1.4))
        px[x, y] = tuple(max(0, min(255, c + glow)) for c in base)

draw = ImageDraw.Draw(img, "RGBA")

# Soft field curves, suggesting fused model manifolds.
for i in range(26):
    y0 = rng.randint(60, H - 80)
    amp = rng.randint(14, 78)
    period = rng.uniform(0.7, 1.65)
    phase = rng.uniform(0, 2 * pi)
    color = rng.choice([(255, 255, 255, 34), (164, 255, 226, 42), (255, 187, 132, 38)])
    pts = []
    for x in range(-40, W + 41, 18):
        yy = y0 + amp * sin((x / W) * 2 * pi * period + phase)
        yy += 16 * sin((x / W) * 2 * pi * 2.4 + phase / 2)
        pts.append((x, yy))
    draw.line(pts, fill=color, width=rng.choice([2, 2, 3]))

# Model checkpoints as connected nodes, merging toward a shared fused model.
clusters = [
    ((360, 300), 155, (180, 255, 226, 150)),
    ((760, 245), 145, (255, 215, 138, 140)),
    ((650, 515), 160, (116, 217, 255, 130)),
    ((1130, 365), 180, (255, 142, 126, 145)),
]

nodes = []
for center, radius, color in clusters:
    cx, cy = center
    local = []
    for j in range(10):
        a = 2 * pi * j / 10 + rng.uniform(-0.18, 0.18)
        r = radius * rng.uniform(0.28, 0.96)
        p = (cx + r * cos(a), cy + r * sin(a))
        local.append(p)
        nodes.append((p, color))
    for a in local:
        nearest = sorted(local, key=lambda b: (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)[1:4]
        for b in nearest:
            draw.line([a, b], fill=color[:3] + (42,), width=2)

fused = (1360, 355)
for p, color in nodes:
    if rng.random() < 0.38:
        draw.line([p, fused], fill=(255, 244, 210, 48), width=2)

for p, color in nodes:
    x, y = p
    draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=color[:3] + (180,))
    draw.ellipse((x - 15, y - 15, x + 15, y + 15), outline=color[:3] + (45,), width=2)

fx, fy = fused
for r, alpha in [(92, 38), (58, 72), (28, 210)]:
    draw.ellipse((fx - r, fy - r, fx + r, fy + r), outline=(255, 245, 208, alpha), width=4)
draw.ellipse((fx - 18, fy - 18, fx + 18, fy + 18), fill=(255, 239, 178, 230))

# Add a dark overlay on the left so header text remains legible.
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay, "RGBA")
for x in range(W):
    alpha = int(max(0, 118 * (1 - x / 950)))
    od.line([(x, 0), (x, H)], fill=(9, 18, 24, alpha))
img = Image.alpha_composite(img.convert("RGBA"), overlay)

img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=115, threshold=2))
OUT.parent.mkdir(parents=True, exist_ok=True)
img.convert("RGB").save(OUT, quality=92, optimize=True)
print(OUT)
