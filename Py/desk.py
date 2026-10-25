#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
desk.py — 收集台:本機手動收集 + STE100 撰寫,存入就寫回 Docs/knowledge.json
================================================================================

一個條目 = topics.md 裡的一個玩家問題,以條目 slug 為鍵(多個問題可以共用同一個來源頁)。
流程:
  1. 從 topics.md 佇列挑一個問題(分類、難度、先讀、待證、期限都以 topics.md 為準,這裡不改)
  2. 「抓取原文」→ Pikipedia 來源抓摘要與版號(沿用 collect_pikipedia.fetch_pages);官方來源列出連結,自己點開讀
  3. 用 STE100-Brief 寫事實、步驟、例外、詞彙;ste.py 即時檢查
  4. 檢查全過才能「存入」→ 以 slug 合併寫回 Docs/knowledge.json(status=curated)

存完要上站:python3 Py/verify_sources.py && python3 Py/build_site.py,再 commit。
只綁 127.0.0.1,不對外。單執行緒,寫檔不會互搶。

用法:
    python3 Py/desk.py              # http://127.0.0.1:8767/
    python3 Py/desk.py --port 9000
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from collect_pikipedia import fetch_pages
from common import (KNOWLEDGE_JSON, PIKIPEDIA, ROOT, TODAY, QueueItem, Topic, load_knowledge, official_name,
                    parse_categories, pikipedia_url, queue_items, save_knowledge, source_grade)
from ste import issues_json, lint, parse_terms

DESK_HTML = Path(__file__).resolve().parent / "desk.html"
STYLE_CSS = ROOT / "assets" / "style.css"
CONTENT = ("facts_zh", "steps_zh", "exceptions_zh", "terms_zh")

_page_cache: Dict[str, dict] = {}     # Pikipedia 頁名 → MediaWiki page dict(抓過就不重抓,存入時直接用)


def parse_topics() -> List[Topic]:
    return [t for c in parse_categories() for t in c.topics]


def find_entry(entries: List[dict], slug: str) -> Optional[dict]:
    return next((e for e in entries if e.get("slug") == slug), None)


def queue_item(slug: str) -> Tuple[QueueItem, List[Topic]]:
    topics = parse_topics()
    for it in queue_items(topics):
        if it.slug == slug:
            return it, topics
    raise LookupError(f"「{slug}」不在 topics.md;先在 Docs/topics.md 對應子分類下加一行")


def content_view(e: Optional[dict]) -> dict:
    """條目已存的內容 → 編輯器用的純文字清單。"""
    e = e or {}
    return {"facts_zh": e.get("facts_zh", []), "steps_zh": e.get("steps_zh", []),
            "exceptions_zh": e.get("exceptions_zh", []),
            "terms_zh": [f"{t['term']} = {t['def']}" for t in e.get("terms_zh", [])]}


def queue_view() -> List[dict]:
    cats = parse_categories()
    entries = load_knowledge()
    out = []
    for c in cats:
        for t in c.topics:
            for it in t.items:
                e = find_entry(entries, it.slug)
                out.append({"slug": it.slug, "title_zh": it.title_zh, "topic": t.slug,
                            "topic_name": f"{t.number} {t.name}", "category": f"{c.order}. {c.name}",
                            "level": it.level, "status": it.status,
                            "state": "done" if e and e.get("facts_zh") else "todo"})
    return out


def get_page(title: str, refresh: bool = False) -> dict:
    if refresh or title not in _page_cache:
        p = fetch_pages([title]).get(title) or {}
        if p.get("missing") or "pageid" not in p:
            raise LookupError(f"Pikipedia 找不到頁面「{title}」,請檢查 topics.md 來源")
        _page_cache[title] = p
    return _page_cache[title]


def sources_view(it: QueueItem, refresh: bool) -> List[dict]:
    out = []
    for s in it.sources:
        if s.kind == "pikipedia":
            p = get_page(s.ref, refresh)
            out.append({"kind": "pikipedia", "grade": "B", "name": PIKIPEDIA["name"], "title": p["title"],
                        "url": p.get("canonicalurl") or pikipedia_url(p["title"]), "revid": p.get("lastrevid"),
                        "excerpt": (p.get("extract") or "").strip()})
        else:
            out.append({"kind": "url", "grade": source_grade(s), "name": official_name(s.ref), "url": s.ref})
    return out


