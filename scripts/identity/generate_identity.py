#!/usr/bin/env python3
"""
Generate missing identity assets (png/jpg/ico/favicon/insignia) for Spatial Avy
executable/web client, themed to story novel data (Bodium/Mind/Soul/SATS-REA-REM,
Z-Q-C-T, door nodes N10-N0) and AI-integrated data (Kilo/Ollama runtime).
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets/identity"
ICONS = OUT / "icons"
INSIGNIA = OUT / "insignia"
WEB_ASSETS = ROOT / "build/web/assets"
LOG = ROOT / "logs/identity/generate.log"

PALETTE = {
    "bg": (11, 15, 20),
    "bodium": (196, 204, 214),
    "bodium_glow": (120, 200, 255),
    "mind": (120, 170, 255),
    "soul": (255, 170, 90),
    "ai": (80, 255, 180),
    "accent": (46, 160, 67),
    "fault": (255, 220, 120),
    "grid": (40, 60, 80),
    "text": (230, 237, 243),
}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{now()}] {msg}\n"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())


def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def ensure_dirs():
    for d in [ICONS, INSIGNIA, WEB_ASSETS, WEB_ASSETS / "icons", WEB_ASSETS / "insignia"]:
        d.mkdir(parents=True, exist_ok=True)


def draw_bodium_terrain(draw, w, h):
    # layered mineral strata + fault glow
    for i in range(0, h, 8):
        shade = 18 + (i * 18 // max(h, 1))
        draw.line([(0, i), (w, i)], fill=(shade, shade + 4, shade + 10), width=1)
    # ridges
    cx, cy = w * 0.5, h * 0.62
    for r in range(int(min(w, h) * 0.12), int(min(w, h) * 0.48), int(min(w, h) * 0.06)):
        pts = []
        for a in range(0, 361, 8):
            rad = math.radians(a)
            jitter = (math.sin(a * 0.7) + math.cos(a * 1.3)) * (min(w, h) * 0.012)
            rr = r + jitter
            pts.append((cx + math.cos(rad) * rr, cy + math.sin(rad) * rr * 0.55))
        draw.line(pts, fill=(90, 110, 130), width=2)
    # fault line (Beat 1 disturbance)
    fx0, fy0 = w * 0.18, h * 0.78
    fx1, fy1 = w * 0.82, h * 0.28
    for width, col in [(10, (60, 90, 110)), (4, PALETTE["fault"]), (2, (255, 255, 230))]:
        draw.line([(fx0, fy0), (w * 0.45, h * 0.52), (fx1, fy1)], fill=col, width=width, joint="curve")


def draw_mind_lattice(draw, w, h):
    # mind aspect: geometric lattice
    step = max(18, min(w, h) // 14)
    col = (PALETTE["mind"][0], PALETTE["mind"][1], PALETTE["mind"][2], 90)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(0, w, step):
        od.line([(x, 0), (x, h)], fill=(80, 120, 180, 50), width=1)
    for y in range(0, h, step):
        od.line([(0, y), (w, y)], fill=(80, 120, 180, 50), width=1)
    # causal threads
    nodes = [(w * 0.25, h * 0.3), (w * 0.5, h * 0.22), (w * 0.72, h * 0.34), (w * 0.58, h * 0.5), (w * 0.35, h * 0.48)]
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            od.line([a, b], fill=(120, 170, 255, 70), width=1)
    for n in nodes:
        r = max(3, min(w, h) // 80)
        od.ellipse([n[0]-r, n[1]-r, n[0]+r, n[1]+r], fill=(160, 210, 255, 180))
    return overlay


def draw_soul_core(draw, w, h):
    # soul aspect: warm ember/core
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    cx, cy = w * 0.5, h * 0.5
    for r, a in [(min(w,h)*0.22, 30), (min(w,h)*0.16, 55), (min(w,h)*0.11, 90), (min(w,h)*0.07, 140)]:
        od.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255, 170, 90, a))
    od.ellipse([cx-min(w,h)*0.04, cy-min(w,h)*0.04, cx+min(w,h)*0.04, cy+min(w,h)*0.04], fill=(255, 230, 180, 200))
    return overlay


def draw_ai_ring(draw, w, h):
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    cx, cy = w * 0.5, h * 0.5
    r = min(w, h) * 0.34
    # AI integrated ring / mnemonic ticks
    bbox = [cx-r, cy-r, cx+r, cy+r]
    od.arc(bbox, start=210, end=510, fill=(80, 255, 180, 180), width=max(2, min(w,h)//60))
    # door-node ticks N10-N0 (11 ticks)
    for i in range(11):
        ang = math.radians(210 + i * (300/10))
        x1 = cx + math.cos(ang) * (r - min(w,h)*0.03)
        y1 = cy + math.sin(ang) * (r - min(w,h)*0.03)
        x2 = cx + math.cos(ang) * (r + min(w,h)*0.03)
        y2 = cy + math.sin(ang) * (r + min(w,h)*0.03)
        od.line([(x1,y1),(x2,y2)], fill=(180,255,220,200), width=max(1, min(w,h)//120))
    # Z-Q-C-T micro marks
    for txt, ang in [("Z", 250), ("Q", 310), ("C", 10), ("T", 70)]:
        rad = math.radians(ang)
        tx = cx + math.cos(rad) * (r + min(w,h)*0.07)
        ty = cy + math.sin(rad) * (r + min(w,h)*0.07)
        od.text((tx-4, ty-5), txt, fill=(200, 255, 230, 220))
    return overlay


def compose_emblem(size=1024):
    img = Image.new("RGBA", (size, size), PALETTE["bg"] + (255,))
    d = ImageDraw.Draw(img)
    draw_bodium_terrain(d, size, size)
    img = Image.alpha_composite(img, draw_mind_lattice(d, size, size))
    img = Image.alpha_composite(img, draw_soul_core(d, size, size))
    img = Image.alpha_composite(img, draw_ai_ring(d, size, size))
    # central monogram SA (simple geometry)
    d = ImageDraw.Draw(img)
    cx, cy = size*0.5, size*0.5
    s = size*0.12
    # S-like and A-like strokes
    d.line([(cx-s, cy-s*0.2),(cx-s*0.2, cy-s),(cx+s*0.3, cy-s*0.4),(cx-s*0.3, cy+s*0.4),(cx+s*0.2, cy+s),(cx+s, cy+s*0.2)], fill=(240,248,255,230), width=max(6,size//90), joint="curve")
    d.line([(cx+s*0.15, cy+s),(cx+s*0.55, cy-s),(cx+s*0.95, cy+s)], fill=(240,248,255,230), width=max(6,size//90), joint="curve")
    d.line([(cx+s*0.32, cy+s*0.2),(cx+s*0.78, cy+s*0.2)], fill=(240,248,255,230), width=max(5,size//110))
    return img


def compose_cover(w=1600, h=900):
    img = Image.new("RGBA", (w, h), PALETTE["bg"] + (255,))
    d = ImageDraw.Draw(img)
    draw_bodium_terrain(d, w, h)
    img = Image.alpha_composite(img, draw_mind_lattice(d, w, h))
    # soul ember offset
    soul = draw_soul_core(ImageDraw.Draw(img), w, h)
    img = Image.alpha_composite(img, soul)
    img = Image.alpha_composite(img, draw_ai_ring(ImageDraw.Draw(img), w, h))
    d = ImageDraw.Draw(img)
    # title bars / insignia text-like blocks (no font dependency issues: geometric)
    d.rectangle([60, h-220, 860, h-80], fill=(12,18,26,210), outline=(80,120,160,180), width=2)
    d.text((90, h-200), "SPATIAL AVY", fill=PALETTE["text"])
    d.text((90, h-160), "Bodium / Mind / Soul  |  Z-Q-C-T  |  N10-N0  |  AI-Integrated Runtime", fill=(170,200,230))
    d.text((90, h-125), "Kilo Code + Ollama (llama3.2)  |  Web Client & Player", fill=(140,220,180))
    return img


def export_png_jpg(img_rgba, base_path_no_ext, jpg_quality=92):
    png = base_path_no_ext.with_suffix(".png")
    jpg = base_path_no_ext.with_suffix(".jpg")
    img_rgba.save(png, format="PNG")
    bg = Image.new("RGB", img_rgba.size, PALETTE["bg"])
    bg.paste(img_rgba, mask=img_rgba.split()[-1])
    bg.save(jpg, format="JPEG", quality=jpg_quality, optimize=True)
    return png, jpg


def export_ico(img_rgba, path):
    sizes = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]
    icons = [img_rgba.resize(s, Image.LANCZOS) for s in sizes]
    path.parent.mkdir(parents=True, exist_ok=True)
    icons[0].save(path, format="ICO", sizes=sizes)
    return path


def main():
    ensure_dirs()
    generated = []

    emblem = compose_emblem(1024)
    p_png, p_jpg = export_png_jpg(emblem, ICONS / "spatial_avy_emblem")
    generated += [str(p_png.relative_to(ROOT)), str(p_jpg.relative_to(ROOT))]
    # standard app/web icon sizes
    for sz, name in [(512,"icon-512"),(256,"icon-256"),(192,"icon-192"),(180,"apple-touch-icon"),(128,"icon-128"),(64,"icon-64"),(32,"icon-32"),(16,"icon-16")]:
        im = emblem.resize((sz,sz), Image.LANCZOS)
        pngp = ICONS / f"{name}.png"
        im.save(pngp, format="PNG")
        generated.append(str(pngp.relative_to(ROOT)))
        # copy key ones to web assets
        if name in {"icon-512","icon-192","apple-touch-icon","icon-32","icon-16"}:
            im.save(WEB_ASSETS/"icons"/f"{name}.png", format="PNG")
    # favicon.ico and app ico
    for ico_path in [ICONS/"favicon.ico", ICONS/"spatial_avy.ico", WEB_ASSETS/"favicon.ico", ROOT/"build/web/favicon.ico"]:
        export_ico(emblem, ico_path)
        generated.append(str(ico_path.relative_to(ROOT)))

    cover = compose_cover(1600, 900)
    c_png, c_jpg = export_png_jpg(cover, INSIGNIA / "spatial_avy_identity_cover")
    generated += [str(c_png.relative_to(ROOT)), str(c_jpg.relative_to(ROOT))]
    # additional insignia variants
    for name, size in [("insignia_bodium_mind_soul", (1200,630)), ("insignia_ai_runtime", (1200,630)), ("og_image", (1200,630))]:
        im = compose_cover(size[0], size[1])
        p1,p2 = export_png_jpg(im, INSIGNIA / name)
        generated += [str(p1.relative_to(ROOT)), str(p2.relative_to(ROOT))]
        if name == "og_image":
            im.resize((1200,630), Image.LANCZOS).save(WEB_ASSETS/"insignia"/"og_image.png", format="PNG")
            bg = Image.new("RGB", im.size, PALETTE["bg"]); bg.paste(im, mask=im.split()[-1]); bg.save(WEB_ASSETS/"insignia"/"og_image.jpg", format="JPEG", quality=92)

    # small jpg export for emblem too
    bg = Image.new("RGB", emblem.size, PALETTE["bg"]); bg.paste(emblem, mask=emblem.split()[-1])
    for sz, name in [(512,"icon-512"),(256,"icon-256")]:
        bg.resize((sz,sz), Image.LANCZOS).save(ICONS/f"{name}.jpg", format="JPEG", quality=92)
        generated.append(str((ICONS/f"{name}.jpg").relative_to(ROOT)))

    manifest = {
        "id": "identity_manifest",
        "type": "executable_identity",
        "generated_at": now(),
        "story_novel_data": {
            "world": "spatial_avy_home",
            "motifs": ["Bodium terrain", "Mind aspect", "Soul aspect", "SATS/REA-REM border protocol"],
            "mnemonic_lace": "Z<zone>-Q<pocket>-C<cell>-T<tick>",
            "door_node_string": "N10-N9-N8-N7-N6-N5-N4-N3-N2-N1-N0",
            "timeline_base": "BT-spatial_avy-v1",
            "character": "protagonist (preset_bodium_initiate)"
        },
        "ai_integrated_data": {
            "runtime": "systems/runtime/game_world_runtime.json",
            "local_ai": "llama3.2:latest @ http://localhost:11434",
            "components": ["kilo_code", "ollama", "voice_transcription_vlm_digestion_vocals"]
        },
        "assets": {
            "emblem": "assets/identity/icons/spatial_avy_emblem.png",
            "favicon_ico": "assets/identity/icons/favicon.ico",
            "app_ico": "assets/identity/icons/spatial_avy.ico",
            "cover_png": "assets/identity/insignia/spatial_avy_identity_cover.png",
            "cover_jpg": "assets/identity/insignia/spatial_avy_identity_cover.jpg",
            "og_image": "assets/identity/insignia/og_image.png",
            "web_favicon": "build/web/favicon.ico",
            "web_manifest_icons_dir": "build/web/assets/icons"
        },
        "generated_files": sorted(set(generated))
    }
    save_json(OUT / "identity_manifest.json", manifest)
    save_json(WEB_ASSETS / "identity_manifest.json", manifest)
    log(f"generated {len(set(generated))} identity files")
    print(json.dumps({"generated": len(set(generated)), "manifest": "assets/identity/identity_manifest.json"}, indent=2))


if __name__ == "__main__":
    main()
