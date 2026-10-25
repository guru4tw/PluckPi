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

# ## 1. 入門基礎 (basics) · 入門
HEADING_RE = re.compile(r"^##\s+(\d+)\.\s*(.+?)\s*\(([a-z0-9_-]+)\)\s*(?:[·・]\s*(入門|進階|達人))?\s*$")
# >> en: Pikmin Types — Each Pikmin type's traits, immunities and uses.
LANG_RE = re.compile(r"^>>\s*([a-z-]+)\s*:\s*(.+?)\s*$")
# 標題裡出現這些符號,多半是把英文名寫進來了(英文要寫在 >> en: 行)
NAME_BAD = ("|", "｜", "/", "—")
ITEM_KEYS = {"先讀": "prereq"}     # 條目行的具名欄位 → QueueItem 屬性


class TopicsFormatError(ValueError):
    """topics.md 有無法解析的行。訊息帶「檔名:行號」,寧可擋下建站也不默默吞掉。"""


@dataclass
class Topic:
    order: int
    name: str
    slug: str
    level: str = "入門"
    desc: str = ""
    name_en: str = ""
    desc_en: str = ""
    items: List["QueueItem"] = field(default_factory=list)


@dataclass
class QueueItem:
    title: str        # Pikipedia 頁名
    title_zh: str
    topic: str        # slug
    level: str
    prereq: Optional[str] = None   # 先讀=頁名(跨主題前置,選配)


def parse_item(body: str, cur: Topic, fail) -> QueueItem:
    """`頁名 | 中文標題 | 難度(可省) | key=value ...` → QueueItem。難度只能在第 3 欄,具名欄位之後不能再有位置欄。"""
    cols = [c.strip() for c in body.split("|")]
    if len(cols) < 2 or not all(cols):
        fail("條目要寫成「- 頁名 | 中文標題 | 難度(可省)」,且每欄不可空白")
    item = QueueItem(title=cols[0], title_zh=cols[1], topic=cur.slug, level=cur.level)
    for i, col in enumerate(cols[2:], start=2):
        if "=" in col:
            key, _, val = (x.strip() for x in col.partition("="))
            if key not in ITEM_KEYS or not val:
                fail(f"不認得的欄位「{col}」(可用:{'、'.join(ITEM_KEYS)})")
            setattr(item, ITEM_KEYS[key], val)
        elif i == 2 and col in LEVELS:
            item.level = col
        else:
            fail(f"第 {i + 1} 欄「{col}」不是難度({'/'.join(LEVELS)},只能放第 3 欄)也不是 key=value")
    return item


def parse_topics_text(text: str, src: str = "topics.md") -> List[Topic]:
    """解析 topics.md 內容 → Topic 清單(含各自的佇列),依主題編號排序。

    第一個 `##` 之前是檔頭說明,不解析;之後每一行都要認得,認不得就丟 TopicsFormatError。
    """
    topics: List[Topic] = []
    cur: Optional[Topic] = None
    for n, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        def fail(msg: str):
            raise TopicsFormatError(f"{src}:{n}: {msg}\n  {line}")
        if line.startswith("##"):
            m = HEADING_RE.match(line)
            if not m:
                fail("主題標題要寫成「## 數字. 中文名 (slug) · 預設難度(可省)」")
            name = m.group(2)
            if any(ch in name for ch in NAME_BAD):
                fail("主題名只放中文;英文名請寫在下一行「>> en: 英文名 — 英文說明」")
            if any(t.slug == m.group(3) for t in topics):
                fail(f"主題 slug「{m.group(3)}」重複")
            cur = Topic(order=int(m.group(1)), name=name, slug=m.group(3), level=m.group(4) or "入門")
            topics.append(cur)
        elif cur is None or not line:
            continue
        elif line.startswith(">>"):
            m = LANG_RE.match(line)
            if not m or m.group(1) != "en":
                fail("語系行目前只支援「>> en: 英文名 — 英文說明」")
            if cur.name_en:
                fail("同一主題只能有一行 >> en:")
            name_en, _, desc_en = m.group(2).partition("—")
            cur.name_en, cur.desc_en = name_en.strip(), desc_en.strip()
        elif line.startswith(">"):
            if cur.desc:
                fail("主題說明只能一行(第一行 > 之後不能再有 >)")
            cur.desc = line[1:].strip()
        elif line.startswith("- "):
            cur.items.append(parse_item(line[2:], cur, fail))
        else:
            fail("認不得這行:主題內只能有 > 說明、>> en: 英文、- 條目")
    return sorted(topics, key=lambda t: t.order)


def parse_topics(path: Path = TOPICS_MD) -> List[Topic]:
    return parse_topics_text(path.read_text(encoding="utf-8"), path.name)


def queue_items(topics: List[Topic]) -> List[QueueItem]:
    return [it for t in topics for it in t.items]


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
