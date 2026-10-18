#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py — 把 Docs/knowledge.json 正規化成網站資料,並靜態生成子頁
=====================================================================

產物:
  knowledge.json         前端契約 {updated_at, count, license, topics[], entries[]}(只含未 hidden 條目)
  topics/{slug}.html     每主題一頁(靜態卡片 + ItemList JSON-LD),搜尋引擎可直接收錄
  sources/index.html     引用來源總表(每條知識的出處、版本、授權、查閱日)
  sitemap.xml            首頁 + 全部子頁
  index.html             在 MAP / STATS 標記之間注入道場地圖與統計(其餘不動)

主題順序、名稱、說明全部來自 Docs/topics.md,這裡不另外定義。

用法:
    python3 Py/build_site.py
    python3 Py/build_site.py --check   # 只檢查、印統計,不寫檔
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import List

from common import (ROOT, SITE_BASE, SITE_JSON, SITE_NAME, TODAY, LEVELS, Topic,
                    load_knowledge, parse_topics, sort_key)

TOPICS_DIR = ROOT / "topics"
SOURCES_DIR = ROOT / "sources"
SITEMAP = ROOT / "sitemap.xml"
INDEX = ROOT / "index.html"
LICENSE = {"name": "CC BY-SA 4.0", "url": "https://creativecommons.org/licenses/by-sa/4.0/"}

PUBLIC_FIELDS = ("id", "topic", "level", "title_zh", "title_en", "summary_zh", "key_points_zh",
                 "excerpt_en", "games", "source", "status", "fetched_at", "link_ok", "hidden")


def esc(s) -> str:
    return (str(s if s is not None else "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ── HTML 片段(與 index.html 的 JS 版本對齊,改一邊記得改另一邊)────────────
def card_html(e: dict) -> str:
    curated = e.get("status") == "curated" and e.get("summary_zh")
    s = e.get("source") or {}
    sum_html = (f'<p class="sum">{esc(e["summary_zh"])}</p>' if curated
                else f'<p class="sum en">{esc(e.get("excerpt_en"))}</p>')
    pts = "".join(f"<li>{esc(p)}</li>" for p in e.get("key_points_zh") or [])
    pts_html = f"<details><summary>重點</summary><ul>{pts}</ul></details>" if pts else ""
    orig = (f'<details><summary>原文(英文)</summary><p class="sum en">{esc(e.get("excerpt_en"))}</p></details>'
            if curated and e.get("excerpt_en") else "")
    games = "".join(f"<span>{esc(g)}</span>" for g in e.get("games") or [])
    games_html = f'<div class="games">{games}</div>' if games else ""
    link = ('<span class="warn">⚠ 連結待確認</span>' if e.get("link_ok") is False
            else ('<span class="ok">✓ 連結已驗證</span>' if e.get("link_ok") else ""))
    raw = "" if curated else '<span class="raw">待整理・原文</span>'
    return f"""<article class="card" id="{esc(e['id'])}">
  <div class="head"><span class="lv" data-lv="{esc(e.get('level'))}">{esc(e.get('level'))}</span>{raw}</div>
  <h3>{esc(e.get('title_zh') or e.get('title_en'))}<span class="en">{esc(e.get('title_en'))}</span></h3>
  {sum_html}{pts_html}{orig}{games_html}
  <div class="src">出處:<a href="{esc(s.get('url'))}" rel="noopener">{esc(s.get('name'))}〈{esc(e.get('title_en'))}〉</a>
    ・版本 {esc(s.get('revid'))}・{esc(s.get('license'))}・查閱 {esc(s.get('accessed'))} {link}</div>
</article>"""


def page(title: str, desc: str, canonical: str, body: str, depth: int = 1, jsonld: dict | None = None) -> str:
    rel = "../" * depth
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} ｜ {SITE_NAME}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)} ｜ 拔拔道場">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<link rel="stylesheet" href="{rel}assets/style.css">
{ld}
</head>
<body>
<header class="site-head"><div class="wrap">
  <div class="brand"><h1><a href="{rel}" style="color:inherit">拔拔道場</a></h1><span class="en">PluckSkill</span>
    <span class="dots"><span class="r"></span><span class="y"></span><span class="b"></span></span></div>
  <p class="crumbs"><a href="{rel}">首頁</a> › {esc(title)}</p>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site-foot"><div class="wrap">
  <p>內容整理自 <a href="https://www.pikminwiki.com/" rel="noopener">Pikipedia</a> 等來源,原文與本站整理文字皆採
    <a href="{LICENSE['url']}" rel="license noopener">{LICENSE['name']}</a>;全部來源見 <a href="{rel}sources/">引用來源總表</a>。</p>
  <p>Pikmin／皮克敏為任天堂商標。本站為粉絲整理的非官方資源,與任天堂無任何關聯。</p>
</div></footer>
</body>
</html>
"""


# ── 各產物 ───────────────────────────────────────────────────────────────
def build_topic_page(t: Topic, entries: List[dict]) -> str:
    url = f"{SITE_BASE}topics/{t.slug}.html"
    cards = "".join(card_html(e) for e in entries) or '<p class="empty">這個主題還沒有條目,下週收集後補上。</p>'
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": f"{t.name}・皮克敏知識",
          "url": url, "numberOfItems": len(entries),
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": e.get("title_zh"),
                               "url": f"{url}#{e['id']}"} for i, e in enumerate(entries)]}
    body = f"""<section class="topic">
  <h2><span class="n">{t.order}</span>{esc(t.name)}</h2>
  <p class="desc">{esc(t.desc)} 共 {len(entries)} 條,預設難度「{esc(t.level)}」。</p>
  <div class="cards">{cards}</div>
