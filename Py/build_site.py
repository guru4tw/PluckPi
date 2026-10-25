#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py — 把 Docs/topics.md + Docs/knowledge.json 靜態生成整個網站
=====================================================================

產物(全部由這支腳本產生,勿手改):
  index.html                         首頁 = 走路小遊戲 + 道場地圖(全部大分類、大綱、子分類)
  zh-hant/c/{大分類}/index.html       大綱頁:這分類在講什麼、子分類與建議閱讀順序
  zh-hant/topics/{子分類}/index.html  子分類頁:玩家問題清單 +「讀完了,種一朵花」
  zh-hant/k/{條目}/index.html         條目頁:玩家問題 → STE100 答案 → 出處
  zh-hant/sources/index.html         引用來源總表
  knowledge.json                     前端與外部用的資料契約(只含已寫好、未 hidden 的條目)
  轉址頁                              Docs/retired.json 列的舊網址(主機版時期的條目與主題)→ 新去處
  sitemap.xml                        lastmod 取資料日期

脈絡(分類、問題、難度、待證、期限)全部來自 Docs/topics.md;knowledge.json 只放答案與出處。
頁面是純 HTML,關掉 JS 照樣能讀;JS 只負責首頁走路小遊戲與讀完種花(assets/js/)。
建站是資料的純函數:不讀系統日期,同一份資料哪天建都得到相同輸出。

用法:
    python3 Py/build_site.py
    python3 Py/build_site.py --check   # 只檢查、印統計,不寫檔
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from typing import Dict, List, Optional

from common import (DOCS, ROOT, SITE_BASE, SITE_JSON, SITE_NAME, Category, QueueItem, Topic,
                    load_knowledge, parse_categories)

LANG = "zh-hant"
LANG_DIR = ROOT / LANG
OLD_TOPICS_DIR = ROOT / "topics"      # 最早期網址 topics/{slug}.html,只放轉址頁
OLD_SOURCES_DIR = ROOT / "sources"
RETIRED_JSON = DOCS / "retired.json"  # {"entries": {slug: 站內路徑}, "topics": {slug: 站內路徑}}
SITEMAP = ROOT / "sitemap.xml"
INDEX = ROOT / "index.html"
LICENSE = {"name": "CC BY-SA 4.0", "url": "https://creativecommons.org/licenses/by-sa/4.0/"}
COLORS = ("coral", "lilac", "sun", "mint")     # 大分類的花色依序輪替(調色盤見 Docs/images.md)
CONTENT = ("facts_zh", "steps_zh", "exceptions_zh", "terms_zh", "sources")
PUBLIC_FIELDS = ("slug", "topic", "level", "title_zh", "unverified", "expires", "facts_zh", "steps_zh",
                 "exceptions_zh", "terms_zh", "sources", "link_ok", "curated_at")
GRADE_NAME = {"A": "A 官方", "B": "B Pikipedia"}


