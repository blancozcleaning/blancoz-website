#!/usr/bin/env python3
"""Build index.html from blancoz-site-template.html.

Inlines every photograph as a base64 data URI so the published page has no
external dependencies except Google Fonts, then wraps the fragment in a proper
HTML document. Run: python3 build_site.py
"""
import base64, pathlib, re, sys

P = pathlib.Path("/root/.augmented/monica/project")
HERE = pathlib.Path(__file__).parent

def b64(rel):
    p = P / rel
    if not p.exists():
        sys.exit(f"MISSING IMAGE: {p}")
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()

IMG = {
    "HERO":     "site-photos/01-HERO-crew-scrubbing-studio-floor.jpg",
    "OFFICE1":  "site-photos/02-office-open-plan-bay-views.jpg",
    "OFFICE2":  "site-photos/03-office-architects-studio.jpg",
    "OFFICE3":  "site-photos/04-office-bayside-glass-partitions.jpg",
    "RETAIL":   "site-photos/05-retail-eyewear-boutique.jpg",
    "BKITCHEN": "site-photos/06-builders-luxury-kitchen.jpg",
    "BHAND":    "site-photos/07-builders-empty-room-handover.jpg",
    "BDRAWER":  "site-photos/08-builders-drawer-detail.jpg",
    "CKITCHEN": "site-photos/09-commercial-kitchen.jpg",
    "CHILD1":   "site-photos/childcare-richmond-01-playroom.jpg",
    "CHILD2":   "site-photos/childcare-richmond-02-tables.jpg",
    "CHILD3":   "site-photos/childcare-richmond-03-corridor.jpg",
    "SPORT1":   "site-photos/sporting-mckinnon-01-clubroom-oval.jpg",
    "LOGO":     "assets/logotype.jpg",
    "MARK":     "assets/logo-black-negative.png",
}

frag = (HERE / "blancoz-site-template.html").read_text(encoding="utf-8")

used = set(re.findall(r"__IMG_([A-Z0-9]+)__", frag))
unknown = used - set(IMG)
if unknown:
    sys.exit(f"Template references unknown images: {sorted(unknown)}")
unused = set(IMG) - used
if unused:
    print(f"note: defined but unused: {sorted(unused)}")

for key, rel in IMG.items():
    frag = frag.replace(f"__IMG_{key}__", b64(rel))

assert "__IMG_" not in frag, "unsubstituted placeholder remains"

split = frag.rindex("</style>") + len("</style>")
head, body = frag[:split], frag[split:]

doc = f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Blancoz Cleaning - commercial cleaning across Melbourne. Family owned since 2008. Labour Hire Authority licensed, police-checked staff, $20M public liability.">
<meta name="theme-color" content="#0E0F11">
{head}
</head>
<body>
{body}
</body>
</html>
"""
out = HERE / "index.html"
out.write_text(doc, encoding="utf-8")
print(f"built {out} -> {len(doc)/1024/1024:.2f} MB, {len(used)} images inlined")
