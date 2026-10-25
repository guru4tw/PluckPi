#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ste.py — 卡片內容的 STE100-Brief 檢查(收集台存檔前必過)

STE100(Simplified Technical English)在本站的落點:
  標題   條目標題就是玩家問題(topics.md),這裡不檢查;舊版「名稱:特性」標題仍可用 headline= 檢查
  事實   一句一件事、≤ 25 字、主動語態、不比喻、主詞寫全名、只用詞彙表標準詞
  步驟   最多 6 步,每步同事實句規則
  例外   同事實句規則
  詞彙   「詞 = 定義」

規則用關鍵字比對,會有誤判;誤判就改寫句子避開,不要放寬規則。
詞彙表在 Docs/glossary.md,格式錯直接丟 GlossaryFormatError。
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from common import DOCS

GLOSSARY_MD = DOCS / "glossary.md"
MAX_LEN = 25
MAX_STEPS = 6          # 設定教學常要 5 步(例:iPhone 計步權限),2026-10-25 從 3 放寬

HEADLINE_RE = re.compile(r"^[^:：]+[:：]\s*\S.*$")
HYPE_RE = re.compile(r"最強|必備|神級|超好用|無敵")
METAPHOR_RE = re.compile(r"(?<![圖影頭肖])像|如同|宛如|好比|彷彿")
PASSIVE_RE = re.compile(r"被")
MULTI_RE = re.compile(r"並且|而且|同時|以及|[,，]並")
PRONOUN_RE = re.compile(r"^(它們|牠們|他們|它|牠)")
TERM_RE = re.compile(r"^(.+?)\s*[=＝]\s*(.+)$")


class GlossaryFormatError(ValueError):
    """glossary.md 有無法解析的行。"""


@dataclass
class Issue:
    field: str              # headline / facts / steps / exceptions / terms
    index: Optional[int]    # 第幾行(1 起算);標題為 None
    msg: str


def parse_glossary_text(text: str, src: str = "glossary.md") -> Dict[str, str]:
    """→ {禁用詞: 標準詞}。只解析 `- ` 開頭的行。"""
    banned: Dict[str, str] = {}
    for n, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line.startswith("- "):
            continue
        cols = [c.strip() for c in line[2:].split("|")]
        if len(cols) != 3 or not cols[0] or not cols[2]:
            raise GlossaryFormatError(f"{src}:{n}: 要寫成「- 標準詞 | 禁用詞 | 白話定義」\n  {line}")
        for w in (w.strip() for w in re.split(r"[,，、]", cols[1])):
            if w:
                banned[w] = cols[0]
    return banned


def load_glossary(path: Path = GLOSSARY_MD) -> Dict[str, str]:
    return parse_glossary_text(path.read_text(encoding="utf-8"), path.name) if path.exists() else {}


def _sentence(field: str, i: int, s: str, banned: Dict[str, str]) -> List[Issue]:
    out: List[Issue] = []
    n = len(re.sub(r"\s", "", s))
    if n > MAX_LEN:
        out.append(Issue(field, i, f"{n} 字,上限 {MAX_LEN},拆成兩句"))
    if m := METAPHOR_RE.search(s):
        out.append(Issue(field, i, f"用了比喻(「{m.group()}」),直接寫事實"))
    if PASSIVE_RE.search(s):
        out.append(Issue(field, i, "被動語態(「被」),改成主動:誰做什麼"))
    if m := MULTI_RE.search(s):
        out.append(Issue(field, i, f"一句寫了兩件事(「{m.group()}」),拆成兩句"))
    if m := PRONOUN_RE.search(s):
        out.append(Issue(field, i, f"代名詞開頭(「{m.group()}」),改寫全名"))
    if m := HYPE_RE.search(s):
        out.append(Issue(field, i, f"誇張用語(「{m.group()}」)"))
    for w, std in banned.items():
        if w in s:
            out.append(Issue(field, i, f"「{w}」不在詞彙表,改用「{std}」"))
    return out


def lint(facts: List[str], steps: List[str], exceptions: List[str], terms: List[str],
         banned: Optional[Dict[str, str]] = None, headline: Optional[str] = None) -> List[Issue]:
    """回傳全部問題;空清單 = 可以存。headline 給了才檢查(Bloom 版條目用玩家問題當標題,不需要)。"""
    banned = load_glossary() if banned is None else banned
    out: List[Issue] = []
    if headline is not None:
        headline = headline.strip()
        if not HEADLINE_RE.match(headline):
            out.append(Issue("headline", None, "標題要寫成「名稱:特性」"))
        if m := HYPE_RE.search(headline):
            out.append(Issue("headline", None, f"誇張用語(「{m.group()}」)"))
    if not facts:
        out.append(Issue("facts", None, "至少要有一句事實"))
    if len(steps) > MAX_STEPS:
        out.append(Issue("steps", None, f"{len(steps)} 步,上限 {MAX_STEPS}"))
    for field, rows in (("facts", facts), ("steps", steps), ("exceptions", exceptions)):
        for i, s in enumerate(rows, start=1):
            out += _sentence(field, i, s, banned)
    for i, t in enumerate(terms, start=1):
        if not TERM_RE.match(t):
            out.append(Issue("terms", i, "要寫成「詞 = 定義」"))
    return out


def parse_terms(terms: List[str]) -> List[dict]:
    """["洋蔥 = 定義"] → [{"term": "洋蔥", "def": "定義"}];格式錯的行略過(lint 會先擋)。"""
    return [{"term": m.group(1).strip(), "def": m.group(2).strip()} for t in terms if (m := TERM_RE.match(t))]


def issues_json(issues: List[Issue]) -> List[dict]:
    return [asdict(i) for i in issues]
