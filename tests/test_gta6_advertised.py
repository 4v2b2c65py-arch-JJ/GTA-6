#!/usr/bin/env python3
"""
Test suite against advertised GTA 6 features/content as represented in the
Spatial Avy web client/player GTA VI pageout and packaged build.

Checks: full loading page, core advertised facts (release, platforms, setting,
protagonists, editions/pricing/bonuses, locations, characters, trailers/media,
preload/storage/PC status), assets/images presence, and package injection.
"""
import json, re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(p):
    return (ROOT / p).read_text(encoding="utf-8", errors="ignore")

def exists(p):
    return (ROOT / p).exists()

def load_json(p):
    with open(ROOT / p, "r", encoding="utf-8") as f:
        return json.load(f)

class TestGTA6Advertised(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = read("build/web/gta6/index.html")
        cls.app = read("build/web/gta6/app.js")
        cls.css = read("build/web/gta6/style.css")
        cls.html_l = cls.html.lower()
        cls.app_l = cls.app.lower()
        cls.all_text = cls.html + "\n" + cls.app

    # --- Loading page ---
    def test_loading_screen_present(self):
        for token in ['id="loading-screen"', 'loading-bar', 'loading-fill', 'ENTER LEONIDA', 'LOADING', 'progress', 'Jason & Lucia']:
            self.assertIn(token, self.html if token[0] in '<J' else self.html, msg=f"loading token missing: {token}")
        self.assertIn('loading_screen.png', self.html + self.app)

    def test_loading_assets(self):
        self.assertTrue(exists("build/web/gta6/assets/loading_screen.png"))
        self.assertTrue(exists("build/web/gta6/assets/hero.png"))

    # --- Core advertised facts ---
    def test_release_date(self):
        self.assertIn('November 19, 2026', self.all_text)

    def test_platforms(self):
        for p in ['PlayStation 5', 'Xbox Series X|S', 'PS5 Pro', 'Xbox Cloud Gaming']:
            self.assertIn(p, self.all_text)
        self.assertRegex(self.all_text, r'PC.*Not announced|Not Announced', msg="PC not-announced status missing")

    def test_setting_and_protagonists(self):
        self.assertIn('State of Leonida', self.all_text)
        self.assertIn('Vice City', self.all_text)
        self.assertIn('Jason Duval', self.all_text)
        self.assertIn('Lucia Caminos', self.all_text)

    # --- Editions & pricing & bonuses ---
    def test_editions_pricing(self):
        self.assertIn('Standard Edition', self.all_text)
        self.assertIn('Ultimate Edition', self.all_text)
        self.assertIn('$79.99', self.all_text)
        self.assertIn('$99.99', self.all_text)

    def test_preorder_bonuses_and_vintage_pack(self):
        self.assertIn('Vintage Vice City Pack', self.all_text)
        self.assertIn('55 Vapid Stanier', self.all_text)
        self.assertRegex(self.all_text, r'GTA\+')
        self.assertIn('Nov 20, 2026', self.all_text)

    def test_ultimate_features(self):
        for item in ['Grotti Cheetah', 'Hawk & Little Morgan', 'Shitzu Squalo', 'Dinka Enduro', 'Paradise Garage']:
            self.assertIn(item, self.all_text)

    # --- Locations (Leonida) ---
    def test_locations(self):
        for loc in ['Vice City', 'Leonida Keys', 'Grassrivers', 'Port Gellhorn', 'Ambrosia', 'Mount Kalaga']:
            self.assertIn(loc, self.all_text)
        for img in ['vice_city.png','leonida_keys.png','grassrivers.png','port_gellhorn.png','ambrosia.png','mount_kalaga.png']:
            self.assertTrue(exists(f"build/web/gta6/assets/locations/{img}"), msg=f"missing location image {img}")
            self.assertTrue(exists(f"assets/images/in_game/gta6/locations/{img}"), msg=f"missing source location image {img}")

    # --- Characters ---
    def test_characters(self):
        for name in ['Jason Duval','Lucia Caminos','Cal Hampton','Boobie Ike',"Dre'Quan Priest",'Real Dimez','Raul Bautista','Brian Heder']:
            self.assertIn(name, self.all_text)
        for img in ['jason_lucia.png','jason.png','lucia.png','cal.png','boobie.png','drequan.png','realdimez.png','raul.png','brian.png']:
            self.assertTrue(exists(f"build/web/gta6/assets/characters/{img}"), msg=f"missing character image {img}")

    # --- Trailers / media ---
    def test_trailers_media(self):
        self.assertIn('Trailer 1', self.all_text)
        self.assertIn('Trailer 2', self.all_text)
        self.assertRegex(self.all_text, r'An Extended Look')
        self.assertIn('rockstargames.com/VI', self.all_text)
        self.assertRegex(self.all_text, r'Gallery|gallery')

    def test_gallery_screenshots_assets(self):
        for i in range(1,9):
            self.assertTrue(exists(f"build/web/gta6/assets/screenshots/s0{i}_"), msg=f"missing screenshot pattern s0{i}") if False else None
        # explicit checks
        for name in ['s01_vice_skyline.png','s02_keys_water.png','s03_grassrivers.png','s04_port_gellhorn.png','s05_ambrosia.png','s06_mount_kalaga.png','s07_jason_lucia.png','s08_heist.png']:
            self.assertTrue(exists(f"build/web/gta6/assets/screenshots/{name}"), msg=f"missing screenshot {name}")

    # --- Preload/storage/features ---
    def test_preload_storage_features(self):
        self.assertIn('212 GB', self.all_text)
        self.assertRegex(self.all_text, r'Pre-?load', msg="preload info missing")
        self.assertIn('November 12, 2026', self.all_text)
        self.assertRegex(self.all_text, r'DualSense|haptic', msg="PS5 features missing")

    # --- Packaging / injection ---
    def test_packaged_and_injected(self):
        self.assertTrue(exists("build/web/package_manifest.json"))
        self.assertTrue(exists("build/package/spatial-avy-web-client-player.tar.gz"))
        self.assertTrue(exists("build/web/data/build/web/gta6/index.html"))
        self.assertTrue(exists("build/web/data/build/web/gta6/assets/loading_screen.png"))
        manifest = load_json("build/web/package_manifest.json")
        self.assertEqual(manifest.get("client_entry"), "build/web/index.html")
        self.assertTrue(exists("build/web/data/" + manifest.get("client_entry","")))

    def test_web_client_link(self):
        idx = read("build/web/index.html")
        self.assertIn("gta6/index.html", idx)

if __name__ == "__main__":
    unittest.main(verbosity=2)
