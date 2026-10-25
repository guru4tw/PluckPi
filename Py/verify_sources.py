#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_sources.py — 逐筆連回出處網址,確認引用連結有效
=====================================================

讀 Docs/knowledge.json,對每條條目的每個 sources[].url 做 HEAD(405 則改 GET;同一網址只查一次),
每個來源寫 ok,條目的 link_ok = 全部來源都通;並產 Docs/link_report.json。

exit code:0 = 全通過;2 = 有失效連結(不擋 pipeline,前端標「⚠ 連結待確認」);1 = 讀檔失敗。

用法:
    python3 Py/verify_sources.py
    python3 Py/verify_sources.py --no-annotate   # 只出報告不回寫
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

from common import DOCS, TODAY, UA, load_knowledge, save_knowledge

REPORT = DOCS / "link_report.json"
DELAY = 1.5


def check(url: str) -> tuple[bool, int | str]:
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return 200 <= r.status < 400, r.status
        except urllib.error.HTTPError as e:
            if e.code == 405 and method == "HEAD":
                continue
            if 300 <= e.code < 400:            # Python 3.9 的 urllib 不跟 307/308;有轉址就代表頁面還在
                return True, e.code
            return False, e.code
        except Exception as e:
            return False, type(e).__name__
    return False, "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-annotate", action="store_true")
    args = ap.parse_args()
    try:
        entries = load_knowledge()
    except Exception as e:
        print(f"讀檔失敗:{e}", file=sys.stderr); return 1

    rows, broken, seen = [], [], {}
    for e in entries:
        srcs = e.get("sources") or []
        for s in srcs:
            url = s.get("url")
            if url not in seen:
                if seen:
                    time.sleep(DELAY)
                seen[url] = check(url) if url else (False, "no-url")
            ok, st = seen[url]
            rows.append({"slug": e.get("slug"), "url": url, "ok": ok, "status": st})
            if not ok:
                broken.append(rows[-1])
            if not args.no_annotate:
                s["ok"] = ok
            print(f"  {'✓' if ok else '✗'} {e.get('slug')} {url} ({st})")
        if not args.no_annotate:
            e["link_ok"] = bool(srcs) and all(x.get("ok") for x in srcs); e["link_checked_at"] = TODAY

    REPORT.write_text(json.dumps({"checked_at": TODAY, "total": len(rows), "broken": len(broken),
                                  "broken_list": broken, "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    if not args.no_annotate:
        save_knowledge(entries)
    print(f"檢查 {len(rows)} 個出處(不重複網址 {len(seen)}),失效 {len(broken)};報告 {REPORT.name}")
    return 2 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
