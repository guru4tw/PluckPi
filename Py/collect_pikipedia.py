#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collect_pikipedia.py — Pikipedia(CC BY-SA 4.0)MediaWiki API 抓取函式
=====================================================================

2026-10-25 起收集改人工(Py/desk.py),條目以「玩家問題 slug」為鍵,不再以 Pikipedia 頁名建條目。
這支只留給收集台用的抓取函式:fetch_pages(頁名清單)→ 首段摘要、正式網址、最新版號、分類。
直接執行只會印出說明,不寫任何檔。

零第三方依賴(urllib)。爬蟲禮儀:UA PluckPiBot/0.1,批次請求間隔 1.5 秒。
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from typing import Dict, List

from common import UA

API = "https://www.pikminwiki.com/api.php"
BATCH = 10           # 一次查幾個頁名(TextExtracts exintro 上限 20)


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


def main() -> int:
    print(__doc__)
    print("收集請用:python3 Py/desk.py(本機收集台)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
