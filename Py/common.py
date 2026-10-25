#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
common.py — 四支腳本共用的小工具:路徑、日期、topics.md 解析、knowledge.json 讀寫。

topics.md 是唯一的脈絡來源,collect 與 build 都從這裡讀主題與佇列,
所以解析規則只寫一次、放在這裡。
"""
from __future__ import annotations

import datetime
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "Docs"
TOPICS_MD = DOCS / "topics.md"
KNOWLEDGE_JSON = DOCS / "knowledge.json"       # 收集腳本合併寫入的原始資料
SITE_JSON = ROOT / "knowledge.json"            # 前端讀的正規化資料(build 產)

SITE_BASE = "https://guru4tw.github.io/PluckPi/"
SITE_NAME = "拔拔道場 PluckPi"
UA = "PluckPiBot/0.1 (+https://github.com/guru4tw/PluckPi; weekly knowledge digest)"

LEVELS = ("入門", "進階", "達人")
TODAY = datetime.date.today().isoformat()

# # 1. 開始玩 (start)
CAT_RE = re.compile(r"^#\s+(\d+)\.\s*(.+?)\s*\(([a-z0-9_-]+)\)\s*$")
# ## 1.2 第一天要做的事 (first-day) · 入門
SUB_RE = re.compile(r"^##\s+(\d+)\.(\d+)\s*(.+?)\s*\(([a-z0-9_-]+)\)\s*(?:[·・]\s*(入門|進階|達人))?\s*$")
# >> en: Pikmin Types — Each Pikmin type's traits, immunities and uses.
LANG_RE = re.compile(r"^>>\s*([a-z-]+)\s*:\s*(.+?)\s*$")
# - 我走路為什麼沒算到步數? (steps-not-counted)
QUESTION_RE = re.compile(r"^(.+?)\s*\(([a-z0-9-]+)\)$")
# 名稱裡出現這些符號,多半是把英文名寫進來了(英文要寫在 >> en: 行)
NAME_BAD = ("|", "｜", "/", "—")
ITEM_KEYS = {"先讀": "prereq", "狀態": "status", "期限": "expires"}   # 條目行的具名欄位 → QueueItem 屬性
STATUSES = ("待證",)


class TopicsFormatError(ValueError):
    """topics.md 有無法解析的行。訊息帶「檔名:行號」,寧可擋下建站也不默默吞掉。"""


@dataclass
class Source:
    kind: str     # pikipedia / url
    ref: str      # Pikipedia 頁名或完整網址


@dataclass
class Topic:
    """子分類。網站上的一個子分類頁;條目掛在這裡。"""
    order: int                 # 全站流水號(排序用)
    name: str
    slug: str
    level: str = "入門"
    desc: str = ""
    name_en: str = ""
    desc_en: str = ""
    number: str = ""           # 顯示用編號,例 "1.2"
    category: str = ""         # 所屬大分類 slug
    items: List["QueueItem"] = field(default_factory=list)


@dataclass
class Category:
    """大分類。網站上的一個大綱頁;首頁網站地圖的一格。"""
    order: int
    name: str
    slug: str
    outline: str = ""          # 一行大綱
    name_en: str = ""
    desc_en: str = ""
    topics: List[Topic] = field(default_factory=list)


@dataclass
class QueueItem:
    title_zh: str               # 玩家問題
    slug: str                   # 條目網址,全站唯一
    sources: List[Source]
    topic: str                  # 子分類 slug
    level: str
    prereq: Optional[str] = None    # 先讀=條目 slug(選配)
    status: Optional[str] = None    # 狀態=待證(只有一個來源或來源不夠硬)
    expires: Optional[str] = None   # 期限=YYYY-MM-DD(活動類)

    @property
    def title(self) -> str:
        """第一個 Pikipedia 頁名;沒有就給第一個網址。收集器用它抓原文。"""
        pk = [s.ref for s in self.sources if s.kind == "pikipedia"]
        return pk[0] if pk else self.sources[0].ref


def parse_sources(col: str, fail) -> List[Source]:
    """`pikipedia:頁名; https://…` → Source 清單。每條至少一個來源。"""
    out: List[Source] = []
    for raw in (x.strip() for x in col.split(";")):
        if raw.startswith("pikipedia:") and raw[10:].strip():
            out.append(Source("pikipedia", raw[10:].strip()))
        elif re.match(r"^https?://\S+$", raw):
            out.append(Source("url", raw))
        else:
            fail(f"來源「{raw}」要寫成「pikipedia:頁名」或完整網址,多個用 ; 分開")
    return out


def parse_item(body: str, cur: Topic, fail) -> QueueItem:
    """`玩家問題 (slug) | 來源 | 難度(可省) | key=value ...` → QueueItem。難度只能在第 3 欄。"""
    cols = [c.strip() for c in body.split("|")]
    if len(cols) < 2 or not all(cols):
        fail("條目要寫成「- 玩家問題 (slug) | 來源 | 難度(可省)」,且每欄不可空白")
    m = QUESTION_RE.match(cols[0])
    if not m:
        fail("玩家問題後面要接半形括號 slug,例:「我走路為什麼沒算到步數? (steps-not-counted)」")
    item = QueueItem(title_zh=m.group(1), slug=m.group(2), sources=parse_sources(cols[1], fail),
                     topic=cur.slug, level=cur.level)
    for i, col in enumerate(cols[2:], start=2):
        if "=" in col:
            key, _, val = (x.strip() for x in col.partition("="))
            if key not in ITEM_KEYS or not val:
                fail(f"不認得的欄位「{col}」(可用:{'、'.join(ITEM_KEYS)})")
            if key == "狀態" and val not in STATUSES:
                fail(f"狀態只能是 {'/'.join(STATUSES)}")
            if key == "期限" and not re.match(r"^\d{4}-\d{2}-\d{2}$", val):
                fail("期限要寫成 YYYY-MM-DD")
            setattr(item, ITEM_KEYS[key], val)
        elif i == 2 and col in LEVELS:
            item.level = col
        else:
            fail(f"第 {i + 1} 欄「{col}」不是難度({'/'.join(LEVELS)},只能放第 3 欄)也不是 key=value")
    return item


def parse_categories_text(text: str, src: str = "topics.md") -> List[Category]:
    """解析 topics.md → 大分類 → 子分類 → 條目。

    第一個 `# 數字.` 大分類之前是檔頭說明,不解析;之後每一行都要認得,認不得就丟 TopicsFormatError。
    """
    cats: List[Category] = []
    cat: Optional[Category] = None
    cur: Optional[Topic] = None
    seq = 0
    slugs: set = set()
    item_slugs: set = set()
    for n, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        def fail(msg: str):
            raise TopicsFormatError(f"{src}:{n}: {msg}\n  {line}")
        if cat is None and not CAT_RE.match(line):
            continue                                   # 檔頭
        if line.startswith("##"):
            m = SUB_RE.match(line)
            if not m:
                fail("子分類標題要寫成「## 大分類號.子分類號 中文名 (slug) · 預設難度(可省)」")
            if int(m.group(1)) != cat.order:
                fail(f"子分類編號 {m.group(1)}.{m.group(2)} 不屬於大分類 {cat.order}")
            name, slug = m.group(3), m.group(4)
            if any(ch in name for ch in NAME_BAD):
                fail("子分類名只放中文;英文名請寫在下一行「>> en: 英文名 — 英文說明」")
            if slug in slugs:
                fail(f"slug「{slug}」重複")
            seq += 1
            cur = Topic(order=seq, name=name, slug=slug, level=m.group(5) or "入門",
                        number=f"{m.group(1)}.{m.group(2)}", category=cat.slug)
            cat.topics.append(cur); slugs.add(slug)
        elif line.startswith("#"):
            m = CAT_RE.match(line)
            if not m:
                fail("大分類標題要寫成「# 數字. 中文名 (slug)」")
            name, slug = m.group(2), m.group(3)
            if any(ch in name for ch in NAME_BAD):
                fail("大分類名只放中文;英文名請寫在下一行「>> en: 英文名 — 英文說明」")
            if slug in slugs:
                fail(f"slug「{slug}」重複")
            cat = Category(order=int(m.group(1)), name=name, slug=slug)
            cur = None
            cats.append(cat); slugs.add(slug)
        elif not line:
            continue
        elif line.startswith(">>"):
            m = LANG_RE.match(line)
            if not m or m.group(1) != "en":
                fail("語系行目前只支援「>> en: 英文名 — 英文說明」")
            target = cur or cat
            if target.name_en:
                fail("同一分類只能有一行 >> en:")
            name_en, _, desc_en = m.group(2).partition("—")
            target.name_en, target.desc_en = name_en.strip(), desc_en.strip()
        elif line.startswith(">"):
            if cur is None:
                if cat.outline:
                    fail("大綱只能一行(第一行 > 之後不能再有 >)")
                cat.outline = line[1:].strip()
            else:
                if cur.desc:
                    fail("子分類說明只能一行(第一行 > 之後不能再有 >)")
                cur.desc = line[1:].strip()
        elif line.startswith("- "):
            if cur is None:
                fail("條目要放在子分類(##)底下,不能直接掛在大分類下")
            item = parse_item(line[2:], cur, fail)
            if item.slug in item_slugs:
                fail(f"條目 slug「{item.slug}」重複")
            item_slugs.add(item.slug)
            cur.items.append(item)
        else:
            fail("認不得這行:分類內只能有 # 大分類、## 子分類、> 說明、>> en: 英文、- 條目")
    cats.sort(key=lambda c: c.order)
    for i, t in enumerate((t for c in cats for t in c.topics), start=1):
        t.order = i                                   # 流水號跟著大分類順序重排
    for c in cats:
        if not c.topics:
            raise TopicsFormatError(f"{src}: 大分類「{c.name}」底下沒有子分類")
    return cats


def parse_categories(path: Path = TOPICS_MD) -> List[Category]:
    return parse_categories_text(path.read_text(encoding="utf-8"), path.name)


def parse_topics_text(text: str, src: str = "topics.md") -> List[Topic]:
    """攤平成子分類清單(依大分類、子分類順序)。建站與收集台以子分類為單位,用這個。"""
    return [t for c in parse_categories_text(text, src) for t in c.topics]


def parse_topics(path: Path = TOPICS_MD) -> List[Topic]:
    return parse_topics_text(path.read_text(encoding="utf-8"), path.name)


def queue_items(topics: List[Topic]) -> List[QueueItem]:
    return [it for t in topics for it in t.items]


# 來源分級:A 官方、B 社群百科(Pikipedia)。其他網域不算合格來源,收集台與測試會擋。
OFFICIAL_SITES = {
    "pikminbloom.com": "Pikmin Bloom 官網",
    "helpshift.com": "Pikmin Bloom 說明中心",
    "nintendo.com": "任天堂官網",
    "apps.apple.com": "App Store 開發商頁",
}
PIKIPEDIA = {"name": "Pikipedia", "license": "CC BY-SA 4.0",
             "license_url": "https://creativecommons.org/licenses/by-sa/4.0/"}


def source_grade(src: "Source") -> Optional[str]:
    """Source → "A" / "B" / None(不合格)。"""
    if src.kind == "pikipedia":
        return "B"
    host = re.sub(r"^https?://([^/]+).*$", r"\1", src.ref).lower()
    return "A" if any(host == d or host.endswith("." + d) for d in OFFICIAL_SITES) else None


def official_name(url: str) -> str:
    host = re.sub(r"^https?://([^/]+).*$", r"\1", url).lower()
    return next((n for d, n in OFFICIAL_SITES.items() if host == d or host.endswith("." + d)), host)


def pikipedia_url(page: str) -> str:
    return "https://www.pikminwiki.com/" + page.replace(" ", "_")


def norm_title(t: str) -> str:
    """MediaWiki 頁名正規化:底線→空白、首字大寫、多餘空白收斂。"""
    t = (t or "").replace("_", " ").strip()
    t = re.sub(r"\s+", " ", t)
    return t[:1].upper() + t[1:] if t else t


def make_slug(title: str, taken: set) -> str:
    """英文頁名 → 網址 slug(小寫、非英數轉 -);撞名加 -2、-3。"""
    base = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-") or "entry"
    slug, n = base, 2
    while slug in taken:
        slug, n = f"{base}-{n}", n + 1
    return slug


def ensure_slugs(entries: List[dict]) -> int:
    """缺 slug 的條目補上。slug 是條目網址,一旦產生永不改(標題改了也不變)。回傳補了幾筆。"""
    taken = {e["slug"] for e in entries if e.get("slug")}
    added = 0
    for e in entries:
        if not e.get("slug"):
            e["slug"] = make_slug(e.get("title_en") or e.get("id", ""), taken)
            taken.add(e["slug"]); added += 1
    return added


def load_knowledge(path: Path = KNOWLEDGE_JSON) -> List[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data.get("entries", [])


def save_knowledge(entries: List[dict], path: Path = KNOWLEDGE_JSON) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sort_key(topics: List[Topic]):
    """條目排序:主題順序 → 難度 → 中文標題。build 與 collect 共用,輸出才穩定(diff 乾淨)。"""
    order = {t.slug: t.order for t in topics}
    lv = {l: i for i, l in enumerate(LEVELS)}
    return lambda e: (order.get(e.get("topic"), 99), lv.get(e.get("level"), 9), e.get("title_zh") or e.get("title_en") or "")
