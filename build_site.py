#!/usr/bin/env python3
"""Build index.html from blancoz-site-template.html.

Photographs are copied to img/ as REAL FILES with descriptive, search-friendly
names, not inlined as base64. Base64 data URIs cannot be indexed by Google
Images at all, and inlining 15 photos was what made the page 3.6MB.

Run: python3 build_site.py
"""
import pathlib, re, shutil, struct, sys

SRC = pathlib.Path("/root/.augmented/monica/project")
HERE = pathlib.Path(__file__).parent
IMGDIR = HERE / "img"

# key -> (source file, published filename, alt text)
IMAGES = {
"HERO":     ("site-photos/01-HERO-crew-scrubbing-studio-floor.jpg",
             "commercial-cleaning-melbourne-blancoz-team.jpg",
             "Blancoz cleaners scrubbing a studio floor during an out-of-hours commercial clean in Melbourne"),
"CREW2":    ("site-photos/cleaner-detail-cleaning-joinery-melbourne.jpg",
             "cleaner-detail-cleaning-joinery-melbourne.jpg",
             "Blancoz cleaner detail cleaning the top of joinery during a Melbourne commercial clean"),
"OFFICE1":  ("site-photos/02-office-open-plan-bay-views.jpg",
             "office-cleaning-bayside-melbourne-open-plan.jpg",
             "Open plan office in Bayside Melbourne cleaned twice weekly by Blancoz"),
"OFFICE2":  ("site-photos/03-office-architects-studio.jpg",
             "office-cleaning-richmond-melbourne-architecture-studio.jpg",
             "Architecture studio in Richmond Melbourne after a weekly commercial clean"),
# v2, sent 22 Aug: sharper and wider than the original, which was visibly soft.
# It is a 2.3:1 crop going into a 4:3 card, so see .card img object-position.
"OFFICE4":  ("site-photos/office-south-yarra-developer-boardroom-v2.jpg",
             "office-cleaning-south-yarra-melbourne-boardroom.jpg",
             "Property developer's boardroom in South Yarra Melbourne cleaned by Blancoz"),
"OFFICE3":  ("site-photos/04-office-bayside-glass-partitions.jpg",
             "office-cleaning-black-rock-melbourne-glass-partitions.jpg",
             "Media agency office in Black Rock with glass partitions cleaned by Blancoz"),
"PILATES":  ("site-photos/allied-health-pilates-studio-brighton.jpg",
             "allied-health-pilates-studio-cleaning-brighton-melbourne.jpg",
             "Pilates studio in Brighton Melbourne cleaned by Blancoz, reformer beds and mirrors"),
"RETAIL":   ("site-photos/05-retail-eyewear-boutique.jpg",
             "high-end-retail-shop-cleaning-melbourne.jpg",
             "High end retail shop front-of-house cleaned before opening, Melbourne"),
"BKITCHEN": ("site-photos/06-builders-luxury-kitchen.jpg",
             "builders-clean-melbourne-kitchen-handover.jpg",
             "Kitchen in a new residential build after a Blancoz builders clean, ready for handover"),
"BHAND":    ("site-photos/07-builders-empty-room-handover.jpg",
             "builders-clean-melbourne-room-ready-for-handover.jpg",
             "Empty room in a completed Melbourne build, detail cleaned and ready for handover"),
"BDRAWER":  ("site-photos/08-builders-drawer-detail.jpg",
             "builders-clean-melbourne-drawer-detail.jpg",
             "Inside of a cupboard drawer cleaned during a builders detail clean in Melbourne"),
"BROBE1":   ("site-photos/builders-handover-wardrobe-drawers-open.jpg",
             "builders-clean-melbourne-wardrobe-drawers-open.jpg",
             "Built-in wardrobe with every door and drawer opened and cleaned during a Melbourne builders handover clean"),
"BROBE2":   ("site-photos/builders-handover-walk-in-robe.jpg",
             "builders-clean-melbourne-walk-in-robe-joinery.jpg",
             "Walk-in robe joinery cleaned inside every drawer before handover, Melbourne"),
"DEFECT1":  ("site-photos/defect-report-wall-marks-new-build.jpg",
             "builders-defect-report-wall-marks-melbourne.jpg",
             "Defect report photo from a Melbourne new build, unfilled fixing holes circled for the builder to correct before handover"),
"DEFECT2":  ("site-photos/defect-report-skirting-caulking-new-build.jpg",
             "builders-defect-report-skirting-caulking-melbourne.jpg",
             "Defect report photo from a Melbourne new build, unfinished skirting caulking circled for the builder before handover"),
"CKITCHEN": ("site-photos/09-commercial-kitchen.jpg",
             "commercial-kitchen-cleaning-melbourne.jpg",
             "Commercial kitchen cleaned by Blancoz in Melbourne"),
"CHILD1":   ("site-photos/childcare-richmond-01-playroom.jpg",
             "childcare-cleaning-richmond-melbourne-playroom.jpg",
             "Childcare centre playroom in Richmond Melbourne after a nightly Blancoz clean"),
"CHILD2":   ("site-photos/childcare-richmond-02-tables.jpg",
             "childcare-cleaning-richmond-melbourne-activity-room.jpg",
             "Childcare centre activity room in Richmond Melbourne cleaned five days a week"),
"CHILD3":   ("site-photos/childcare-richmond-03-corridor.jpg",
             "childcare-cleaning-richmond-melbourne-interior.jpg",
             "Childcare centre interior in Richmond Melbourne cleaned to Department of Health guidelines"),
"SPORT2":   ("site-photos/community-club-social-room-brighton.jpg",
             "community-club-social-room-cleaning-brighton-melbourne.jpg",
             "Community sporting club social and trophy room in Brighton with a polished floor after a Blancoz clean"),
"SPORT3":   ("site-photos/community-club-social-room-mckinnon.jpg",
             "community-club-social-room-cleaning-mckinnon-melbourne.jpg",
             "Sporting club social room at McKinnon vacuumed and set up after a Blancoz clean"),
"SPORT1":   ("site-photos/sporting-mckinnon-01-clubroom-oval.jpg",
             "sporting-club-cleaning-mckinnon-melbourne-clubroom.jpg",
             "Community sporting clubroom at McKinnon with cleaned windows overlooking the oval"),
# SPORT4 is the East Brighton change room. Juan asked for a cleaner shot, so it
# is not referenced by the template right now. Unused keys are skipped by the
# copy loop below, so leaving it defined costs nothing and keeps the option open.
"SPORT4":   ("site-photos/HOLD-change-room-east-brighton-untidy.jpg",
             "sporting-club-change-room-cleaning-east-brighton-melbourne.jpg",
             "Sporting club change rooms in East Brighton cleaned and reset by Blancoz between games"),
"SPORT5":   ("site-photos/sporting-change-room-clean-benches.jpg",
             "sporting-club-change-room-cleaning-melbourne.jpg",
             "Sporting club change rooms cleaned and reset by Blancoz, benches clear and floor cleaned through"),
"SPORT6":   ("site-photos/sporting-facility-exterior-windows-oval.jpg",
             "sporting-facility-window-cleaning-melbourne-oval.jpg",
             "Sporting facility windows cleaned by Blancoz along the oval boundary in Melbourne"),
# Transparent PNG, not the flat JPEG. The JPEG carries a hard white plate that
# shows as a box against the header, and the CSS blend that used to hide it is
# cancelled out by the header's backdrop-filter. Regenerated by
# make_transparent_logo.py (in this repo) from assets/logotype.jpg via a luminance key.
"LOGO":     ("assets/logotype-transparent.png", "blancoz-cleaning-logo.png", "Blancoz Cleaning"),
"MARK":     ("assets/logo-black-negative.png", "blancoz-cleaning-mark.png", ""),
}

