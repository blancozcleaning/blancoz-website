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
"OFFICE1":  ("site-photos/02-office-open-plan-bay-views.jpg",
             "office-cleaning-bayside-melbourne-open-plan.jpg",
             "Open plan office in Bayside Melbourne cleaned twice weekly by Blancoz"),
"OFFICE2":  ("site-photos/03-office-architects-studio.jpg",
             "office-cleaning-richmond-melbourne-architecture-studio.jpg",
             "Architecture studio in Richmond Melbourne after a weekly commercial clean"),
"OFFICE4":  ("site-photos/office-south-yarra-developer-boardroom.jpg",
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
"LOGO":     ("assets/logotype.jpg", "blancoz-cleaning-logo.jpg", "Blancoz Cleaning"),
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

split = frag.rindex("</style>") + len("</style>")
head, body = frag[:split], frag[split:]

SITE = "https://blancoz-website.vercel.app"
TITLE = "Commercial Cleaning Melbourne | Blancoz Cleaning | Bayside, CBD &amp; South East"
DESC = ("Commercial and builders cleaning across Melbourne CBD, Bayside and the South Eastern "
        "Suburbs. Family owned since 2008. Labour Hire Authority licensed, police-checked staff, "
        "$20M public liability, and a photo report after every clean. Call 0407 537 976.")

LD = '''{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "@id": "%(site)s/#business",
  "name": "Blancoz Cleaning",
  "description": "Commercial and builders cleaning across Melbourne CBD, Bayside and the South Eastern Suburbs. Family owned and operated since 2008.",
  "url": "%(site)s",
  "telephone": "+61407537976",
  "email": "info@blancoz.cleaning",
  "foundingDate": "2008",
  "image": "%(site)s/img/commercial-cleaning-melbourne-blancoz-team.jpg",
  "logo": "%(site)s/img/blancoz-cleaning-logo.jpg",
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
<meta property="og:image" content="{SITE}/img/commercial-cleaning-melbourne-blancoz-team.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Commercial Cleaning Melbourne | Blancoz Cleaning">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{SITE}/img/commercial-cleaning-melbourne-blancoz-team.jpg">
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
print(f"index.html  {len(doc)/1024:.0f} KB")
print(f"img/        {len(list(IMGDIR.iterdir()))} files, {total/1024/1024:.2f} MB total")
