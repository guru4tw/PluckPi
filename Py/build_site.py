#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py — 把 Docs/knowledge.json 正規化成網站資料,並靜態生成子頁
=====================================================================

產物(全部由這支腳本產生,勿手改):
  knowledge.json                     前端契約 {updated_at, count, license, topics[], entries[]}(只含未 hidden 條目)
  zh-hant/topics/{slug}/index.html   每主題一頁(靜態卡片 + ItemList JSON-LD)
  zh-hant/k/{slug}/index.html        每條知識一頁(可分享、可被索引;LearningResource JSON-LD)
  zh-hant/sources/index.html         引用來源總表
  topics/{slug}.html、sources/       舊網址轉址頁(含 #錨點 → 條目頁對應)
  sitemap.xml                        首頁 + 全部子頁,lastmod 取自資料日期
  index.html                         在 MAP / STATS 標記之間注入道場地圖與統計(其餘不動)

卡片 HTML 只有這裡一份(card_html);首頁 JS 不渲染卡片,只做搜尋結果清單。
建站是資料的純函數:不讀系統日期,同一份 knowledge.json 哪天建都得到相同輸出。
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
from typing import Dict, List, Optional

from common import (DOCS, ROOT, SITE_BASE, SITE_JSON, SITE_NAME, LEVELS, Topic,
                    load_knowledge, parse_topics, sort_key)

LANG = "zh-hant"
LANG_DIR = ROOT / LANG
OLD_TOPICS_DIR = ROOT / "topics"      # 舊網址 topics/{slug}.html,現在只放轉址頁
OLD_SOURCES_DIR = ROOT / "sources"
RETIRED_JSON = DOCS / "retired.json"  # 選配:已刪除條目 {slug: 轉去的站內路徑}
SITEMAP = ROOT / "sitemap.xml"
INDEX = ROOT / "index.html"
LICENSE = {"name": "CC BY-SA 4.0", "url": "https://creativecommons.org/licenses/by-sa/4.0/"}

PUBLIC_FIELDS = ("id", "slug", "topic", "level", "title_zh", "title_en", "summary_zh", "key_points_zh",
                 "excerpt_en", "games", "source", "status", "fetched_at", "link_ok", "hidden")


def esc(s) -> str:
    return (str(s if s is not None else "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ── 網址(站內路徑,相對於站根)────────────────────────────────────────────
def topic_path(slug: str) -> str:
    return f"{LANG}/topics/{slug}/"


def entry_path(e: dict) -> str:
    return f"{LANG}/k/{e['slug']}/"


SOURCES_PATH = f"{LANG}/sources/"


def entry_date(e: dict) -> str:
    """條目內容最後變動日:收集或整理,取較新者。"""
    return max(d[:10] for d in (e.get("fetched_at"), e.get("curated_at"), "") if d is not None)


# ── HTML 片段(全站唯一的卡片渲染器)──────────────────────────────────────
def card_html(e: dict, href: Optional[str] = None) -> str:
    """href 給了就讓標題連到條目頁(主題頁用);條目頁自己不連。"""
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
    title = esc(e.get('title_zh') or e.get('title_en'))
    if href:
        title = f'<a href="{esc(href)}">{title}</a>'
    return f"""<article class="card" id="{esc(e['id'])}">
  <div class="head"><span class="lv" data-lv="{esc(e.get('level'))}">{esc(e.get('level'))}</span>{raw}</div>
  <h3>{title}<span class="en">{esc(e.get('title_en'))}</span></h3>
  {sum_html}{pts_html}{orig}{games_html}
  <div class="src">出處:<a href="{esc(s.get('url'))}" rel="noopener">{esc(s.get('name'))}〈{esc(e.get('title_en'))}〉</a>
    ・版本 {esc(s.get('revid'))}・{esc(s.get('license'))}・查閱 {esc(s.get('accessed'))} {link}</div>
</article>"""


def page(title: str, desc: str, path: str, body: str, crumbs: List[tuple] = (),
         jsonld: dict | None = None, og_type: str = "article") -> str:
    """path 是本頁站內路徑(如 zh-hant/k/red-pikmin/),據此算 canonical 與回站根的相對路徑。"""
    rel = "../" * path.count("/")
    canonical = SITE_BASE + path
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    trail = "".join(f' › <a href="{rel}{esc(p)}">{esc(n)}</a>' for n, p in crumbs)
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} ｜ {SITE_NAME}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)} ｜ 拔拔道場">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<link rel="stylesheet" href="{rel}assets/style.css">
{ld}
</head>
<body>
<header class="site-head"><div class="wrap">
  <div class="brand"><h1><a href="{rel}" style="color:inherit">拔拔道場</a></h1><span class="en">PluckPi</span>
    <span class="dots"><span class="r"></span><span class="y"></span><span class="b"></span></span></div>
  <p class="crumbs"><a href="{rel}">首頁</a>{trail} › {esc(title)}</p>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site-foot"><div class="wrap">
  <p>內容整理自 <a href="https://www.pikminwiki.com/" rel="noopener">Pikipedia</a> 等來源,原文與本站整理文字皆採
    <a href="{LICENSE['url']}" rel="license noopener">{LICENSE['name']}</a>;全部來源見 <a href="{rel}{SOURCES_PATH}">引用來源總表</a>。</p>
  <p>Pikmin／皮克敏為任天堂商標。本站為粉絲整理的非官方資源,與任天堂無任何關聯。</p>