</section>"""
    return page(t.name, f"{t.desc} 皮克敏「{t.name}」主題下的知識條目,每條附出處。", url, body, jsonld=ld)


def build_sources_page(entries: List[dict], topics: List[Topic]) -> str:
    tname = {t.slug: t.name for t in topics}
    rows = "".join(
        f"<tr><td>{esc(tname.get(e.get('topic'), e.get('topic')))}</td>"
        f"<td><a href='../topics/{esc(e.get('topic'))}.html#{esc(e['id'])}'>{esc(e.get('title_zh'))}</a></td>"
        f"<td><a href='{esc(e['source'].get('url'))}' rel='noopener'>{esc(e['source'].get('name'))}〈{esc(e.get('title_en'))}〉</a></td>"
        f"<td>{esc(e['source'].get('revid'))}</td><td>{esc(e['source'].get('license'))}</td>"
        f"<td>{esc(e['source'].get('accessed'))}</td>"
        f"<td>{'✓' if e.get('link_ok') else ('⚠' if e.get('link_ok') is False else '–')}</td></tr>"
        for e in entries)
    by_src = {}
    for e in entries:
        by_src[e["source"].get("name")] = by_src.get(e["source"].get("name"), 0) + 1
    summary = "、".join(f"{k} {v} 條" for k, v in by_src.items())
    body = f"""<h2>引用來源總表</h2>
<p class="desc">本站每一條知識的出處。版本欄是來源 wiki 當時的修訂版號(revid),方便對到被引用的那一版。目前:{esc(summary)}。</p>
<table class="sources"><thead><tr><th>主題</th><th>條目</th><th>出處</th><th>版本</th><th>授權</th><th>查閱</th><th>連結</th></tr></thead>
<tbody>{rows}</tbody></table>"""
    return page("引用來源總表", "拔拔道場所有知識條目的引用出處、版本與授權。", f"{SITE_BASE}sources/", body)


def map_html(topics: List[Topic], counts: dict, base: str = "") -> str:
    items = "".join(
        f'<li><a href="{base}topics/{esc(t.slug)}.html"><span class="n">{t.order}</span> '
        f'<span class="t">{esc(t.name)}</span><span class="c">{counts.get(t.slug, 0)} 條</span>'
        f'<span class="d">{esc(t.desc)}</span></a></li>' for t in topics)
    return f'<ul class="map">{items}</ul>'


def inject(html: str, tag: str, content: str) -> str:
    pat = re.compile(rf"(<!-- {tag}:START -->)(.*?)(<!-- {tag}:END -->)", re.S)
    if not pat.search(html):
        raise SystemExit(f"index.html 缺少 <!-- {tag}:START/END --> 標記")
    return pat.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", html)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    topics = parse_topics()
    raw = load_knowledge()
    visible = [e for e in raw if not e.get("hidden")]
    visible.sort(key=sort_key(topics))
    counts = {}
    for e in visible:
        counts[e["topic"]] = counts.get(e["topic"], 0) + 1
    curated = sum(1 for e in visible if e.get("status") == "curated")
    lv_counts = {lv: sum(1 for e in visible if e.get("level") == lv) for lv in LEVELS}
    unknown_topic = [e["title_en"] for e in visible if e["topic"] not in {t.slug for t in topics}]

    print(f"條目 {len(visible)}(已整理 {curated}、待整理 {len(visible) - curated});主題 {len(topics)};難度 {lv_counts}")
    if unknown_topic:
        print(f"⚠ 以下條目的 topic 不在 topics.md:{unknown_topic}")
    if args.check:
        return 0

    # 1) 前端契約
    site = {"site": SITE_NAME, "updated_at": TODAY, "count": len(visible), "license": LICENSE,
            "topics": [{"order": t.order, "slug": t.slug, "name": t.name, "desc": t.desc,
                        "level": t.level, "count": counts.get(t.slug, 0)} for t in topics],
            "entries": [{k: e.get(k) for k in PUBLIC_FIELDS if k in e} for e in visible]}
    SITE_JSON.write_text(json.dumps(site, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # 2) 主題頁 + 來源頁(每次乾淨重建,避免孤兒頁)
    for d in (TOPICS_DIR, SOURCES_DIR):
        shutil.rmtree(d, ignore_errors=True); d.mkdir(parents=True)
    for t in topics:
        (TOPICS_DIR / f"{t.slug}.html").write_text(
            build_topic_page(t, [e for e in visible if e["topic"] == t.slug]), encoding="utf-8")
    (SOURCES_DIR / "index.html").write_text(build_sources_page(visible, topics), encoding="utf-8")

    # 3) sitemap
    urls = [SITE_BASE, f"{SITE_BASE}sources/"] + [f"{SITE_BASE}topics/{t.slug}.html" for t in topics]
    SITEMAP.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                       + "".join(f"  <url><loc>{esc(u)}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls)
                       + "</urlset>\n", encoding="utf-8")

    # 4) 首頁注入
    html = INDEX.read_text(encoding="utf-8")
    html = inject(html, "MAP", map_html(topics, counts))
    html = inject(html, "STATS", f'<p class="stats">最近更新 {TODAY}・共 {len(visible)} 條知識(已中文整理 {curated} 條)・'
                                 f'每週一清晨自動更新・<a href="sources/">引用來源總表</a></p>')
    INDEX.write_text(html, encoding="utf-8")
    print(f"已寫:knowledge.json、topics/×{len(topics)}、sources/index.html、sitemap.xml、index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
