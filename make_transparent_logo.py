"""
Cut a transparent PNG of the Blancoz wordmark from the flat JPEG.

The source is a black wordmark on a solid white plate, so the correct cut is a
luminance key: white becomes fully transparent, black becomes fully opaque, and
the greys in between become the matching partial alpha. That keeps the
antialiased edges smooth AND opens up the counters inside the letters and the
crescent inside the circular mark, so the page shows through them the way it
should. Colour is normalised to pure black, which is the brand rule anyway and
means a plain invert() is all dark mode needs.
"""
from PIL import Image
import pathlib

# Same photo library build_site.py reads from.
ASSETS = pathlib.Path("/root/.augmented/monica/project/assets")
SRC = ASSETS / "logotype.jpg"
DST = ASSETS / "logotype-transparent.png"

SCALE = 3          # source is only 331x107; header renders it at 64px on 2-3x screens
WHITE = 238        # at/above this luminance -> fully transparent
BLACK = 70         # at/below this luminance -> fully opaque

im = Image.open(SRC).convert("L")
im = im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS)
w, h = im.size

# alpha ramp, built once as a 256-entry lookup table
lut = []
for lum in range(256):
    if lum >= WHITE:
        lut.append(0)
    elif lum <= BLACK:
        lut.append(255)
    else:
        lut.append(int(round(255 * (WHITE - lum) / (WHITE - BLACK))))

alpha = im.point(lut)
out = Image.merge("RGBA", (
    Image.new("L", (w, h), 0),
    Image.new("L", (w, h), 0),
    Image.new("L", (w, h), 0),
    alpha,
))
out.save(DST, optimize=True)

hist = alpha.histogram()
print(f"{DST.name}: {w}x{h}")
print(f"  fully transparent: {hist[0]*100//(w*h)}%   fully opaque: {hist[255]*100//(w*h)}%")
print(f"  partial (antialiased edge): {sum(hist[1:255])} px")