def dims(p: pathlib.Path):
    """Width/height without Pillow. Returns (w,h) or None."""
    b = p.read_bytes()
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", b[16:24]); return w, h
    if b[:2] == b"\xff\xd8":
        i = 2
        while i < len(b) - 9:
            if b[i] != 0xFF: i += 1; continue
            m = b[i+1]
            if m in (0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF):
                h, w = struct.unpack(">HH", b[i+5:i+9]); return w, h
            if m in (0xD8,0xD9) or 0xD0 <= m <= 0xD7: i += 2; continue
            i += 2 + struct.unpack(">H", b[i+2:i+4])[0]
    return None

# ---------------------------------------------------------------------------
# GUARD: never silently overwrite hand edits to index.html
#
# Juan edits index.html directly in the GitHub web editor. This script
# REGENERATES index.html from blancoz-site-template.html, so an unguarded run
# would wipe his work without saying so. After each successful build we record
# a checksum of what we produced. On the next run, if index.html no longer
# matches that checksum, someone has edited it by hand and this script stops.
#
# If you hit this: diff index.html against the last build, port the changes
# into blancoz-site-template.html, then delete .index.build.sha256 and re-run.
# ---------------------------------------------------------------------------
import hashlib

STAMP = HERE / ".index.build.sha256"
_idx = HERE / "index.html"

