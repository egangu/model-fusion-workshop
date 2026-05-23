from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PEOPLE = ROOT / "assets" / "people"

for src in list(PEOPLE.glob("*.png")) + list(PEOPLE.glob("*.jpg")):
    if src.stem.endswith("-thumb"):
        continue
    img = Image.open(src).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    if src.stem == "hongxia-yang":
        top = max(0, int((h - side) * 0.18))
    crop = img.crop((left, top, left + side, top + side))
    crop = crop.resize((420, 420), Image.Resampling.LANCZOS)
    out = PEOPLE / f"{src.stem}-thumb.jpg"
    crop.save(out, quality=86, optimize=True)
    print(out)
