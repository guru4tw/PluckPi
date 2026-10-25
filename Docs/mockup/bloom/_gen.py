#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_gen.py — 階段 4 草稿產生器:讀 Docs/topics.md,產出首頁、7 個大綱頁、24 個子分類頁與 1 個範例條目頁。

只給草稿用;定案後的版面會搬進 Py/build_site.py。全部是靜態 HTML,關掉 JS 網站地圖照樣能用;
JS 只負責首頁走路體驗(walk.js)與讀完種花(progress.js)。

用法:python3 Docs/mockup/bloom/_gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "Py"))
from common import Category, QueueItem, Topic, parse_categories  # noqa: E402

IMG = "../../../assets/img"
COLORS = ["coral", "lilac", "sun", "mint"]           # 大分類的花色依序輪替
SAMPLE = "step-permission-ios"                        # 目前唯一寫好的範例條目


def esc(s) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def flower(c: Category) -> str:
    return f"{IMG}/flower-{COLORS[(c.order - 1) % len(COLORS)]}.svg"


def page(title: str, body: str, crumbs: str = "", scripts: tuple = ("progress.js",)) -> str:
    js = "".join(f'<script src="{s}" defer></script>' for s in scripts)
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<link rel="stylesheet" href="bloom.css">{js}
</head>
<body><div class="wrap">
<header class="head"><a class="brand" href="index.html"><img src="{IMG}/mascot-bud.svg" alt=""><b>拔拔道場</b><span>Pikmin Bloom 玩法筆記</span></a>{crumbs}</header>
{body}
<footer class="foot">非官方粉絲網站,與任天堂、Niantic、Scopely 無關。Pikmin Bloom 遊戲 © Niantic / Scopely;皮克敏角色、美術、音樂 © Nintendo。
本站文字與插畫採 CC BY-SA 4.0,每條知識附出處。(草稿,不會上站)</footer>
</div></body>
</html>
"""


def chips(cats) -> str:
    return '<nav class="chips" aria-label="大分類">' + "".join(
        f'<a href="#{c.slug}"><i style="background:var(--{COLORS[(c.order - 1) % 4]})"></i>{c.order} {esc(c.name)}</a>'
        for c in cats) + "</nav>"


def subs_html(c: Category) -> str:
    return '<ul class="subs">' + "".join(
        f'<li><a href="topic-{t.slug}.html" data-topic="{t.slug}"><img src="{flower(c)}" alt="已讀">{esc(t.name)}</a></li>'
        for t in c.topics) + "</ul>"


def build_index(cats) -> str:
    field = f"""<section class="field" id="field" data-img="{IMG}" aria-label="走路小遊戲:在這裡滑動手指">
  <div class="hud"><span class="pill">步數 <b data-steps>0</b></span><span class="bar" aria-hidden="true"><i></i></span>
    <img src="{IMG}/seedling.svg" alt="" width="22"></div>
  <p class="hint">用手指在這裡走走看</p>
  <button class="walk-btn" type="button">走一段</button>
</section>"""
    cards = "".join(f"""<li class="cat" id="{c.slug}">
  <h3><img src="{flower(c)}" alt=""><a href="cat-{c.slug}.html"><span class="n">{c.order}</span> {esc(c.name)}</a></h3>
  <p>{esc(c.outline)}</p>
  {subs_html(c)}
  <a class="more" href="cat-{c.slug}.html">看大綱與閱讀順序 →</a> <small data-count-read="{','.join(t.slug for t in c.topics)}"></small>
</li>""" for c in cats)
    body = f"""{chips(cats)}
{field}
<h2 class="sec">道場地圖</h2>
<ul class="map">{cards}</ul>"""
    return page("拔拔道場 ｜ Pikmin Bloom 玩法筆記", body, scripts=("walk.js", "progress.js"))


def build_category(c: Category) -> str:
    items = "".join(f"""<li><span class="no">{esc(t.number)}</span><a href="topic-{t.slug}.html" data-topic="{t.slug}">{esc(t.name)}</a>
  <span class="c">{len(t.items)} 題</span><span class="d">{esc(t.desc)}</span></li>""" for t in c.topics)
    body = f"""<h1><img src="{flower(c)}" alt="">{esc(c.name)}</h1>