</div></footer>
</body>
</html>
"""


def redirect_stub(from_path: str, to_path: str, anchors: Dict[str, str] | None = None) -> str:
    """舊網址轉址頁。GitHub Pages 不能發 301,改用 canonical + JS(保留 #錨點對應)+ meta refresh 後備。"""
    rel = "../" * from_path.count("/")
    target = rel + to_path
    amap = json.dumps({k: rel + v for k, v in (anchors or {}).items()}, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>已搬到新網址 ｜ {SITE_NAME}</title>
<link rel="canonical" href="{esc(SITE_BASE + to_path)}">
<script>(function(){{var m={amap};location.replace(m[location.hash.slice(1)]||"{target}");}})();</script>
<meta http-equiv="refresh" content="0;url={esc(target)}">
</head>
<body><p>本頁已搬到 <a href="{esc(target)}">新網址</a>。</p></body>
</html>
"""


# ── 各產物 ───────────────────────────────────────────────────────────────
def build_topic_page(t: Topic, entries: List[dict]) -> str:
    path = topic_path(t.slug)
    cards = ("".join(card_html(e, href=f"../../k/{e['slug']}/") for e in entries)
             or '<p class="empty">這個主題還沒有條目,下週收集後補上。</p>')
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": f"{t.name}・皮克敏知識",
          "url": SITE_BASE + path, "numberOfItems": len(entries),
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": e.get("title_zh"),
                               "url": SITE_BASE + entry_path(e)} for i, e in enumerate(entries)]}
    body = f"""<section class="topic">
  <h2><span class="n">{t.order}</span>{esc(t.name)}</h2>
  <p class="desc">{esc(t.desc)} 共 {len(entries)} 條,預設難度「{esc(t.level)}」。</p>
  <div class="cards">{cards}</div>
</section>"""
    return page(t.name, f"{t.desc} 皮克敏「{t.name}」主題下的知識條目,每條附出處。", path, body, jsonld=ld)


def build_entry_page(e: dict, t: Topic) -> str:
    s = e.get("source") or {}
    title = e.get("title_zh") or e.get("title_en")
    desc = e.get("summary_zh") or (e.get("excerpt_en") or "")[:120]
    ld = {"@context": "https://schema.org", "@type": "LearningResource", "name": title,
          "alternateName": e.get("title_en"), "inLanguage": "zh-Hant", "educationalLevel": e.get("level"),
          "url": SITE_BASE + entry_path(e), "isBasedOn": s.get("url"), "license": LICENSE["url"],
          "dateModified": entry_date(e)}
    body = f"""<div class="entry">{card_html(e)}
<p class="back"><a href="../../topics/{esc(t.slug)}/">← 回到「{esc(t.name)}」全部條目</a></p></div>"""
    return page(f"{title}({e.get('title_en')})", f"{desc} 出處:{s.get('name')}。", entry_path(e), body,
                crumbs=[(t.name, topic_path(t.slug))], jsonld=ld)


def build_sources_page(entries: List[dict], topics: List[Topic]) -> str:
    tname = {t.slug: t.name for t in topics}
    rows = "".join(
        f"<tr><td>{esc(tname.get(e.get('topic'), e.get('topic')))}</td>"
        f"<td><a href='../k/{esc(e['slug'])}/'>{esc(e.get('title_zh'))}</a></td>"
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
    return page("引用來源總表", "拔拔道場所有知識條目的引用出處、版本與授權。", SOURCES_PATH, body)


def map_html(topics: List[Topic], counts: dict) -> str:
    items = "".join(
        f'<li><a href="{esc(topic_path(t.slug))}"><span class="n">{t.order}</span> '
        f'<span class="t">{esc(t.name)}</span><span class="c">{counts.get(t.slug, 0)} 條</span>'
        f'<span class="d">{esc(t.desc)}</span></a></li>' for t in topics)
    return f'<ul class="map">{items}</ul>'


def inject(html: str, tag: str, content: str) -> str:
    pat = re.compile(rf"(<!-- {tag}:START -->)(.*?)(<!-- {tag}:END -->)", re.S)
    if not pat.search(html):
        raise SystemExit(f"index.html 缺少 <!-- {tag}:START/END --> 標記")
    return pat.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", html)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    topics = parse_topics()
    tby = {t.slug: t for t in topics}
    raw = load_knowledge()
    raw.sort(key=sort_key(topics))
    visible = [e for e in raw if not e.get("hidden")]
    hidden = [e for e in raw if e.get("hidden") and e.get("slug")]
    counts = {}
    for e in visible:
        counts[e["topic"]] = counts.get(e["topic"], 0) + 1
    curated = sum(1 for e in visible if e.get("status") == "curated")
    lv_counts = {lv: sum(1 for e in visible if e.get("level") == lv) for lv in LEVELS}
    unknown_topic = [e["title_en"] for e in visible if e["topic"] not in tby]
    no_slug = [e.get("title_en") or e["id"] for e in visible if not e.get("slug")]
    retired = json.loads(RETIRED_JSON.read_text(encoding="utf-8")) if RETIRED_JSON.exists() else {}
    site_date = max((entry_date(e) for e in visible), default="")

    print(f"條目 {len(visible)}(已整理 {curated}、待整理 {len(visible) - curated});主題 {len(topics)};難度 {lv_counts}")
    if unknown_topic:
        print(f"⚠ 以下條目的 topic 不在 topics.md,略過:{unknown_topic}")
        visible = [e for e in visible if e["topic"] in tby]
    if no_slug:
        print(f"✗ 以下條目缺 slug(條目網址),先跑 collect_pikipedia.py 補上:{no_slug}", file=sys.stderr)
        return 1
    if args.check:
        return 0

    # 1) 前端契約(搜尋用)
    site = {"site": SITE_NAME, "updated_at": site_date, "count": len(visible), "license": LICENSE,
            "topics": [{"order": t.order, "slug": t.slug, "name": t.name, "desc": t.desc,
                        "level": t.level, "count": counts.get(t.slug, 0)} for t in topics],
            "entries": [{k: e.get(k) for k in PUBLIC_FIELDS if k in e} for e in visible]}
    SITE_JSON.write_text(json.dumps(site, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # 2) 子頁(每次乾淨重建,避免孤兒頁)
    for d in (LANG_DIR, OLD_TOPICS_DIR, OLD_SOURCES_DIR):
        shutil.rmtree(d, ignore_errors=True)
    for t in topics:
        write(ROOT / topic_path(t.slug) / "index.html",
              build_topic_page(t, [e for e in visible if e["topic"] == t.slug]))
    for e in visible:
        write(ROOT / entry_path(e) / "index.html", build_entry_page(e, tby[e["topic"]]))
    write(ROOT / SOURCES_PATH / "index.html", build_sources_page(visible, topics))

    # 3) 轉址頁:下架條目 → 所屬主題;retired.json 列的已刪條目 → 指定去處;舊網址 → 新網址
    for e in hidden:
        write(ROOT / entry_path(e) / "index.html", redirect_stub(entry_path(e), topic_path(e["topic"])))
    for slug, to in sorted(retired.items()):
        p = f"{LANG}/k/{slug}/"
        write(ROOT / p / "index.html", redirect_stub(p, to))
    for t in topics:
        old = f"topics/{t.slug}.html"
        anchors = {e["id"]: entry_path(e) for e in visible if e["topic"] == t.slug}
        write(ROOT / old, redirect_stub(old, topic_path(t.slug), anchors))
    write(OLD_SOURCES_DIR / "index.html", redirect_stub("sources/index.html", SOURCES_PATH))

    # 4) sitemap(lastmod 取資料日期,不取建站日)
    tdate = {t.slug: max((entry_date(e) for e in visible if e["topic"] == t.slug), default=site_date) for t in topics}
    urls = ([("", site_date), (SOURCES_PATH, site_date)]
            + [(topic_path(t.slug), tdate[t.slug]) for t in topics]
            + [(entry_path(e), entry_date(e)) for e in visible])
    SITEMAP.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                       + "".join(f"  <url><loc>{esc(SITE_BASE + p)}</loc>"
                                 + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>\n" for p, d in urls)
                       + "</urlset>\n", encoding="utf-8")

    # 5) 首頁注入
    html = INDEX.read_text(encoding="utf-8")
    html = inject(html, "MAP", map_html(topics, counts))
    html = inject(html, "STATS", f'<p class="stats">最近更新 {site_date}・共 {len(visible)} 條知識(已中文整理 {curated} 條)・'
                                 f'每週一清晨自動更新・<a href="{SOURCES_PATH}">引用來源總表</a></p>')
    INDEX.write_text(html, encoding="utf-8")
    print(f"已寫:knowledge.json、{LANG}/topics/×{len(topics)}、{LANG}/k/×{len(visible)}、{SOURCES_PATH}、"
          f"轉址頁×{len(topics) + 1 + len(hidden) + len(retired)}、sitemap.xml、index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
