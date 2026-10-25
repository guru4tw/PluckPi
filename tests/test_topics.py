# -*- coding: utf-8 -*-
"""topics.md 解析測試:大分類 → 子分類 → 條目三層、來源欄、具名欄位、格式錯要報錯。

跑法:python3 -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Py"))

from common import (TOPICS_MD, TopicsFormatError, parse_categories, parse_categories_text,  # noqa: E402
                    parse_topics_text, queue_items)

GOOD = """# 檔頭標題,不是大分類
> 檔頭說明
> - 這行像條目但在檔頭,要略過

# 2. 走路與成長 (grow)
> 走路讓花苗長大。
>> en: Walk and grow — Steps grow seedlings.

## 2.1 花苗 (seedlings) · 進階
> 花苗靠步數長大。
- 花苗要走幾步才會長大? (seedling-steps) | pikipedia:Seedling
- 花苗包滿了怎麼辦? (seedling-slots) | pikipedia:Slot; https://example.com/faq | 達人 | 先讀=seedling-steps

# 1. 開始玩 (start)
> 裝好遊戲。

## 1.1 認識這個遊戲 (about)
- 要花錢嗎? (is-it-free) | https://example.com/a | 狀態=待證 | 期限=2026-12-31
"""


def bad(snippet: str, head: str = "# 1. 開始玩 (start)\n> 大綱\n## 1.1 子 (sub)\n") -> str:
    return head + snippet


class ParseTest(unittest.TestCase):
    def setUp(self):
        self.cats = parse_categories_text(GOOD)

    def test_categories_sorted_and_outline(self):
        self.assertEqual([c.slug for c in self.cats], ["start", "grow"])
        self.assertEqual(self.cats[1].outline, "走路讓花苗長大。")
        self.assertEqual((self.cats[1].name_en, self.cats[1].desc_en), ("Walk and grow", "Steps grow seedlings."))

    def test_subcategory(self):
        t = self.cats[1].topics[0]
        self.assertEqual((t.number, t.slug, t.level, t.category, t.desc), ("2.1", "seedlings", "進階", "grow", "花苗靠步數長大。"))

    def test_topic_order_follows_category_order(self):
        self.assertEqual([t.slug for t in parse_topics_text(GOOD)], ["about", "seedlings"])
        self.assertEqual([t.order for t in parse_topics_text(GOOD)], [1, 2])

    def test_items(self):
        a, b = self.cats[1].topics[0].items
        self.assertEqual((a.title_zh, a.slug, a.level, a.title), ("花苗要走幾步才會長大?", "seedling-steps", "進階", "Seedling"))
        self.assertEqual([(s.kind, s.ref) for s in b.sources], [("pikipedia", "Slot"), ("url", "https://example.com/faq")])
        self.assertEqual((b.level, b.prereq), ("達人", "seedling-steps"))
        c = self.cats[0].topics[0].items[0]
        self.assertEqual((c.status, c.expires, c.title), ("待證", "2026-12-31", "https://example.com/a"))

    def test_queue_items(self):
        self.assertEqual(len(queue_items(parse_topics_text(GOOD))), 3)


class ErrorTest(unittest.TestCase):
    CASES = {
        "no slug on question": "- 沒有 slug 的問題 | pikipedia:X\n",
        "bad source": "- 問題 (q) | Seedling\n",
        "empty column": "- 問題 (q) |  \n",
        "level not third": "- 問題 (q) | pikipedia:X | 狀態=待證 | 入門\n",
        "unknown key": "- 問題 (q) | pikipedia:X | 作者=我\n",
        "bad status": "- 問題 (q) | pikipedia:X | 狀態=確定\n",
        "bad expiry": "- 問題 (q) | pikipedia:X | 期限=明年\n",
        "duplicate item slug": "- 甲 (q) | pikipedia:X\n- 乙 (q) | pikipedia:Y\n",
        "two outlines": "> 第二行說明\n> 第三行\n",
        "stray line": "隨便一行\n",
    }

    def test_errors(self):
        for name, snippet in self.CASES.items():
            with self.subTest(name), self.assertRaises(TopicsFormatError):
                parse_categories_text(bad(snippet))

    def test_item_under_category(self):
        with self.assertRaises(TopicsFormatError):
            parse_categories_text("# 1. 開始玩 (start)\n- 問題 (q) | pikipedia:X\n")

    def test_sub_number_mismatch(self):
        with self.assertRaises(TopicsFormatError):
            parse_categories_text("# 1. 開始玩 (start)\n## 2.1 子 (sub)\n")

    def test_duplicate_slug_across_levels(self):
        with self.assertRaises(TopicsFormatError):
            parse_categories_text("# 1. 開始玩 (start)\n## 1.1 子 (start)\n")

    def test_empty_category(self):
        with self.assertRaises(TopicsFormatError):
            parse_categories_text("# 1. 開始玩 (start)\n> 大綱\n")

    def test_error_has_line_number(self):
        with self.assertRaises(TopicsFormatError) as cm:
            parse_categories_text(bad("隨便一行\n"))
        self.assertIn("topics.md:4:", str(cm.exception))


class RepoFileTest(unittest.TestCase):
    """真正的 Docs/topics.md 要能解析,而且守住網站精神裡的硬規則。"""

    def test_repo_topics(self):
        cats = parse_categories(TOPICS_MD)
        self.assertEqual(len(cats), 7)
        self.assertIn("trivia", [c.slug for c in cats])
        for c in cats:
            self.assertTrue(c.outline, f"{c.name} 缺大綱")
            for t in c.topics:
                self.assertTrue(t.desc, f"{t.name} 缺一句話說明")
                self.assertTrue(t.items, f"{t.name} 沒有條目")

    def test_every_item_has_graded_source(self):
        """每條至少一個 A(官方網域)或 B(Pikipedia)來源。"""
        official = ("pikminbloom.com", "helpshift.com", "nintendo.com", "apps.apple.com")
        for it in queue_items([t for c in parse_categories(TOPICS_MD) for t in c.topics]):
            ok = any(s.kind == "pikipedia" or any(d in s.ref for d in official) for s in it.sources)
            self.assertTrue(ok, f"{it.slug} 沒有 A/B 來源")


if __name__ == "__main__":
    unittest.main()
