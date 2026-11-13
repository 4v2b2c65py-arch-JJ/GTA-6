#!/usr/bin/env python3
"""Generate GTA 6 pageout images (hero, characters, locations, editions, gallery/loading assets)."""
import json, math, os, shutil, random
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets/images/in_game/gta6"
WEB = ROOT / "build/web/gta6/assets"

def ensure(p): p.mkdir(parents=True, exist_ok=True)

def grad(size, c1, c2, vertical=True):
    img = Image.new("RGB", size, c1)
    d = ImageDraw.Draw(img)
    w,h = size
    for i in range(h if vertical else w):
        t = i/max(1,(h-1 if vertical else w-1))
        c = tuple(int(c1[j]+(c2[j]-c1[j])*t) for j in range(3))
        if vertical: d.line([(0,i),(w,i)], fill=c)
        else: d.line([(i,0),(i,h)], fill=c)
    return img

def add_noise(img, amt=12):
    px = img.load(); w,h = img.size
    for y in range(0,h,2):
        for x in range(0,w,2):
            p = px[x,y]
            r,g,b = p[:3]
            n = random.randint(-amt,amt)
            nv = (max(0,min(255,r+n)), max(0,min(255,g+n)), max(0,min(255,b+n)))
            px[x,y] = nv + p[3:] if len(p)==4 else nv
    return img

