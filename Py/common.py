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
# - Red Pikmin | 紅色皮克敏 | 進階
ITEM_RE = re.compile(r"^-\s+(.+?)\s*\|\s*(.+?)(?:\s*\|\s*(入門|進階|達人))?\s*$")


@dataclass
class Topic:
    order: int
    name: str
    slug: str
    level: str = "入門"
    desc: str = ""
    items: List["QueueItem"] = field(default_factory=list)


@dataclass
class QueueItem:
    title: str        # Pikipedia 頁名
    title_zh: str
    topic: str        # slug
    level: str


def parse_topics(path: Path = TOPICS_MD) -> List[Topic]:
    """解析 topics.md → Topic 清單(含各自的佇列)。格式錯的行直接略過,不中斷。"""
    topics: List[Topic] = []
    cur: Optional[Topic] = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        m = HEADING_RE.match(line)
        if m:
            cur = Topic(order=int(m.group(1)), name=m.group(2), slug=m.group(3), level=m.group(4) or "入門")
            topics.append(cur)
            continue
        if cur is None:
            continue
        if line.startswith(">") and not cur.desc:
            cur.desc = line.lstrip("> ").strip()
            continue
        m = ITEM_RE.match(line)
        if m:
            cur.items.append(QueueItem(title=m.group(1).strip(), title_zh=m.group(2).strip(),
                                       topic=cur.slug, level=m.group(3) or cur.level))
    return sorted(topics, key=lambda t: t.order)


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
