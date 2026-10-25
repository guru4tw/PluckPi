# -*- coding: utf-8 -*-
"""收集台與建站測試:STE100 檢查規則、詞彙表、以 slug 存入、條目頁渲染。不連網(fetch_pages 換成假資料)。

跑法:python3 -m unittest discover -s tests
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Py"))

import build_site  # noqa: E402
import common  # noqa: E402
import desk  # noqa: E402
import ste  # noqa: E402

BANNED = {"花蜜": "精華", "遠征": "探險"}
GOOD = dict(facts=["紅色皮克敏需要走 1,000 步。", "玩家可以拔出紅色皮克敏。"],
            steps=["打開花苗包。"], exceptions=[], terms=["花苗 = 走路後長出皮克敏的苗"])


def msgs(**kw):
    a = {**GOOD, **kw}
    return [i.msg for i in ste.lint(a["facts"], a["steps"], a["exceptions"], a["terms"], banned=BANNED,
                                    headline=a.get("headline"))]


class LintTest(unittest.TestCase):
    def test_good_passes(self):
        self.assertEqual(msgs(), [])

    def test_headline_only_when_given(self):
        self.assertTrue(any("名稱:特性" in m for m in msgs(headline="紅色皮克敏")))
        self.assertEqual(msgs(headline="紅色皮克敏:不怕火"), [])

    def test_sentence_rules(self):
        cases = {
            "紅色皮克敏像小炸彈。": "比喻",
            "紅色皮克敏被玩家拔出來。": "被動",
            "紅色皮克敏會開花,並且會走路。": "兩件事",
            "牠會開花。": "代名詞",
            "皮克敏喝了花蜜會開花。": "改用「精華」",
            "皮克敏是最強的夥伴。": "誇張",
            "紅色皮克敏" * 6 + "。": "上限",
        }
        for s, want in cases.items():
            with self.subTest(s=s):
                self.assertTrue(any(want in m for m in msgs(facts=[s])), msgs(facts=[s]))

    def test_image_is_not_metaphor(self):
        self.assertEqual(msgs(facts=["圖鑑有皮克敏的圖像。"]), [])

    def test_steps_limit_and_terms(self):
        self.assertEqual(msgs(steps=["打開設定。"] * 6), [])
        self.assertTrue(any("上限 6" in m for m in msgs(steps=["打開設定。"] * 7)))
        self.assertTrue(any("詞 = 定義" in m for m in msgs(terms=["花苗:苗"])))
        self.assertTrue(any("至少" in m for m in msgs(facts=[])))


class GlossaryTest(unittest.TestCase):
    def test_parse(self):
        g = ste.parse_glossary_text("說明\n- 精華 | 花蜜, 果汁 | 餵皮克敏\n- 社群日 |  | 每月一天\n")
        self.assertEqual(g, {"花蜜": "精華", "果汁": "精華"})

    def test_bad_line(self):
        with self.assertRaises(ste.GlossaryFormatError):
            ste.parse_glossary_text("- 精華 | 花蜜\n")

    def test_repo_glossary(self):
        g = ste.load_glossary()
        self.assertEqual(g["花蜜"], "精華")
        self.assertEqual(g["遠征"], "探險")
        for std in ("巨大花朵", "花苗包"):            # 禁用詞不能是標準詞的子字串
            self.assertFalse([w for w in g if w in std], std)

    def test_parse_terms(self):
        self.assertEqual(ste.parse_terms(["花苗 = 苗", "壞行"]), [{"term": "花苗", "def": "苗"}])


TOPICS = """# 2. 走路與成長 (grow)
> 大綱
## 2.2 花苗 (seedlings) · 入門
> 說明
- 花苗要走幾步才會長大? (seedling-steps) | pikipedia:Seedling; https://pikminbloom.com/zh_hant/ | 狀態=待證
- 花苗從哪裡來? (seedling-sources) | pikipedia:Seedling
- 壞來源 (bad-source) | https://example.com/x
"""
PAGE = {"pageid": 1, "title": "Seedling", "extract": "Seedlings grow ...", "lastrevid": 999999,
        "canonicalurl": "https://www.pikminwiki.com/Seedling"}


class SaveTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "knowledge.json"
        self.tmp.write_text(json.dumps([{"slug": "seedling-steps", "facts_zh": ["舊的。"], "hidden": False,
                                         "link_ok": True}], ensure_ascii=False), encoding="utf-8")
        desk._page_cache.clear()
        real_load, real_save = common.load_knowledge, common.save_knowledge
        self.patches = [
            mock.patch.object(desk, "fetch_pages", return_value={"Seedling": PAGE}),
            mock.patch.object(desk, "parse_categories", lambda: common.parse_categories_text(TOPICS)),
            mock.patch.object(desk, "load_knowledge", lambda: real_load(self.tmp)),
            mock.patch.object(desk, "save_knowledge", lambda es: real_save(es, self.tmp)),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def body(self, slug="seedling-steps", **kw):
        return {"slug": slug, "facts_zh": GOOD["facts"], "steps_zh": GOOD["steps"], "exceptions_zh": [],
                "terms_zh": GOOD["terms"], **kw}

    def saved(self):
        return {e["slug"]: e for e in json.loads(self.tmp.read_text(encoding="utf-8"))}

    def test_update_by_slug(self):
        r = desk.save(self.body(), accessed="2026-10-25")
        self.assertTrue(r["ok"], r)
        e = self.saved()["seedling-steps"]
        self.assertEqual(e["facts_zh"], GOOD["facts"])
        self.assertEqual(e["terms_zh"], [{"term": "花苗", "def": "走路後長出皮克敏的苗"}])
        self.assertEqual([s["grade"] for s in e["sources"]], ["B", "A"])
        self.assertEqual((e["sources"][0]["revid"], e["sources"][0]["license"]), (999999, "CC BY-SA 4.0"))
        self.assertEqual(e["sources"][1]["name"], "Pikmin Bloom 官網")
        self.assertEqual(e["status"], "curated")

    def test_two_questions_share_one_source_page(self):
        desk.save(self.body("seedling-steps"))
        desk.save(self.body("seedling-sources"))
        self.assertEqual(set(self.saved()), {"seedling-steps", "seedling-sources"})

    def test_lint_failure_does_not_write(self):
        before = self.tmp.read_text(encoding="utf-8")
        r = desk.save(self.body(facts_zh=["牠被丟出去。"]))
        self.assertFalse(r["ok"])
        self.assertEqual(self.tmp.read_text(encoding="utf-8"), before)

    def test_ungraded_source_rejected(self):
        with self.assertRaises(LookupError):
            desk.save(self.body("bad-source"))

    def test_not_in_queue(self):
        with self.assertRaises(LookupError):
            desk.save(self.body("no-such-question"))

    def test_queue_view(self):
        q = {x["slug"]: x for x in desk.queue_view()}
        self.assertEqual(q["seedling-steps"]["state"], "done")
        self.assertEqual(q["seedling-sources"]["state"], "todo")
        self.assertEqual(q["seedling-steps"]["status"], "待證")


class EntryPageTest(unittest.TestCase):
    def test_entry_page(self):
        cats = common.parse_categories_text(TOPICS)
        raw = [{"slug": "seedling-steps", "facts_zh": ["事實一。"], "steps_zh": ["步驟一。"], "exceptions_zh": [],
                "terms_zh": [{"term": "花苗", "def": "苗"}], "curated_at": "2026-10-25",
                "sources": [{"grade": "B", "name": "Pikipedia", "title": "Seedling", "url": "https://x",
                             "revid": 1, "license": "CC BY-SA 4.0", "accessed": "2026-10-25"}]}]
        done = build_site.written(cats, raw)
        self.assertEqual(set(done), {"seedling-steps"})
        c = cats[0]; t = c.topics[0]
        h = build_site.build_entry(c, t, done["seedling-steps"])
        for want in ("花苗要走幾步才會長大?", "<li>事實一。</li>", "怎麼做", "B Pikipedia", "待證", "版本 1"):
            self.assertIn(want, h)
        th = build_site.build_topic(c, t, done)
        self.assertIn("../../../zh-hant/k/seedling-steps/", th)
        self.assertIn("還沒寫", th)                 # seedling-sources 還沒寫,不給連結


if __name__ == "__main__":
    unittest.main()