def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if _idx.exists() and STAMP.exists():
    if _sha(_idx) != STAMP.read_text(encoding="utf-8").strip():
        sys.exit(
            "REFUSING TO BUILD: index.html has been edited by hand since the last build.\n"
            "Rebuilding would destroy those edits.\n\n"
            "Do this instead:\n"
            "  1. git log -p -- index.html   (see what changed)\n"
            "  2. port those changes into blancoz-site-template.html\n"
            "  3. rm .index.build.sha256\n"
            "  4. re-run this script\n"
        )

frag = (HERE / "blancoz-site-template.html").read_text(encoding="utf-8")
used = set(re.findall(r"__IMG_([A-Z0-9]+)__", frag))
unknown = used - set(IMAGES)
if unknown: sys.exit(f"Unknown image keys in template: {sorted(unknown)}")

if IMGDIR.exists(): shutil.rmtree(IMGDIR)
IMGDIR.mkdir()

total = 0
for key, (src, name, alt) in IMAGES.items():
    if key not in used: continue
    s = SRC / src
    if not s.exists(): sys.exit(f"MISSING: {s}")
    d = IMGDIR / name
    shutil.copyfile(s, d)
    total += d.stat().st_size
    wh = dims(d)
    size_attr = f' width="{wh[0]}" height="{wh[1]}"' if wh else ""
    # first image on the page (hero) and the logo must not be lazy
    lazy = "" if key in ("LOGO", "HERO") else ' loading="lazy" decoding="async"'
    frag = frag.replace(f'src="__IMG_{key}__"', f'src="img/{name}"{size_attr}{lazy}')

assert "__IMG_" not in frag, "unsubstituted placeholder remains"

# alt text: replace the placeholder-era alts with the descriptive, local ones
for key, (src, name, alt) in IMAGES.items():
    frag = re.sub(rf'(src="img/{re.escape(name)}"[^>]*?)alt="[^"]*"', rf'\1alt="{alt}"', frag)
    frag = re.sub(rf'alt="[^"]*"([^>]*?src="img/{re.escape(name)}")', rf'alt="{alt}"\1', frag)

# ---------------------------------------------------------------------------
# SOCIAL CARD
#
# The link preview (Facebook, WhatsApp, LinkedIn, iMessage, Google) used to be
# the raw hero JPEG: full colour, where the same photo on the page is greyscale
# and darkened by CSS, and with no branding on it at all. Anyone who saw a
# shared link and then opened the site saw two different images.
#
# This renders the card the page implies. Same filter the hero carries, the
# crop Juan framed, the logotype and a "COMMERCIAL CLEANING" line set in the
# site's own label style.
#
# The crop box below is not eyeballed. Juan sent back a re-cropped mock, and it
# was registered against the source photo by normalised cross-correlation
# (0.998), so these are the exact pixels he framed. The logo geometry was
# measured off that same mock. Do not "tidy" these numbers.
#
# Keep SOCIAL_CONTRAST / SOCIAL_BRIGHTNESS in step with .hero img.bg, and the
# label styling in step with .label, both in the template.
# ---------------------------------------------------------------------------
SOCIAL_NAME = "commercial-cleaning-melbourne-blancoz-social-card.jpg"
# 2:1, the rectangle Juan asked for. Rendered at 2x the source crop so the
# logotype and lettering are genuinely sharp on retina displays; the photo
# itself only holds 780px of real detail, hence the unsharp pass after resize.
SOCIAL_W, SOCIAL_H = 1600, 800
# Matches: filter: grayscale(1) contrast(1.06) brightness(.72)
SOCIAL_CONTRAST, SOCIAL_BRIGHTNESS = 1.06, 0.72
# Registered crop, in source pixels: 780x390 out of 1079x957.
SOCIAL_CROP = (260, 136, 1040, 526)
# Logo placement, as fractions of the card, measured off Juan's mock. Only the
# vertical was changed, lifted from .59 so the second line has room and the
# whole lockup still clears the 1.91:1 area Facebook crops a 2:1 image to.
SOCIAL_LOGO_LEFT, SOCIAL_LOGO_W, SOCIAL_LOGO_TOP = 0.0675, 0.5936, 0.500
SOCIAL_SUB = "COMMERCIAL CLEANING"
FONT_FILE = HERE / "vendor/Archivo.ttf"     # OFL, vendored so builds are reproducible