def font(size, bold=False):
    for p in [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def glow_text(img, xy, text, fnt, fill, glow=(255,0,128), radius=8):
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.text(xy, text, font=fnt, fill=glow+(180,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius))
    img.alpha_composite(layer)
    d = ImageDraw.Draw(img); d.text(xy, text, font=fnt, fill=fill)

def tw(draw,text,fnt):
    try: b=draw.textbbox((0,0),text,font=fnt); return b[2]-b[0]
    except:
        try: return draw.textlength(text,font=fnt)
        except: return len(text)*fnt.size*0.6

def wrap(draw,text,fnt,maxw):
    words=text.split(); lines=[]; cur=""
    for wd in words:
        t=(cur+" "+wd).strip()
        if tw(draw,t,fnt)>maxw and cur:
            lines.append(cur); cur=wd
        else: cur=t
    if cur: lines.append(cur)
    return lines

def shutil_copy(src,dst):
    ensure(dst.parent); shutil.copy2(src,dst)
def save_png(img, path):
    ensure(path.parent); img.save(path,"PNG")
def save_jpg(img, path):
    ensure(path.parent); img.convert("RGB").save(path,"JPEG",quality=92)

def hero():
    w,h=1920,1080
    img = grad((w,h),(8,10,30),(40,5,40)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for r,a in [(260,30),(200,55),(150,90),(100,140),(60,200)]:
        d.ellipse([w*0.72-r,h*0.34-r,w*0.72+r,h*0.34+r], fill=(255,120,60,a))
    for i,x in enumerate(range(0,w,36)):
        bh = 120 + (i*37 % 280)
        col = (18+i%25, 14, 34+i%20)
        d.rectangle([x,h-bh,x+26,h], fill=col)
        for wy in range(h-bh+10,h-10,20):
            if (i+wy)%5==0: d.rectangle([x+4,wy,x+9,wy+7], fill=(255,80,160,170))
            if (i+wy)%7==0: d.rectangle([x+13,wy,x+18,wy+7], fill=(80,220,255,150))
    for yy in range(h-280,h-268): d.line([(0,yy),(w,yy)], fill=(255,0,140,180))
    img = add_noise(img.convert("RGB"),7).convert("RGBA")
    d = ImageDraw.Draw(img)
    glow_text(img,(100,360),"GRAND THEFT AUTO",font(78,True),(255,255,255),(0,240,255),12)
    glow_text(img,(100,450),"VI",font(240,True),(255,255,255),(255,0,140),18)
    d.text((110,700),"STATE OF LEONIDA · VICE CITY", font=font(44,True), fill=(255,220,240))
    d.text((110,760),"Jason Duval & Lucia Caminos — November 19, 2026", font=font(30), fill=(180,220,255))
    d.rectangle([110,815,520,885], outline=(255,0,140), width=4)
    d.text((145,835),"PRE-ORDER NOW", font=font(28,True), fill=(255,255,255))
    d.text((110,920),"PS5 · PS5 Pro · Xbox Series X|S  |  PC: Not Announced", font=font(24), fill=(170,190,220))
    save_png(img, OUT/"artwork"/"gta6_hero.png"); save_jpg(img, OUT/"artwork"/"gta6_hero.jpg")
    shutil_copy(OUT/"artwork"/"gta6_hero.png", WEB/"hero.png")

def loading_screen():
    w,h=1920,1080
    img = grad((w,h),(5,4,18),(25,5,35)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # sun glow
    for r,a in [(320,25),(240,45),(170,70),(110,110)]:
        d.ellipse([w//2-r,h*0.42-r,w//2+r,h*0.42+r], fill=(255,90,140,a))
    # palm silhouettes
    for base_x in [220,350,1550,1680]:
        for i in range(6):
            ang = -0.8 + i*0.32
            x2 = base_x + int(math.cos(ang)*180)
            y2 = h - 120 + int(math.sin(ang)*120) - 180
            d.line([(base_x,h-120),(x2,y2)], fill=(10,8,20), width=8)
        d.line([(base_x,h-40),(base_x,h-260)], fill=(10,8,20), width=14)
    # horizon
    for yy in range(h-220,h-200): d.line([(0,yy),(w,yy)], fill=(255,0,140,200))
    img = add_noise(img.convert("RGB"),6).convert("RGBA")
    d = ImageDraw.Draw(img)
    # logo
    glow_text(img,(w//2-420,260),"GRAND THEFT AUTO",font(72,True),(255,255,255),(0,240,255),10)
    glow_text(img,(w//2-140,360),"VI",font(260,True),(255,255,255),(255,0,140),20)
    d.text((w//2-170,640),"LOADING LEONIDA...", font=font(34,True), fill=(220,230,255))
    # progress bar
    bx,by,bw,bh = w//2-420,700,840,18
    d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=9, outline=(255,0,140), width=2)
    d.rounded_rectangle([bx+4,by+4,bx+int(bw*0.72),by+bh-4], radius=6, fill=(255,0,140))
    d.text((w//2-210,740),"Jason & Lucia  |  Vice City  |  Coming November 19, 2026", font=font(22), fill=(180,200,230))
    d.text((w//2-260,790),"PlayStation 5  ·  PlayStation 5 Pro  ·  Xbox Series X|S", font=font(22), fill=(140,170,210))
    d.text((w//2-90,840),"PC: Not Announced", font=font(20), fill=(120,140,170))
    save_png(img, OUT/"ui"/"loading_screen.png"); save_jpg(img, OUT/"ui"/"loading_screen.jpg")
    shutil_copy(OUT/"ui"/"loading_screen.png", WEB/"loading_screen.png")

chars = [
    ("jason_lucia","Jason & Lucia","Protagonists","A criminal conspiracy across the state of Leonida forces them to rely on each other more than ever if they want to make it out alive.",[(20,20,50),(120,20,60)],(255,180,200)),
    ("jason","Jason Duval","Protagonist","Wants an easy life, but things just keep getting harder. Grew up around grifters and crooks; met Lucia — best or worst thing to happen to him.",[(10,25,45),(40,60,120)],(120,210,255)),
    ("lucia","Lucia Caminos","Protagonist","Fresh out of Leonida Penitentiary and ready to change the odds in her favor, committed to her plan — no matter what it takes.",[(30,10,30),(90,20,50)],(255,160,220)),
    ("cal","Cal Hampton","Jason's Friend / Associate","At the low tide of America and happy there. Snooping on Coast Guard comms with a few beers and private browser tabs open.",[(15,30,25),(30,70,50)],(120,255,180)),
    ("boobie","Boobie Ike","Vice City Legend","Transformed time in the streets into a legitimate empire: real estate, a strip club, and a recording studio — all smiles until business.",[(40,25,10),(120,70,20)],(255,210,80)),
    ("drequan","Dre'Quan Priest","Only Raw Records","Always more of a hustler than a gangster. Even while dealing, breaking into music was the goal; partnered with Boobie for a hit.",[(20,10,40),(70,20,100)],(200,160,255)),
    ("realdimez","Real Dimez","Bae-Luxe & Roxy","Friends since high school — turned time shaking down local dealers into cash via spicy rap tracks and relentless social media presence.",[(40,10,35),(120,30,80)],(255,120,200)),
    ("raul","Raul Bautista","Seasoned Bank Robber","Confidence, charm, and cunning — always on the hunt for talent ready to take the risks that bring the biggest rewards.",[(35,20,15),(90,50,30)],(255,180,120)),
    ("brian","Brian Heder","Classic Drug Runner","From the golden age of smuggling in the Keys. Still moving product through his boat yard with his third wife, Lori.",[(15,25,30),(40,60,70)],(170,230,255)),
]

def make_char(cid,name,role,desc,cols,accent):
    w,h=900,1200
    img = grad((w,h),cols[0],cols[1]).convert("RGBA")
    d = ImageDraw.Draw(img)
    cx = w//2
    d.ellipse([cx-190,170,cx+190,550], fill=(0,0,0,90))
    d.polygon([(cx-160,500),(cx+160,500),(cx+220,980),(cx-220,980)], fill=(0,0,0,70))
    for i in range(6):
        y=70+i*200; d.line([(50,y),(w-50,y)], fill=accent+(35,), width=2)
    d.rectangle([0,0,w-1,h-1], outline=accent, width=6)
    d.rectangle([36,h-370,w-36,h-36], fill=(0,0,0,160))
    glow_text(img,(66,h-340),name,font(52,True),(255,255,255),accent,8)
    d.text((68,h-270),role.upper(), font=font(24,True), fill=accent)
    lines=wrap(d,desc,font(23),w-140)
    yy=h-225
    for ln in lines[:4]:
        d.text((68,yy),ln,font=font(23),fill=(230,235,245)); yy+=32
    img = add_noise(img.convert("RGB"),6).convert("RGBA")
    save_png(img, OUT/"characters"/f"{cid}.png"); save_jpg(img, OUT/"characters"/f"{cid}.jpg")
    shutil_copy(OUT/"characters"/f"{cid}.png", WEB/"characters"/f"{cid}.png")

locs = [
    ("vice_city","Vice City","The sun and fun capital of America. Glamour, hustle, and greed in one city — from pastel Art Deco hotels to the barrios, Little Cuba, Tisha-Wocka flea market and VC Port.",[(10,10,40),(80,0,80)],(255,0,140)),
    ("leonida_keys","Leonida Keys","Life in this tropical archipelago isn't flashy but it's easy — gateway to paradise with some of the most beautiful and dangerous waters in America.",[(0,30,50),(0,90,110)],(0,220,255)),
    ("grassrivers","Grassrivers","The untamable jewel of Leonida's crown. Alligators outnumber people, but deadly predators are not the only discovery among the mangroves.",[(10,35,15),(30,80,30)],(120,255,120)),
    ("port_gellhorn","Port Gellhorn","Cheap motels, shuttered attractions, and empty strip malls on Leonida's forgotten coast — a different economy fueled by malt liquor, painkillers and truck stop energy drinks.",[(40,25,15),(90,60,30)],(255,170,80)),
    ("ambrosia","Ambrosia","In the heart of Leonida, American industry and old school values still reign. The Allied Crystal sugar refinery keeps the lights on in this company town.",[(30,20,20),(70,45,35)],(255,200,120)),
    ("mount_kalaga","Mount Kalaga","A national landmark offering prime hunting, fishing, and off-road trails. Hillbilly mystics and paranoid radicals in the surrounding backwoods live far from prying eyes.",[(15,20,35),(40,50,80)],(180,200,255)),
]

def make_loc(cid,name,desc,cols,accent):
    w,h=1200,700
    img = grad((w,h),cols[0],cols[1]).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([20,20,w-20,h-20], outline=(240,230,210), width=4)
    d.rectangle([30,30,w-30,h-30], outline=accent, width=2)
    for i in range(7): d.rectangle([40,350+i*42, w-40, 385+i*42], fill=(accent[0],accent[1],accent[2],25+i*12))
    d.ellipse([w-280,50,w-90,240], fill=accent+(110,))
    glow_text(img,(60,370),name,font(66,True),(255,255,255),accent,10)
    d.text((64,455),"LEONIDA", font=font(28,True), fill=accent)
    lines=wrap(d,desc,font(24),w-130)
    yy=505
    for ln in lines[:4]:
        d.text((64,yy),ln,font=font(24),fill=(240,240,235)); yy+=34
    img = add_noise(img.convert("RGB"),7).convert("RGBA")
    save_png(img, OUT/"locations"/f"{cid}.png"); save_jpg(img, OUT/"locations"/f"{cid}.jpg")
    shutil_copy(OUT/"locations"/f"{cid}.png", WEB/"locations"/f"{cid}.png")

def make_editions():
    items_map = {
        "standard": ["Base game: Jason & Lucia story across the State of Leonida & Vice City","Full single-player experience (1 player, offline play)","Pre-order bonus: Vintage Vice City Pack (all pre-orders before Nov 20, 2026)","Digital pre-order: 1 free month of GTA+","PS5 features: DualSense haptics/adaptive triggers, Tempest 3D audio, fast SSD loading, PS5 Pro Enhanced"],
        "ultimate": ["'95 Grotti Cheetah; Shitzu Squalo; '67 Vapid Dominator Buggy & Paradise Garage","Jason's safehouse vehicles: Dinka Enduro motorcycle & Crest Kayak","Hawk & Little Morgan revolvers (Vercetti Estate stylings)","Personalized weapon variants: Jason's Girardi ES9 & Lucia's Klose K17","Vice City Style & Goodtime Gear (outfits, hairstyles, tattoos)","Ganado Retro Build & Classic Car Collection commissions","Rideout Customs, Sara's Unisex Salon, Stock 305, Electric Fang Tattoo, One-Eyed Willie's"],
        "vintage_vc": ["'55 Vapid Stanier sedan (classic retro ride)","Exclusive vintage looks & hairstyles for Jason and Lucia","Vintage weapon pattern","Retro Vice City vibes across Leonida","Included with all pre-orders/purchases before Nov 20, 2026"],
    }
    for cid,name,price,cols,accent in [
        ("ultimate","Ultimate Edition","$99.99",[(30,20,10),(90,60,20)],(255,200,60)),
        ("standard","Standard Edition","$79.99",[(15,20,35),(30,45,80)],(120,180,255)),
        ("vintage_vc","Vintage Vice City Pack","Pre-order Bonus",[(40,10,30),(100,20,70)],(255,100,180)),
    ]:
        w,h=1200,760
        img=grad((w,h),cols[0],cols[1]).convert("RGBA")
        d=ImageDraw.Draw(img)
        d.rectangle([30,30,w-30,h-30], outline=accent, width=4)
        glow_text(img,(60,55),name,font(58,True),(255,255,255),accent,8)
        d.text((64,140),price,font=font(42,True),fill=accent)
        y=210
        for it in items_map[cid]:
            lines=wrap(d,f"• {it}",font(22),w-140)
            for ln in lines:
                d.text((80,y),ln,font=font(22),fill=(235,240,245)); y+=32
            y+=6
        img = add_noise(img.convert("RGB"),6).convert("RGBA")
        save_png(img, OUT/"editions"/f"{cid}.png"); save_jpg(img, OUT/"editions"/f"{cid}.jpg")
        shutil_copy(OUT/"editions"/f"{cid}.png", WEB/"editions"/f"{cid}.png")

def gallery_shots():
    shots = [
        ("s01_vice_skyline","Vice City Skyline","Neon skyline and ocean drive at sunset",[(10,10,50),(90,0,70)],(255,0,140)),
        ("s02_keys_water","Leonida Keys Waters","Tropical waters and islands of the Keys",[(0,30,60),(0,100,130)],(0,220,255)),
        ("s03_grassrivers","Grassrivers Mangroves","Untamable wetlands and wildlife",[(10,40,15),(30,90,35)],(120,255,120)),
        ("s04_port_gellhorn","Port Gellhorn Strip","Forgotten coast motels and strip malls",[(45,30,15),(100,65,35)],(255,170,80)),
        ("s05_ambrosia","Ambrosia Refinery","Allied Crystal sugar refinery lights",[(35,25,20),(80,55,40)],(255,200,120)),
        ("s06_mount_kalaga","Mount Kalaga Trails","Northern wilderness and off-road trails",[(15,20,40),(45,55,90)],(180,200,255)),
        ("s07_jason_lucia","Jason & Lucia","Partners against the odds in Leonida",[(25,15,45),(110,20,70)],(255,160,220)),
        ("s08_heist","The Score","An easy score goes wrong",[(30,15,20),(90,30,40)],(255,220,120)),
    ]
    for cid,title,sub,cols,accent in shots:
        w,h=1280,720
        img=grad((w,h),cols[0],cols[1]).convert("RGBA")
        d=ImageDraw.Draw(img)
        for i in range(8): d.line([(0,120+i*70),(w,80+i*70)], fill=accent+(30,), width=2)
        d.rectangle([0,h-140,w,h], fill=(0,0,0,140))
        glow_text(img,(40,h-120),title,font(44,True),(255,255,255),accent,8)
        d.text((42,h-65),sub,font=font(24),fill=(210,220,235))
        d.text((42,30),"GTA VI · Leonida",font=font(22,True),fill=accent)
        img=add_noise(img.convert("RGB"),6).convert("RGBA")
        save_png(img, OUT/"screenshots"/f"{cid}.png"); save_jpg(img, OUT/"screenshots"/f"{cid}.jpg")
        shutil_copy(OUT/"screenshots"/f"{cid}.png", WEB/"screenshots"/f"{cid}.png")

def main():
    for sub in ["characters","locations","artwork","editions","screenshots","ui"]:
        ensure(OUT/sub)
    for sub in ["characters","locations","editions","screenshots"]:
        ensure(WEB/sub)
    ensure(WEB)
    hero(); loading_screen()
    for c in chars: make_char(*c)
    for l in locs: make_loc(*l)
    make_editions(); gallery_shots()
    for s,d in [(OUT/"artwork"/"gta6_keyart.jpg", WEB/"keyart.jpg"), (ROOT/"assets/images/icons/games/gta6/gta6_logo.png", WEB/"logo.png")]:
        if s.exists(): shutil_copy(s,d)
    manifest={"id":"gta6_images_manifest","generated_at":datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "hero":"assets/images/in_game/gta6/artwork/gta6_hero.png",
              "loading":"assets/images/in_game/gta6/ui/loading_screen.png",
              "characters":[f"assets/images/in_game/gta6/characters/{c[0]}.png" for c in chars],
              "locations":[f"assets/images/in_game/gta6/locations/{l[0]}.png" for l in locs],
              "editions":[f"assets/images/in_game/gta6/editions/{e}.png" for e in ["ultimate","standard","vintage_vc"]],
              "screenshots":[f"assets/images/in_game/gta6/screenshots/s0{i}_{n}.png" for i,n in enumerate(["vice_skyline","keys_water","grassrivers","port_gellhorn","ambrosia","mount_kalaga","jason_lucia","heist"],1)]}
    with open(OUT/"manifest.json","w") as f: json.dump(manifest,f,indent=2)
    with open(WEB/"manifest.json","w") as f: json.dump(manifest,f,indent=2)
    print(json.dumps({"ok":True,"counts":{"characters":len(chars),"locations":len(locs),"editions":3,"screenshots":8}},indent=2))

if __name__=="__main__": main()
