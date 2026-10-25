# -*- coding: utf-8 -*-
"""topics.md 解析測試:舊格式、新格式(>> en: 行、key=value 欄)、省略難度,以及格式錯要報錯。

跑法:python3 -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Py"))

from common import TOPICS_MD, TopicsFormatError, parse_topics, parse_topics_text, queue_items  # noqa: E402

OLD = """# 標題
> 檔頭說明,不屬於任何主題
> - 這行像條目但在檔頭,要略過

## 2. 皮克敏圖鑑 (pikmin) · 入門
> 各色皮克敏的特性。
- Red Pikmin | 紅色皮克敏
- Purple Pikmin | 紫色皮克敏 | 進階

## 1. 入門基礎 (basics)
- Onion | 洋蔥(皮克敏的母艦)
"""

NEW = """## 2. 皮克敏圖鑑 (pikmin) · 入門
> 各色皮克敏的特性、免疫與用途。
>> en: Pikmin Types — Each Pikmin type's traits, immunities and uses.
- Red Pikmin | 紅色皮克敏
- Purple Pikmin | 紫色皮克敏 | 進階 | 先讀=Red Pikmin
- White Pikmin | 白色皮克敏 | 先讀=Red Pikmin
"""


def parse(text):
    return parse_topics_text(text, "topics.md")


class OldFormat(unittest.TestCase):
    def test_topics_sorted_by_order(self):
        ts = parse(OLD)
        self.assertEqual([t.slug for t in ts], ["basics", "pikmin"])

    def test_heading_fields(self):
        t = parse(OLD)[1]
        self.assertEqual((t.order, t.name, t.slug, t.level, t.desc), (2, "皮克敏圖鑑", "pikmin", "入門", "各色皮克敏的特性。"))

    def test_heading_level_omitted_defaults_to_beginner(self):
        self.assertEqual(parse(OLD)[0].level, "入門")

    def test_items(self):
        items = parse(OLD)[1].items
        self.assertEqual([(i.title, i.title_zh, i.topic, i.level) for i in items],
                         [("Red Pikmin", "紅色皮克敏", "pikmin", "入門"), ("Purple Pikmin", "紫色皮克敏", "pikmin", "進階")])

    def test_preamble_ignored(self):
        self.assertEqual(len(queue_items(parse(OLD))), 3)

    def test_no_english_means_empty(self):
        t = parse(OLD)[1]
        self.assertEqual((t.name_en, t.desc_en), ("", ""))
        self.assertIsNone(t.items[0].prereq)


class NewFormat(unittest.TestCase):
    def test_english_line(self):
        t = parse(NEW)[0]
        self.assertEqual(t.name_en, "Pikmin Types")
        self.assertEqual(t.desc_en, "Each Pikmin type's traits, immunities and uses.")
        self.assertEqual(t.desc, "各色皮克敏的特性、免疫與用途。")

    def test_english_name_only(self):
        t = parse("## 1. 入門基礎 (basics)\n>> en: Basics\n")[0]
        self.assertEqual((t.name_en, t.desc_en), ("Basics", ""))

    def test_named_field_does_not_leak_into_title_zh(self):
        purple = parse(NEW)[0].items[1]
        self.assertEqual((purple.title_zh, purple.level, purple.prereq), ("紫色皮克敏", "進階", "Red Pikmin"))

    def test_named_field_with_level_omitted(self):
        white = parse(NEW)[0].items[2]
        self.assertEqual((white.title_zh, white.level, white.prereq), ("白色皮克敏", "入門", "Red Pikmin"))


class Errors(unittest.TestCase):
    def assertBad(self, text, needle):
        with self.assertRaises(TopicsFormatError) as cm:
            parse(text)
        self.assertIn(needle, str(cm.exception))

    def test_item_missing_title_zh(self):
        self.assertBad("## 1. 入門基礎 (basics)\n- Onion\n", "topics.md:2")

    def test_unknown_field(self):
        self.assertBad("## 1. 入門基礎 (basics)\n- Onion | 洋蔥 | 前置=Leader\n", "前置")

    def test_bad_level(self):
        self.assertBad("## 1. 入門基礎 (basics)\n- Onion | 洋蔥 | 高手\n", "高手")

    def test_level_after_named_field(self):
        self.assertBad("## 1. 入門基礎 (basics)\n- Onion | 洋蔥 | 先讀=Leader | 進階\n", "topics.md:2")

    def test_empty_field(self):
        self.assertBad("## 1. 入門基礎 (basics)\n- Onion |  | 進階\n", "topics.md:2")

    def test_malformed_heading(self):
        self.assertBad("## 1. 入門基礎 basics\n", "topics.md:1")

    def test_english_in_heading(self):
        self.assertBad("## 2. 皮克敏圖鑑 / Pikmin Types (pikmin)\n", ">> en:")

    def test_unknown_lang_line(self):
        self.assertBad("## 1. 入門基礎 (basics)\n>> ja: 基本\n", "ja")

    def test_stray_text_in_topic(self):
        self.assertBad("## 1. 入門基礎 (basics)\n隨手寫的筆記\n", "topics.md:2")

    def test_duplicate_slug(self):
        self.assertBad("## 1. 入門基礎 (basics)\n## 2. 再一次 (basics)\n", "basics")


class RealFile(unittest.TestCase):
    def test_current_topics_md_parses(self):
        ts = parse_topics(TOPICS_MD)
        self.assertEqual(len(ts), 7)
        self.assertTrue(all(t.desc and t.items for t in ts))


if __name__ == "__main__":
    unittest.main()
