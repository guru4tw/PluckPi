# -*- coding: utf-8 -*-
"""首頁一句話輪播測試:從 Docs/pikmin_bloom_oneliners.md 讀出 31 句「X版:句子」,不帶編號、不混進梗定義或驗證器。

跑法:python3 -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Py"))
import build_site  # noqa: E402


class OnelinersTest(unittest.TestCase):
    def setUp(self):
        self.quips = build_site.load_oneliners()

    def test_count(self):
        self.assertEqual(len(self.quips), 31)

    def test_label_and_text(self):
        self.assertEqual(self.quips[0][0], "反差版")
        self.assertTrue(self.quips[0][1].startswith("表面上是療癒散步遊戲"))
        for label, text in self.quips:
            self.assertIn("版", label)
            self.assertFalse(text[:1].isdigit(), text)
            self.assertNotIn("**", label + text)

    def test_index_has_quips(self):
        html = build_site.quip_html(self.quips)
        self.assertIn('class="quip"', html)
        self.assertIn("反差版", html)


if __name__ == "__main__":
    unittest.main()