def esc(s) -> str:
    return (str(s if s is not None else "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ── 網址(站內路徑,相對於站根)────────────────────────────────────────────
def cat_path(slug: str) -> str:
    return f"{LANG}/c/{slug}/"


def topic_path(slug: str) -> str:
    return f"{LANG}/topics/{slug}/"


def entry_path(slug: str) -> str:
    return f"{LANG}/k/{slug}/"


SOURCES_PATH = f"{LANG}/sources/"


def flower(c: Category) -> str:
    return f"assets/img/flower-{COLORS[(c.order - 1) % len(COLORS)]}.svg"


def entry_date(e: dict) -> str:
    return (e.get("curated_at") or "")[:10]


# ── 資料:topics.md 脈絡 + knowledge.json 答案 ───────────────────────────
def merge(item: QueueItem, e: dict) -> dict:
    """條目頁要的資料:脈絡以 topics.md 為準,答案與出處取 knowledge.json。"""
    return {"slug": item.slug, "topic": item.topic, "level": item.level, "title_zh": item.title_zh,
            "unverified": item.status == "待證", "expires": item.expires, "prereq": item.prereq,
            **{k: e.get(k) for k in CONTENT}, "link_ok": e.get("link_ok"), "curated_at": e.get("curated_at")}


def written(cats: List[Category], raw: List[dict]) -> Dict[str, dict]:
    by_slug = {e.get("slug"): e for e in raw}
    out = {}
    for c in cats:
        for t in c.topics:
            for it in t.items:
                e = by_slug.get(it.slug)
                if e and e.get("facts_zh") and not e.get("hidden"):
                    out[it.slug] = merge(it, e)
    return out


# ── 版面 ──────────────────────────────────────────────────────────────────
def page(title: str, desc: str, path: str, body: str, crumbs: List[tuple] = (), scripts: tuple = (),
         jsonld: Optional[dict] = None, home: bool = False) -> str:
    """path 是本頁站內路徑(首頁為空字串),據此算 canonical 與回站根的相對路徑。"""
    rel = "../" * path.count("/")
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    js = "".join(f'<script src="{rel}assets/js/{s}" defer></script>' for s in scripts)
    trail = ""
    if crumbs:
        trail = ('<p class="crumbs"><a href="' + (rel or "./") + '">道場地圖</a>'
                 + "".join(f' › <a href="{rel}{esc(p)}">{esc(n)}</a>' for n, p in crumbs[:-1])
                 + f" › {esc(crumbs[-1][0])}</p>")
    full = SITE_NAME if home else f"{title} ｜ 拔拔道場"
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(full)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(SITE_BASE + path)}">
<meta property="og:type" content="{'website' if home else 'article'}">
<meta property="og:title" content="{esc(full)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(SITE_BASE + path)}">
<link rel="icon" href="{rel}assets/img/mascot-bud.svg" type="image/svg+xml">
<link rel="stylesheet" href="{rel}assets/style.css">{js}
{ld}
</head>
<body><div class="wrap">
<header class="head"><a class="brand" href="{rel or './'}"><img src="{rel}assets/img/mascot-bud.svg" alt=""><b>拔拔道場</b><span>Pikmin Bloom 玩法筆記</span></a>{trail}</header>
<main>
{body}
</main>
<footer class="foot">
  <p>非官方粉絲網站,與任天堂、Niantic、Scopely 無關。Pikmin Bloom 遊戲 © Niantic / Scopely;皮克敏角色、美術、音樂 © Nintendo。</p>
  <p>本站文字與插畫採 <a href="{LICENSE['url']}" rel="license noopener">{LICENSE['name']}</a>;每條知識附出處,全部來源見 <a href="{rel}{SOURCES_PATH}">引用來源總表</a>。</p>
</footer>
</div></body>
</html>
"""


def subs_html(c: Category, rel: str) -> str:
    return '<ul class="subs">' + "".join(
        f'<li><a href="{rel}{topic_path(t.slug)}" data-topic="{t.slug}"><img src="{rel}{flower(c)}" alt="已讀">'
        f'{esc(t.name)}</a></li>' for t in c.topics) + "</ul>"


def build_index(cats: List[Category], done: Dict[str, dict], total: int, site_date: str) -> str:
    chips = '<nav class="chips" aria-label="大分類">' + "".join(
        f'<a href="#{c.slug}"><i style="background:var(--{COLORS[(c.order - 1) % 4]})"></i>{c.order} {esc(c.name)}</a>'
        for c in cats) + "</nav>"
    field = """<section class="field" id="field" data-img="assets/img" aria-label="走路小遊戲:在這裡滑動手指">
  <div class="hud"><span class="pill">步數 <b data-steps>0</b></span><span class="bar" aria-hidden="true"><i></i></span>
    <img src="assets/img/seedling.svg" alt="" width="22"></div>
  <p class="hint">用手指在這裡走走看</p>
  <button class="walk-btn" type="button">走一段</button>
</section>"""
    cards = "".join(f"""<li class="cat" id="{c.slug}">
  <h3><img src="{flower(c)}" alt=""><a href="{cat_path(c.slug)}"><span class="n">{c.order}</span> {esc(c.name)}</a></h3>
  <p>{esc(c.outline)}</p>
  {subs_html(c, '')}
  <a class="more" href="{cat_path(c.slug)}">看大綱與閱讀順序 →</a> <small data-count-read="{','.join(t.slug for t in c.topics)}"></small>
</li>""" for c in cats)
    body = f"""{chips}
{field}
<h2 class="sec">道場地圖</h2>
<ul class="map">{cards}</ul>
<p class="stats">已回答 {len(done)}/{total} 個玩家問題・最近更新 {esc(site_date)}・<a href="{SOURCES_PATH}">引用來源總表</a></p>"""
    desc = "Pikmin Bloom 玩法筆記:走路、花苗、飾品皮克敏、蘑菇、明信片。每個玩家問題用一句一件事的中文回答,每條附出處。"
    return page("首頁", desc, "", body, scripts=("walk.js", "progress.js"), home=True,
                jsonld={"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": SITE_BASE})


def build_category(c: Category, done: Dict[str, dict]) -> str:
    path = cat_path(c.slug)
    rel = "../" * path.count("/")
    rows = "".join(f"""<li><span class="no">{esc(t.number)}</span><a href="{rel}{topic_path(t.slug)}" data-topic="{t.slug}">{esc(t.name)}</a>
  <span class="c">{sum(it.slug in done for it in t.items)}/{len(t.items)} 題</span><span class="d">{esc(t.desc)}</span></li>""" for t in c.topics)
    body = f"""<h1><img src="{rel}{flower(c)}" alt="">{esc(c.name)}</h1>
<p class="lead">{esc(c.outline)}</p>
<h2 class="sec">建議閱讀順序</h2>
<ol class="order">{rows}</ol>"""
    return page(c.name, c.outline, path, body, crumbs=[(c.name, path)], scripts=("progress.js",))


def q_html(it: QueueItem, done: Dict[str, dict], rel: str) -> str:
    title = (f'<a href="{rel}{entry_path(it.slug)}">{esc(it.title_zh)}</a>' if it.slug in done
             else f'<span class="todo">{esc(it.title_zh)}</span><span class="tag">還沒寫</span>')
    unv = '<span class="tag unv">待證</span>' if it.status else ""
    return f'<li>{title}<span class="tag lv">{esc(it.level)}</span>{unv}</li>'


def build_topic(c: Category, t: Topic, done: Dict[str, dict]) -> str:
    path = topic_path(t.slug)
    rel = "../" * path.count("/")
    written_items = [it for it in t.items if it.slug in done]
    body = f"""<h1><img src="{rel}{flower(c)}" alt="">{esc(t.name)}</h1>
<p class="lead">{esc(t.desc)}</p>
<ul class="qs">{''.join(q_html(it, done, rel) for it in t.items)}</ul>
<div class="done" data-done="{t.slug}"><button class="btn" type="button" aria-pressed="false">讀完了,種一朵花</button>
  <img src="{rel}{flower(c)}" alt=""></div>"""
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": t.name, "url": SITE_BASE + path,
          "numberOfItems": len(written_items),
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": it.title_zh,
                               "url": SITE_BASE + entry_path(it.slug)} for i, it in enumerate(written_items)]}
    return page(t.name, t.desc, path, body, crumbs=[(c.name, cat_path(c.slug)), (t.name, path)],
                scripts=("progress.js",), jsonld=ld)


def source_line(s: dict) -> str:
    grade = GRADE_NAME.get(s.get("grade"), s.get("grade"))
    title = f"〈{esc(s['title'])}〉" if s.get("title") else ""
    extra = f"・版本 {esc(s['revid'])}・{esc(s.get('license'))}" if s.get("revid") else ""
    return (f'<li><a href="{esc(s.get("url"))}" rel="noopener">{esc(s.get("name"))}{title}</a>'
            f'<span class="tag a">{esc(grade)}</span>{extra}・查閱 {esc(s.get("accessed"))}</li>')


def build_entry(c: Category, t: Topic, e: dict) -> str:
    path = entry_path(e["slug"])
    li = lambda rows: "".join(f"<li>{esc(r)}</li>" for r in rows)
    parts = [f'<h2>答案</h2><ul class="facts">{li(e["facts_zh"])}</ul>']
    if e.get("steps_zh"):
        parts.append(f'<h2>怎麼做</h2><ol>{li(e["steps_zh"])}</ol>')
    if e.get("exceptions_zh"):
        parts.append(f'<h2>例外</h2><ul class="facts">{li(e["exceptions_zh"])}</ul>')
    if e.get("terms_zh"):
        parts.append('<h2>詞彙</h2><dl class="terms">' + "".join(
            f'<dt>{esc(x["term"])}</dt><dd>{esc(x["def"])}</dd>' for x in e["terms_zh"]) + "</dl>")
    grades = sorted({s.get("grade") for s in e.get("sources") or []})
    tags = (f'<span class="tag lv">{esc(e["level"])}</span>'
            + "".join(f'<span class="tag a">{esc(GRADE_NAME.get(g, g))}</span>' for g in grades)
            + ('<span class="tag unv">待證</span>' if e.get("unverified") else ""))
    notes = []
    if e.get("unverified"):
        notes.append("「待證」:這一條只有一個來源,或來源說法不一致。")
    if e.get("expires"):
        notes.append(f"活動資訊有效到 {esc(e['expires'])}。")
    if e.get("link_ok") is False:
        notes.append("有出處連結打不開,待確認。")
    body = f"""<h1>{esc(e['title_zh'])}</h1>
<p class="lead">{tags}</p>
<article class="card">
  {''.join(parts)}
  <div class="src"><h2>出處</h2><ul class="srcs">{''.join(source_line(s) for s in e.get('sources') or [])}</ul>
  {''.join(f'<p>{n}</p>' for n in notes)}</div>
</article>"""
    ld = {"@context": "https://schema.org", "@type": "LearningResource", "name": e["title_zh"],
          "inLanguage": "zh-Hant", "educationalLevel": e["level"], "url": SITE_BASE + path,
          "isBasedOn": [s.get("url") for s in e.get("sources") or []], "license": LICENSE["url"],
          "dateModified": entry_date(e)}
    return page(e["title_zh"], "".join(e["facts_zh"])[:120], path, body,
                crumbs=[(c.name, cat_path(c.slug)), (t.name, topic_path(t.slug)), (e["title_zh"], path)], jsonld=ld)


def build_sources(cats: List[Category], done: Dict[str, dict]) -> str:
    rows = []
    for c in cats:
        for t in c.topics:
            for it in t.items:
                e = done.get(it.slug)
                if not e:
                    continue
                for s in e.get("sources") or []:
                    rows.append(f"<tr><td>{esc(t.name)}</td><td><a href='../k/{esc(it.slug)}/'>{esc(it.title_zh)}</a></td>"
                                f"<td><a href='{esc(s.get('url'))}' rel='noopener'>{esc(s.get('name'))}"
                                f"{'〈' + esc(s['title']) + '〉' if s.get('title') else ''}</a></td>"
                                f"<td>{esc(s.get('grade'))}</td><td>{esc(s.get('revid') or '–')}</td>"
                                f"<td>{esc(s.get('license') or '–')}</td><td>{esc(s.get('accessed'))}</td></tr>")
    body = f"""<h1>引用來源總表</h1>
<p class="lead">每一條知識的出處。等級 A 是官方(官網、說明中心、任天堂),B 是 Pikipedia(CC BY-SA 4.0,版本欄是被引用的修訂版號)。</p>
<div class="table"><table><thead><tr><th>子分類</th><th>問題</th><th>出處</th><th>等級</th><th>版本</th><th>授權</th><th>查閱</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""
    return page("引用來源總表", "拔拔道場所有條目的引用出處、等級、版本與授權。", SOURCES_PATH, body,
                crumbs=[("引用來源總表", SOURCES_PATH)])


def redirect_stub(from_path: str, to_path: str) -> str:
    """舊網址轉址頁。GitHub Pages 不能發 301,改用 canonical + JS + meta refresh 後備。"""
    rel = "../" * from_path.count("/")
    target = rel + to_path or "./"
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>已搬到新網址 ｜ {SITE_NAME}</title>
<link rel="canonical" href="{esc(SITE_BASE + to_path)}">
<script>location.replace("{target}");</script>
<meta http-equiv="refresh" content="0;url={esc(target)}">
</head>
<body><p>本頁已搬到 <a href="{esc(target)}">新網址</a>。</p></body>
</html>
"""


def write(path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    cats = parse_categories()
    topics = [t for c in cats for t in c.topics]
    items = [it for t in topics for it in t.items]
    raw = load_knowledge()
    done = written(cats, raw)
    retired = json.loads(RETIRED_JSON.read_text(encoding="utf-8")) if RETIRED_JSON.exists() else {}
    r_entries, r_topics = retired.get("entries", {}), retired.get("topics", {})
    site_date = max((entry_date(e) for e in done.values()), default="")

    known = {it.slug for it in items}
    orphans = [e.get("slug") or e.get("id") for e in raw if e.get("slug") not in known and e.get("slug") not in r_entries]
    clash = ({it.slug for it in items} & set(r_entries)) | ({t.slug for t in topics} & set(r_topics))
    print(f"大分類 {len(cats)}、子分類 {len(topics)}、問題 {len(items)};已回答 {len(done)}"
          f"(待證 {sum(e['unverified'] for e in done.values())});轉址 條目 {len(r_entries)}、主題 {len(r_topics)}")
    if orphans:
        print(f"⚠ knowledge.json 裡這些條目不在 topics.md、也沒寫進 retired.json,不會上站:{orphans}")
    if clash:
        print(f"✗ retired.json 的舊網址和現有網址撞名:{sorted(clash)}", file=sys.stderr)
        return 1
    if args.check:
        return 0

    # 1) 資料契約
    site = {"site": SITE_NAME, "updated_at": site_date, "count": len(done), "questions": len(items),
            "license": LICENSE,
            "categories": [{"order": c.order, "slug": c.slug, "name": c.name, "outline": c.outline,
                            "topics": [{"number": t.number, "slug": t.slug, "name": t.name, "desc": t.desc,
                                        "questions": len(t.items), "count": sum(i.slug in done for i in t.items)}
                                       for t in c.topics]} for c in cats],
            "entries": [{k: done[it.slug].get(k) for k in PUBLIC_FIELDS} for it in items if it.slug in done]}
    SITE_JSON.write_text(json.dumps(site, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # 2) 頁面(每次乾淨重建,避免孤兒頁)
    for d in (LANG_DIR, OLD_TOPICS_DIR, OLD_SOURCES_DIR):
        shutil.rmtree(d, ignore_errors=True)
    write(INDEX, build_index(cats, done, len(items), site_date))
    for c in cats:
        write(ROOT / cat_path(c.slug) / "index.html", build_category(c, done))
        for t in c.topics:
            write(ROOT / topic_path(t.slug) / "index.html", build_topic(c, t, done))
            for it in t.items:
                if it.slug in done:
                    write(ROOT / entry_path(it.slug) / "index.html", build_entry(c, t, done[it.slug]))
    write(ROOT / SOURCES_PATH / "index.html", build_sources(cats, done))

    # 3) 轉址頁:舊條目、舊主題、最早期的 topics/*.html 與 sources/
    for slug, to in sorted(r_entries.items()):
        write(ROOT / entry_path(slug) / "index.html", redirect_stub(entry_path(slug), to))
    for slug, to in sorted(r_topics.items()):
        write(ROOT / topic_path(slug) / "index.html", redirect_stub(topic_path(slug), to))
        write(OLD_TOPICS_DIR / f"{slug}.html", redirect_stub(f"topics/{slug}.html", to))
    write(OLD_SOURCES_DIR / "index.html", redirect_stub("sources/index.html", SOURCES_PATH))

    # 4) sitemap(lastmod 取資料日期,不取建站日)
    urls = ([("", site_date), (SOURCES_PATH, site_date)]
            + [(cat_path(c.slug), site_date) for c in cats]
            + [(topic_path(t.slug), site_date) for t in topics]
            + [(entry_path(s), entry_date(e)) for s, e in done.items()])
    SITEMAP.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                       + "".join(f"  <url><loc>{esc(SITE_BASE + p)}</loc>"
                                 + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>\n" for p, d in urls)
                       + "</urlset>\n", encoding="utf-8")
    print(f"已寫:index.html、大綱頁×{len(cats)}、子分類頁×{len(topics)}、條目頁×{len(done)}、來源總表、"
          f"轉址頁×{len(r_entries) + 2 * len(r_topics) + 1}、knowledge.json、sitemap.xml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
