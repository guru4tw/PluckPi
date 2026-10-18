#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_sources.py — 逐筆連回出處網址,確認引用連結有效
=====================================================

讀 Docs/knowledge.json,對每條 source.url 做 HEAD(405 則改 GET),
把 link_ok / link_checked_at 寫回,並產 Docs/link_report.json。

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

    rows, broken = [], []
    for i, e in enumerate(entries):
        url = (e.get("source") or {}).get("url")
        if not url:
            ok, st = False, "no-url"
        else:
            ok, st = check(url)
        rows.append({"id": e["id"], "title": e.get("title_en"), "url": url, "ok": ok, "status": st})
        if not ok:
            broken.append(rows[-1])
        if not args.no_annotate:
            e["link_ok"] = ok; e["link_checked_at"] = TODAY
        print(f"  {'✓' if ok else '✗'} {e.get('title_en')} ({st})")
        if i + 1 < len(entries):
            time.sleep(DELAY)

    REPORT.write_text(json.dumps({"checked_at": TODAY, "total": len(rows), "broken": len(broken),
                                  "broken_list": broken, "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    if not args.no_annotate:
        save_knowledge(entries)
    print(f"檢查 {len(rows)} 條,失效 {len(broken)};報告 {REPORT.name}")
    return 2 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