def build_social_card():
    from PIL import Image, ImageDraw, ImageFont, ImageFilter

    im = (Image.open(SRC / IMAGES["HERO"][0]).convert("RGB")
          .crop(SOCIAL_CROP).resize((SOCIAL_W, SOCIAL_H), Image.LANCZOS))

    # grayscale(1) -> contrast() -> brightness(), in that order, in sRGB, which
    # is the order and the space the browser applies them in.
    lut = [max(0, min(255, round(((v / 255 - .5) * SOCIAL_CONTRAST + .5) * SOCIAL_BRIGHTNESS * 255)))
           for v in range(256)]
    im = im.convert("L").point(lut).convert("RGB")
    # Recover the edge definition the 2x upscale cost. Gentle: enough to look
    # crisp, not enough to ring around the mirror frames.
    im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=85, threshold=3))

    # Fade to black up from the lower half, so white type always has ground.
    ramp = Image.new("L", (1, SOCIAL_H))
    rpx = ramp.load()
    for y in range(SOCIAL_H):
        d = (y - SOCIAL_H * 0.40) / (SOCIAL_H * 0.60)
        rpx[0, y] = int(max(0.0, min(1.0, d)) ** 1.5 * 0.48 * 255)
    im = Image.composite(Image.new("RGB", im.size, (0, 0, 0)),
                         im, ramp.resize(im.size)).convert("RGBA")

    # Logotype: trimmed to its ink (the PNG carries padding), recoloured white,
    # because the only mark we hold is black and black dies on a dark photo.
    lg = Image.open(SRC / IMAGES["LOGO"][0]).convert("RGBA")
    lg = lg.crop(lg.getchannel("A").getbbox())
    lw = int(round(SOCIAL_LOGO_W * SOCIAL_W))
    lg = lg.resize((lw, int(round(lw * lg.height / lg.width))), Image.LANCZOS)
    white = Image.new("RGBA", lg.size, (255, 255, 255, 255))
    white.putalpha(lg.getchannel("A"))
    lx, ly = int(round(SOCIAL_LOGO_LEFT * SOCIAL_W)), int(round(SOCIAL_LOGO_TOP * SOCIAL_H))
    im.alpha_composite(white, (lx, ly))

    # Sub-line, in the site's own .label style: Archivo 600, .15em, uppercase.
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(str(FONT_FILE), round(SOCIAL_W * 0.0258))
    f.set_variation_by_axes([600, 100])                 # weight, width
    track = f.size * 0.15
    y = ly + lg.height + round(SOCIAL_H * 0.050)
    width = sum(d.textlength(c, font=f) for c in SOCIAL_SUB) + track * (len(SOCIAL_SUB) - 1)
    d.line([(lx, y - round(SOCIAL_H * 0.025)), (lx + width, y - round(SOCIAL_H * 0.025))],
           fill=(255, 255, 255, 90), width=max(2, SOCIAL_H // 400))
    x = lx
    for ch in SOCIAL_SUB:                               # PIL has no letter-spacing
        d.text((x, y), ch, font=f, fill=(255, 255, 255, 232))
        x += d.textlength(ch, font=f) + track

    out = IMGDIR / SOCIAL_NAME
    # subsampling=0 keeps the chroma full-resolution, which is what stops JPEG
    # smearing the hard white edges of the logotype and the lettering.
    im.convert("RGB").save(out, "JPEG", quality=94, optimize=True,
                           progressive=True, subsampling=0)
    return out


_social = build_social_card()
print(f"social card  {_social.stat().st_size // 1024} KB  {SOCIAL_W}x{SOCIAL_H}")

split = frag.rindex("</style>") + len("</style>")
head, body = frag[:split], frag[split:]

SITE = "https://blancozcleaning.com"
TITLE = "Commercial Cleaning Melbourne | Blancoz Cleaning | Bayside, CBD &amp; South East"
DESC = ("Commercial and builders cleaning across Melbourne CBD, Bayside and the South Eastern "
        "Suburbs. Family owned since 2009. Labour Hire Authority licensed, police-checked staff, "
        "$20M public liability, and a photo report after every clean. Call 0407 537 976.")

LD = '''{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "@id": "%(site)s/#business",
  "name": "Blancoz Cleaning",
  "description": "Commercial and builders cleaning across Melbourne CBD, Bayside and the South Eastern Suburbs. Family owned and operated since 2009.",
  "url": "%(site)s",
  "telephone": "+61407537976",
  "email": "info@blancoz.cleaning",
  "foundingDate": "2009",
  "image": "%(site)s/img/commercial-cleaning-melbourne-blancoz-team.jpg",
  "logo": "%(site)s/img/blancoz-cleaning-logo.png",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "addressRegion": "VIC",
    "postalCode": "3187",
    "addressCountry": "AU"
  },
  "areaServed": [
    {"@type": "City", "name": "Melbourne"},
    {"@type": "Place", "name": "Melbourne CBD"},
    {"@type": "Place", "name": "Bayside"},
    {"@type": "Place", "name": "Brighton"},
    {"@type": "Place", "name": "Black Rock"},
    {"@type": "Place", "name": "Hampton"},
    {"@type": "Place", "name": "Sandringham"},
    {"@type": "Place", "name": "McKinnon"},
    {"@type": "Place", "name": "Bentleigh"},
    {"@type": "Place", "name": "Carnegie"},
    {"@type": "Place", "name": "Elsternwick"},
    {"@type": "Place", "name": "Elwood"},
    {"@type": "Place", "name": "Windsor"},
    {"@type": "Place", "name": "Richmond"},
    {"@type": "Place", "name": "South Yarra"},
    {"@type": "Place", "name": "Cremorne"},
    {"@type": "Place", "name": "South Melbourne"},
    {"@type": "Place", "name": "Port Melbourne"},
    {"@type": "Place", "name": "South Eastern Suburbs, Melbourne"}
  ],
  "knowsAbout": [
    "Commercial cleaning", "Office cleaning", "Childcare centre cleaning",
    "Medical and allied health cleaning", "Builders cleaning", "Handover cleaning",
    "Sporting and community facility cleaning", "Retail and showroom cleaning",
    "Infectious outbreak cleaning"
  ],
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Cleaning services",
    "itemListElement": [
      {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Commercial cleaning", "description": "Scheduled cleaning for offices, clinics, showrooms, sporting and community facilities and childcare centres, to an agreed scope and checklist."}},
      {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Builders cleaning", "description": "Final detail cleans that get a completed build ready for handover, with a photographed defect list."}},
      {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Express clean", "description": "Site cleaned within 24 hours when something has gone wrong."}},
      {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Childcare cleaning", "description": "Five days a week with Working With Children Checked cleaners, including infectious outbreak cleans to Department of Health guidelines."}}
    ]
  },
  "sameAs": [
    "https://www.facebook.com/blancozcleaning/",
    "https://www.instagram.com/blancozcleaning/"
  ]
}''' % {"site": SITE}

doc = f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{SITE}/">
<meta name="theme-color" content="#0E0F11">
<meta name="geo.region" content="AU-VIC">
<meta name="geo.placename" content="Melbourne, Victoria">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Blancoz Cleaning">
<meta property="og:title" content="Commercial Cleaning Melbourne | Blancoz Cleaning">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}/">
<meta property="og:locale" content="en_AU">
<meta property="og:image" content="{SITE}/img/{SOCIAL_NAME}">
<meta property="og:image:width" content="{SOCIAL_W}">
<meta property="og:image:height" content="{SOCIAL_H}">
<meta property="og:image:alt" content="{IMAGES['HERO'][2]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Commercial Cleaning Melbourne | Blancoz Cleaning">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{SITE}/img/{SOCIAL_NAME}">
<meta name="twitter:image:alt" content="{IMAGES['HERO'][2]}">
<script type="application/ld+json">
{LD}
</script>
{head[head.index('<link rel="preconnect"'):]}
</head>
<body>
{body}
</body>
</html>
"""
out = HERE / "index.html"
out.write_text(doc, encoding="utf-8")
STAMP.write_text(_sha(out), encoding="utf-8")
print(f"index.html  {len(doc)/1024:.0f} KB")
print(f"img/        {len(list(IMGDIR.iterdir()))} files, {total/1024/1024:.2f} MB total")