def fetch_view(slug: str) -> dict:
    it, _ = queue_item(slug)
    old = find_entry(load_knowledge(), slug)
    return {"slug": it.slug, "title_zh": it.title_zh, "level": it.level, "status": it.status,
            "sources": sources_view(it, refresh=True), **content_view(old)}


def clean(rows) -> List[str]:
    return [str(r).strip() for r in (rows or []) if str(r).strip()]


def check(body: dict) -> list:
    return lint(clean(body.get("facts_zh")), clean(body.get("steps_zh")),
                clean(body.get("exceptions_zh")), clean(body.get("terms_zh")))


def entry_sources(it: QueueItem, accessed: str) -> List[dict]:
    """存檔用的來源清單。Pikipedia 記版號與授權;官方網址記查閱日。不合格的來源直接擋。"""
    out = []
    for s in it.sources:
        grade = source_grade(s)
        if not grade:
            raise LookupError(f"來源「{s.ref}」不是 A(官方)或 B(Pikipedia),不能用")
        if s.kind == "pikipedia":
            p = get_page(s.ref)
            out.append({"kind": "pikipedia", "grade": "B", "name": PIKIPEDIA["name"], "title": p["title"],
                        "url": p.get("canonicalurl") or pikipedia_url(p["title"]), "revid": p.get("lastrevid"),
                        "license": PIKIPEDIA["license"], "license_url": PIKIPEDIA["license_url"],
                        "accessed": accessed})
        else:
            out.append({"kind": "url", "grade": grade, "name": official_name(s.ref), "url": s.ref,
                        "accessed": accessed})
    return out


def save(body: dict, accessed: str = TODAY) -> dict:
    issues = check(body)
    if issues:
        return {"ok": False, "issues": issues_json(issues)}
    it, _ = queue_item(body.get("slug", ""))
    entries = load_knowledge()
    old = find_entry(entries, it.slug)
    entry = dict(old or {})
    entry.update({
        "id": it.slug, "slug": it.slug, "topic": it.topic,
        "facts_zh": clean(body.get("facts_zh")),
        "steps_zh": clean(body.get("steps_zh")),
        "exceptions_zh": clean(body.get("exceptions_zh")),
        "terms_zh": parse_terms(clean(body.get("terms_zh"))),
        "sources": entry_sources(it, accessed),
        "status": "curated", "curated_by": body.get("curated_by") or "manual", "curated_at": TODAY,
    })
    entry.setdefault("hidden", False)
    if old:
        old.clear(); old.update(entry)
    else:
        entries.append(entry)
    order = {q.slug: i for i, q in enumerate(queue_items(parse_topics()))}
    entries.sort(key=lambda e: (order.get(e.get("slug"), 10 ** 6), e.get("slug") or ""))
    save_knowledge(entries)
    return {"ok": True, "slug": it.slug, "file": str(KNOWLEDGE_JSON.relative_to(ROOT))}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data, code: int = 200) -> None:
        self._send(code, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _guard(self, fn) -> None:
        try:
            self._json(fn())
        except LookupError as ex:
            self._json({"ok": False, "error": str(ex)}, 404)
        except Exception as ex:  # 網路、格式錯等:回給畫面看,不讓伺服器掛掉
            self._json({"ok": False, "error": f"{type(ex).__name__}: {ex}"}, 500)

    def do_GET(self) -> None:
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path in ("/", "/index.html"):
            self._send(200, DESK_HTML.read_bytes(), "text/html; charset=utf-8")
        elif u.path == "/assets/style.css":
            self._send(200, STYLE_CSS.read_bytes(), "text/css; charset=utf-8")
        elif u.path == "/api/queue":
            self._guard(queue_view)
        elif u.path == "/api/fetch":
            self._guard(lambda: fetch_view((q.get("slug") or [""])[0]))
        else:
            self._json({"ok": False, "error": "not found"}, 404)

    def do_POST(self) -> None:
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
        except ValueError:
            return self._json({"ok": False, "error": "JSON 格式錯"}, 400)
        if self.path == "/api/lint":
            self._guard(lambda: {"issues": issues_json(check(body))})
        elif self.path == "/api/save":
            self._guard(lambda: save(body))
        else:
            self._json({"ok": False, "error": "not found"}, 404)

    def log_message(self, fmt, *args) -> None:
        if "/api/save" in self.requestline or "/api/fetch" in self.requestline:
            sys.stderr.write(f"  {self.requestline}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8767)
    args = ap.parse_args()
    srv = HTTPServer(("127.0.0.1", args.port), Handler)
    print(f"收集台:http://127.0.0.1:{args.port}/  (Ctrl+C 結束)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
