#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collect_pikipedia.py — 從 Pikipedia(CC BY-SA 4.0)收集皮克敏知識原料
======================================================================

讀 Docs/topics.md 的收集佇列,挑出尚未收集的頁面,經 MediaWiki API 一次抓:
  首段純文字摘要(extracts)、正式網址與最新修訂版號(info)、分類(categories → 推出適用作品)
然後合併寫入 Docs/knowledge.json。

合併規則(idempotent,重跑不會洗掉人工/Claude 整理):
  - 新頁面  → 新增一筆,status=raw
  - 已有頁面 → 只更新「原料欄位」(title_en / excerpt_en / games / source / fetched_at)
              與「脈絡欄位」(topic / level / title_zh,以 topics.md 為準);
              「整理欄位」(summary_zh / key_points_zh / status / curated_*)一律保留
  - 佇列裡找不到的頁面(missing)→ 印警告,不寫入

用法:
    python3 Py/collect_pikipedia.py                 # 最多收 20 個新頁面
    python3 Py/collect_pikipedia.py --limit 50
    python3 Py/collect_pikipedia.py --refresh       # 連已收集的也重抓(更新原文與版號)
    python3 Py/collect_pikipedia.py --dry-run       # 只印不寫

零第三方依賴(urllib),本機 Python 3.9 與 Actions 都能跑。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from typing import Dict, List

from common import (KNOWLEDGE_JSON, TODAY, UA, QueueItem, load_knowledge, norm_title,
                    parse_topics, queue_items, save_knowledge, sort_key)

API = "https://www.pikminwiki.com/api.php"
DELAY = 1.5          # robots.txt Crawl-delay: 1,保守一點
BATCH = 10           # 一次查幾個頁名(TextExtracts exintro 上限 20)
SOURCE = {
    "key": "pikipedia",
    "name": "Pikipedia",
    "license": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
}
# 分類名 → 顯示用作品名。頁面掛了哪些作品分類,就代表這條知識適用哪些作品。
GAME_CATS = {
    "Pikmin_1": "Pikmin 1", "Pikmin_2": "Pikmin 2", "Pikmin_3": "Pikmin 3", "Pikmin_4": "Pikmin 4",
    "Hey!_Pikmin": "Hey! Pikmin", "Pikmin_Bloom": "Pikmin Bloom",
}


def api_get(params: dict) -> dict:
    params = {**params, "format": "json", "formatversion": "2"}
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_pages(titles: List[str]) -> Dict[str, dict]:
    """一批頁名 → {請求時的頁名: page dict}。處理 normalized / redirects 對回原請求名。"""
    data = api_get({
        "action": "query", "titles": "|".join(titles), "redirects": 1,
        "prop": "extracts|info|categories",
        "exintro": 1, "explaintext": 1, "exlimit": "max",
        "inprop": "url", "cllimit": "max",
    })
    q = data.get("query", {})
    # 正規化 + 轉址鏈:請求名 → 最終頁名
    alias: Dict[str, str] = {}
    for m in q.get("normalized", []) + q.get("redirects", []):
        alias[m["from"]] = m["to"]
    def final(t: str) -> str:
        seen = set()
        while t in alias and t not in seen:
            seen.add(t); t = alias[t]
        return t
    by_title = {p["title"]: p for p in q.get("pages", [])}
    return {t: by_title.get(final(t), {"missing": True, "title": t}) for t in titles}


