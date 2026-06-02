"""
Génère une image de fond professionnelle pour la page d'accueil du dashboard.
- Dégradé clair + formes douces aux couleurs de la marque (bleu / orange)
- Bande d'en-tête bleu nuit -> bleu pour le titre
Sortie : powerbi/assets/landing_background.png (1920x1080)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "powerbi" / "assets" / "landing_background.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
NAVY = (27, 58, 75)       # #1B3A4B
BLUE = (46, 134, 171)     # #2E86AB
ORANGE = (228, 87, 46)    # #E4572E
LIGHT_TOP = (248, 251, 253)
LIGHT_BOT = (228, 238, 246)


def lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


# --- Base : dégradé vertical très clair -------------------------------------
base = Image.new("RGB", (W, H), LIGHT_TOP)
px = base.load()
for y in range(H):
    t = y / H
    col = lerp(LIGHT_TOP, LIGHT_BOT, t)
    for x in range(W):
        px[x, y] = col

# --- Couche de formes douces (glow) -----------------------------------------
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)

def blob(cx, cy, r, color, alpha):
    gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))

# grands cercles bleus translucides (coins)
blob(1750, 230, 520, BLUE, 60)
blob(150, 950, 460, BLUE, 45)
# touche orange discrète
blob(1500, 980, 300, ORANGE, 38)
blob(360, 120, 220, BLUE, 35)
glow = glow.filter(ImageFilter.GaussianBlur(120))
base = Image.alpha_composite(base.convert("RGBA"), glow)

# --- Bande d'en-tête (dégradé navy -> bleu) ---------------------------------
HEADER_H = 230
header = Image.new("RGB", (W, HEADER_H), NAVY)
hpx = header.load()
for x in range(W):
    t = x / W
    col = lerp(NAVY, BLUE, t)
    for y in range(HEADER_H):
        hpx[x, y] = col
base.paste(header, (0, 0))

# fine ligne d'accent orange sous l'en-tête
acc = ImageDraw.Draw(base)
acc.rectangle([0, HEADER_H, W, HEADER_H + 6], fill=ORANGE + (255,))

# --- Filigrane de pieds de page ---------------------------------------------
foot = ImageDraw.Draw(base)
foot.line([(60, H - 70), (W - 60, H - 70)], fill=(BLUE + (90,)), width=2)

base.convert("RGB").save(OUT, "PNG")
print("Image de fond générée :", OUT, f"({OUT.stat().st_size // 1024} Ko, {W}x{H})")
