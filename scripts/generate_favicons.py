#!/usr/bin/env python3
"""
Generate a full favicon set with a "DF" monogram.

Outputs to images/ matching the filenames already referenced in
_includes/head/custom.html and images/browserconfig.xml:

  favicon.ico (multi-size)
  favicon-16x16.png, favicon-32x32.png, favicon-96x96.png
  apple-touch-icon-{57,60,72,76,114,120,144,152,180}x*.png
  android-chrome-192x192.png
  mstile-{70,144,150,310}x*.png, mstile-310x150.png
  safari-pinned-tab.svg    (monochrome SVG for Safari pinned tabs)

Usage:
    python3 scripts/generate_favicons.py

Tweak the colors / text below if you want a different look.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "images"

# ---- design ------------------------------------------------------------------
TEXT = "DF"
BG_COLOR = (30, 49, 82)      # deep navy blue — feel free to change
FG_COLOR = (255, 255, 255)   # white text
# Favicons with transparent backgrounds look bad on dark browser tabs, so we
# keep a solid background. If you want transparent, set BG_COLOR = None.

# Sizes to generate. Filename template -> size(s)
PNG_TARGETS = {
    "favicon-16x16.png": 16,
    "favicon-32x32.png": 32,
    "favicon-96x96.png": 96,
    "apple-touch-icon-57x57.png": 57,
    "apple-touch-icon-60x60.png": 60,
    "apple-touch-icon-72x72.png": 72,
    "apple-touch-icon-76x76.png": 76,
    "apple-touch-icon-114x114.png": 114,
    "apple-touch-icon-120x120.png": 120,
    "apple-touch-icon-144x144.png": 144,
    "apple-touch-icon-152x152.png": 152,
    "apple-touch-icon-180x180.png": 180,
    "android-chrome-192x192.png": 192,
    "mstile-70x70.png": 70,
    "mstile-144x144.png": 144,
    "mstile-150x150.png": 150,
    "mstile-310x310.png": 310,
}
# Wide Windows tile (non-square)
WIDE_TARGET = ("mstile-310x150.png", 310, 150)

# .ico bundles 16, 32, and 48 px
ICO_SIZES = [16, 32, 48]


def _load_bold_font(size: int) -> ImageFont.FreeTypeFont:
    """Find a bold sans-serif system font at the requested size."""
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                # Some .ttc files need an index; start with 0
                return ImageFont.truetype(path, size, index=0)
            except Exception:
                continue
    # Fallback — PIL's built-in bitmap font (small, not great at large sizes)
    return ImageFont.load_default()


def _render_square(size: int, text: str = TEXT) -> Image.Image:
    img = Image.new("RGBA", (size, size), BG_COLOR + (255,) if BG_COLOR else (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Start at ~60% of the canvas and step down until the text fits with padding
    font_size = max(8, int(size * 0.6))
    padding = max(1, size // 10)
    while font_size > 4:
        font = _load_bold_font(font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        if text_w <= size - 2 * padding and text_h <= size - 2 * padding:
            break
        font_size -= 1

    # Center (textbbox returns offsets relative to the anchor — subtract them)
    x = (size - text_w) / 2 - bbox[0]
    y = (size - text_h) / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=FG_COLOR)
    return img


def _render_wide(width: int, height: int, text: str = TEXT) -> Image.Image:
    img = Image.new("RGBA", (width, height), BG_COLOR + (255,) if BG_COLOR else (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_size = int(height * 0.7)
    padding = max(1, height // 10)
    while font_size > 4:
        font = _load_bold_font(font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        if text_w <= width - 2 * padding and text_h <= height - 2 * padding:
            break
        font_size -= 1

    x = (width - text_w) / 2 - bbox[0]
    y = (height - text_h) / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=FG_COLOR)
    return img


def _write_safari_svg(path: Path) -> None:
    # Safari pinned tabs need a monochrome SVG — the browser applies a color.
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <text x="8" y="12.5" text-anchor="middle"
        font-family="Helvetica, Arial, sans-serif"
        font-weight="bold" font-size="11" fill="black">{TEXT}</text>
</svg>
"""
    path.write_text(svg)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Square PNGs
    for fname, size in PNG_TARGETS.items():
        img = _render_square(size)
        out = OUT_DIR / fname
        img.save(out, format="PNG")
        print(f"wrote {out.relative_to(REPO_ROOT)}  ({size}x{size})")

    # Wide tile
    fname, w, h = WIDE_TARGET
    wide = _render_wide(w, h)
    wide.save(OUT_DIR / fname, format="PNG")
    print(f"wrote images/{fname}  ({w}x{h})")

    # favicon.ico (multi-size)
    ico_images = [_render_square(s) for s in ICO_SIZES]
    ico_images[0].save(
        OUT_DIR / "favicon.ico",
        format="ICO",
        sizes=[(s, s) for s in ICO_SIZES],
    )
    print(f"wrote images/favicon.ico  (bundled {ICO_SIZES})")

    # Safari pinned-tab SVG
    _write_safari_svg(OUT_DIR / "safari-pinned-tab.svg")
    print("wrote images/safari-pinned-tab.svg")

    print("\nDone. Re-commit the images/ folder to publish the new favicons.")


if __name__ == "__main__":
    main()