def to_entry(item: QueueItem, page: dict, old: dict | None) -> dict:
    cats = [c["title"].split(":", 1)[-1].replace(" ", "_") for c in page.get("categories", [])]
    games = [g for k, g in GAME_CATS.items() if k in cats]
    entry = dict(old or {})
    entry.update({
        "id": f"pikipedia-{page['pageid']}",
        # 脈絡欄位:以 topics.md 為準
        "topic": item.topic, "level": item.level, "title_zh": item.title_zh,
        "queue_title": item.title,   # topics.md 裡的請求頁名(可能與 title_en 不同,例如轉址)
        # 原料欄位:以來源為準
        "title_en": page["title"],
        "excerpt_en": (page.get("extract") or "").strip(),
        "games": games,
        "source": {**SOURCE, "url": page.get("canonicalurl") or page.get("fullurl"),
                   "revid": page.get("lastrevid"), "accessed": TODAY},
        "fetched_at": TODAY,
    })
    # 整理欄位:新條目給預設值;舊條目保留原值
    entry.setdefault("summary_zh", "")
    entry.setdefault("key_points_zh", [])
    entry.setdefault("status", "raw")
    entry.setdefault("hidden", False)
    if old and old.get("source", {}).get("revid") not in (None, page.get("lastrevid")):
        entry["source_changed_at"] = TODAY   # 原文有新版本,提醒整理內容可能需要複核
    return entry


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=20, help="本次最多收幾個新頁面(預設 20)")
    ap.add_argument("--refresh", action="store_true", help="已收集的頁面也重抓")
    ap.add_argument("--dry-run", action="store_true", help="只印結果不寫檔")
    args = ap.parse_args()

    topics = parse_topics()
    queue = queue_items(topics)
    existing = load_knowledge()
    by_title = {norm_title(e.get("queue_title") or e.get("title_en", "")): e for e in existing}
    by_title.update({norm_title(e.get("title_en", "")): e for e in existing})
    by_id = {e["id"]: e for e in existing}

    new_items = [it for it in queue if norm_title(it.title) not in by_title][: args.limit]
    old_items = [it for it in queue if norm_title(it.title) in by_title] if args.refresh else []
    todo = new_items + old_items
    print(f"佇列 {len(queue)} 頁;已收集 {len(existing)};本次抓新 {len(new_items)}、重抓 {len(old_items)}")
    if not todo:
        print("沒有要抓的頁面,結束。")
        return 0

    added = updated = missing = 0
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        try:
            pages = fetch_pages([it.title for it in chunk])
        except Exception as ex:  # 單批失敗不中斷整體
            print(f"  ✗ 批次失敗({chunk[0].title} …):{ex}", file=sys.stderr)
            time.sleep(DELAY); continue
        for it in chunk:
            p = pages.get(it.title) or {}
            if p.get("missing") or "pageid" not in p:
                print(f"  ⚠ 找不到頁面:{it.title}(請檢查 topics.md 頁名)"); missing += 1; continue
            old = by_title.get(norm_title(it.title)) or by_id.get(f"pikipedia-{p['pageid']}")
            # 轉址撞車:這個頁名被轉到「別的佇列項」已占用的頁面 → 略過,避免互相覆寫中文標題
            if old and norm_title(old.get("queue_title") or old.get("title_en", "")) != norm_title(it.title):
                print(f"  ⚠ 略過 {it.title}:轉址到已收集的〈{old.get('title_en')}〉,請改頁名或刪掉這行"); missing += 1; continue
            if p["title"] != norm_title(it.title) and not old:
                print(f"  ↪ {it.title} 轉址為〈{p['title']}〉")
            entry = to_entry(it, p, old)
            if old:
                old.clear(); old.update(entry); updated += 1
            else:
                existing.append(entry); by_id[entry["id"]] = entry; added += 1
                by_title[norm_title(entry["title_en"])] = entry; by_title[norm_title(entry["queue_title"])] = entry
            print(f"  {'↻' if old else '＋'} {entry['title_zh']}〈{entry['title_en']}〉rev.{entry['source']['revid']}")
        if i + BATCH < len(todo):
            time.sleep(DELAY)

    existing.sort(key=sort_key(topics))
    print(f"新增 {added}、更新 {updated}、找不到 {missing};總計 {len(existing)} 條")
    if args.dry_run:
        print("(dry-run,未寫檔)")
        return 0
    save_knowledge(existing)
    print(f"已寫入 {KNOWLEDGE_JSON.relative_to(KNOWLEDGE_JSON.parent.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