<p class="lead">{esc(c.outline)}</p>
<h2 class="sec">建議閱讀順序</h2>
<ol class="order">{items}</ol>"""
    crumbs = f'<p class="crumbs"><a href="index.html">道場地圖</a> › {esc(c.name)}</p>'
    return page(f"{c.name} ｜ 拔拔道場", body, crumbs)


def q_html(it: QueueItem) -> str:
    title = (f'<a href="entry-{it.slug}.html">{esc(it.title_zh)}</a>' if it.slug == SAMPLE
             else f'<span class="todo">{esc(it.title_zh)}</span>')
    unv = '<span class="tag unv">待證</span>' if it.status else ""
    todo = "" if it.slug == SAMPLE else '<span class="tag">還沒寫</span>'
    return f'<li>{title}<span class="tag lv">{esc(it.level)}</span>{unv}{todo}</li>'


def build_topic(c: Category, t: Topic) -> str:
    body = f"""<h1><img src="{flower(c)}" alt="">{esc(t.name)}</h1>
<p class="lead">{esc(t.desc)}</p>
<ul class="qs">{''.join(q_html(it) for it in t.items)}</ul>
<div class="done" data-done="{t.slug}"><button class="btn" type="button" aria-pressed="false">讀完了,種一朵花</button>
  <img src="{flower(c)}" alt=""></div>"""
    crumbs = (f'<p class="crumbs"><a href="index.html">道場地圖</a> › <a href="cat-{c.slug}.html">{esc(c.name)}</a>'
              f' › {esc(t.name)}</p>')
    return page(f"{t.name} ｜ 拔拔道場", body, crumbs)


def build_sample(c: Category, t: Topic) -> str:
    """範例條目。內容依官方說明中心(A,查閱 2026-10-25);iOS 繁中選單名稱尚未對過,先用英文原文。"""
    body = """<h1>iPhone 的計步權限要怎麼開?</h1>
<p class="lead"><span class="tag lv">入門</span> <span class="tag a">A 官方</span></p>
<article class="card">
  <h2>答案</h2>
  <ul class="facts">
    <li>Pikmin Bloom 從 iPhone 的「健康」App 讀取步數。</li>
    <li>「健康」App 沒記到的步數,遊戲也不會算。</li>
    <li>遊戲同步步數最多會慢幾個小時。</li>
  </ul>
  <h2>怎麼做</h2>
  <ol>
    <li>打開 <code>Settings › Health › Data Access &amp; Devices › Pikmin Bloom</code>,打開「步數」。</li>
    <li>打開 <code>Settings › Privacy &amp; Security › Location Services › Pikmin Bloom</code>,選「永遠」。</li>
    <li>打開 <code>Settings › Privacy &amp; Security › Motion &amp; Fitness</code>,打開「健身追蹤」。</li>
    <li>關掉「低耗電模式」。</li>
    <li>步數還是沒算,就重新開機。</li>
  </ol>
  <div class="shot">這裡放 iOS 設定頁截圖(系統截圖,C 方案;不含遊戲畫面)</div>
  <h2>例外</h2>
  <ul class="facts"><li>使用輪椅模式的玩家,看官方另一篇說明。</li></ul>
  <h2>詞彙</h2>
  <p><code>健康</code> iPhone 內建、記錄步數的 App</p>
  <p class="src">出處:<a href="https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/2861-my-steps-aren-t-being-counted-correctly-ios/">Pikmin Bloom 說明中心〈My steps aren't being counted correctly (iOS)〉</a>
    ・A 官方・查閱 2026-10-25<br>iOS 繁中選單名稱待確認,目前照官方英文原文。</p>
</article>"""
    crumbs = (f'<p class="crumbs"><a href="index.html">道場地圖</a> › <a href="cat-{c.slug}.html">{esc(c.name)}</a>'
              f' › <a href="topic-{t.slug}.html">{esc(t.name)}</a></p>')
    return page("iPhone 的計步權限要怎麼開? ｜ 拔拔道場", body, crumbs)


def main() -> int:
    cats = parse_categories()
    out = {"index.html": build_index(cats)}
    for c in cats:
        out[f"cat-{c.slug}.html"] = build_category(c)
        for t in c.topics:
            out[f"topic-{t.slug}.html"] = build_topic(c, t)
            if any(it.slug == SAMPLE for it in t.items):
                out[f"entry-{SAMPLE}.html"] = build_sample(c, t)
    for name in HERE.glob("*.html"):
        if name.name != "art-sheet.html" and name.name not in out:
            name.unlink()
    for name, html in out.items():
        (HERE / name).write_text(html, encoding="utf-8")
    print(f"寫了 {len(out)} 頁到 {HERE.relative_to(HERE.parents[2])}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
