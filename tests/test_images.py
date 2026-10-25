# -*- coding: utf-8 -*-
"""圖片登記簿測試:assets/img/ 每個檔都要登記,授權只能是允許清單,截圖在決定前不能放。

規則見 Docs/images.md。跑法:python3 -m unittest discover -s tests
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
REGISTRY = ROOT / "Docs" / "images.json"

LICENSES = {"CC0", "Public Domain", "CC BY 4.0", "CC BY-SA 4.0"}
KINDS = {"original", "own-photo", "commons", "system-screenshot"}   # 遊戲截圖不收(2026-10-25 決定 A+C)
SYSTEM_LICENSES = {"© Apple Inc.,教學說明引用", "© Google LLC,教學說明引用"}
FIELDS = ("file", "kind", "title", "author", "license", "license_url", "source_url", "added", "use", "alt")
MAX_SVG = 8 * 1024
MAX_PHOTO = 200 * 1024


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.rows = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.by_file = {r["file"]: r for r in self.rows}

    def test_fields(self):
        for r in self.rows:
            with self.subTest(r.get("file")):
                self.assertEqual(set(FIELDS), set(r), "欄位不齊或多了")
                self.assertIn(r["kind"], KINDS)
                if r["kind"] == "system-screenshot":
                    self.assertIn(r["license"], SYSTEM_LICENSES)
                    self.assertIsNone(r["license_url"])
                else:
                    self.assertIn(r["license"], LICENSES)
                self.assertRegex(r["added"], r"^\d{4}-\d{2}-\d{2}$")
                self.assertTrue(r["alt"].endswith("。"), "alt 用 STE100 寫成一句完整的句子")
                if r["kind"] == "commons":
                    self.assertTrue(r["source_url"], "commons 圖要有 source_url")

    def test_every_file_registered(self):
        files = {p.name for p in IMG.iterdir() if p.is_file() and not p.name.startswith(".")}
        self.assertEqual(files - set(self.by_file), set(), "有圖沒登記")
        self.assertEqual(set(self.by_file) - files, set(), "登記了但檔案不存在")

    def test_sizes(self):
        for p in IMG.iterdir():
            limit = MAX_SVG if p.suffix == ".svg" else MAX_PHOTO
            self.assertLessEqual(p.stat().st_size, limit, p.name)

    def test_svg_no_embedded_raster(self):
        """原創 SVG 不能夾帶點陣圖或外部連結(可能夾帶來路不明的圖)。"""
        for p in IMG.glob("*.svg"):
            text = p.read_text(encoding="utf-8")
            self.assertNotRegex(text, re.compile(r"<image|href=\"(http|data:)", re.I), p.name)
            self.assertIn("<title>", text, f"{p.name} 缺 <title>")


if __name__ == "__main__":
    unittest.main()
