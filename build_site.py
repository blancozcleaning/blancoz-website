import base64, os, pathlib

P = "/root/.augmented/monica/project"
def b64(path):
    ext = pathlib.Path(path).suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()

IMG = {
    "hero":     b64(f"{P}/site-photos/01-HERO-crew-scrubbing-studio-floor.jpg"),
    "office1":  b64(f"{P}/site-photos/02-office-open-plan-bay-views.jpg"),
    "office2":  b64(f"{P}/site-photos/03-office-architects-studio.jpg"),
    "office3":  b64(f"{P}/site-photos/04-office-bayside-glass-partitions.jpg"),
    "retail":   b64(f"{P}/site-photos/05-retail-eyewear-boutique.jpg"),
    "bkitchen": b64(f"{P}/site-photos/06-builders-luxury-kitchen.jpg"),
    "bhand":    b64(f"{P}/site-photos/07-builders-empty-room-handover.jpg"),
    "bdrawer":  b64(f"{P}/site-photos/08-builders-drawer-detail.jpg"),
    "ckitchen": b64(f"{P}/site-photos/09-commercial-kitchen.jpg"),
    "logo":     b64(f"{P}/assets/logotype.jpg"),
    "mark":     b64(f"{P}/assets/logo-black-negative.png"),
}
for k, v in IMG.items():
    print(k, len(v)//1024, "KB")
with open("/root/.augmented/monica/scratch/images.py", "w") as f:
    f.write("IMG = " + repr(IMG))
