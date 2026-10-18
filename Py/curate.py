#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
curate.py — 選配:用 Claude 把英文摘要整理成中文條目
====================================================

對 Docs/knowledge.json 裡 status=raw 的條目,請 Claude 根據「且僅根據」excerpt_en
產出:一句話中文摘要(summary_zh)、2–4 個重點(key_points_zh)、必要時修正 title_zh。
輸出用 JSON Schema 結構化,寫回後 status=curated、curated_by=模型名。

沒有 ANTHROPIC_API_KEY → 直接略過、exit 0,整條 pipeline 照常;網站顯示英文原文並標「待整理」。
Actions 的金鑰放 repo Secrets,本機放 .env(勿 commit)。

用法:
    python3 Py/curate.py                 # 最多整理 30 條
    python3 Py/curate.py --limit 5 --dry-run
依賴:pip install anthropic
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from common import TODAY, load_knowledge, save_knowledge

MODEL = "claude-opus-5-5"

SYSTEM = """你是「拔拔道場」的皮克敏知識編輯,讀者是第一次接觸皮克敏的中文玩家。
規則:
1. 只能根據使用者提供的英文原文寫作,不可加入原文沒有的資訊;原文沒講的就不要寫。
2. 繁體中文、台灣用語,白話、簡短、說人話。
3. 專有名詞第一次出現時附英文原名,例如「洋蔥(Onion)」。
4. summary_zh 一句話、60 字以內,講清楚「這是什麼、有什麼用」。
5. key_points_zh 2 到 4 點,每點 30 字以內,一點一個事實。
6. title_zh 若提供的中文標題已經正確就照抄,不要改。"""

SCHEMA = {
    "type": "object",
    "properties": {
        "title_zh": {"type": "string"},
        "summary_zh": {"type": "string"},
        "key_points_zh": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 4},
    },
    "required": ["title_zh", "summary_zh", "key_points_zh"],
    "additionalProperties": False,
}


def curate_one(client, e: dict) -> dict | None:
    import anthropic
    prompt = (f"中文標題(可沿用):{e.get('title_zh')}\n英文頁名:{e.get('title_en')}\n"
              f"適用作品:{', '.join(e.get('games') or []) or '未知'}\n\n英文原文:\n{e.get('excerpt_en')}")
    for attempt in range(3):
        try:
            resp = client.beta.messages.create(
                model=MODEL, max_tokens=2048,
                betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                system=SYSTEM,
                messages=[{"role": "user", "content": prompt}],
                output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
            )
            if resp.stop_reason == "refusal":
                print(f"  ✗ 模型拒絕:{e.get('title_en')}"); return None
            text = next(b.text for b in resp.content if b.type == "text")
            return json.loads(text)
        except anthropic.RateLimitError as ex:
            wait = int(ex.response.headers.get("retry-after", "30")); print(f"  … 限流,{wait}s 後重試"); time.sleep(wait)
        except anthropic.APIStatusError as ex:
            if ex.status_code >= 500 and attempt < 2:
                time.sleep(5 * (attempt + 1)); continue
            print(f"  ✗ API 錯誤 {ex.status_code}:{ex.message}", file=sys.stderr); return None
        except anthropic.APIConnectionError:
            if attempt < 2:
                time.sleep(5); continue
            print("  ✗ 連線失敗", file=sys.stderr); return None
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("未設定 ANTHROPIC_API_KEY,略過中文整理(網站將顯示英文原文)。"); return 0
    try:
        import anthropic
    except ImportError:
        print("未安裝 anthropic 套件(pip install anthropic),略過中文整理。"); return 0

    client = anthropic.Anthropic()
    entries = load_knowledge()
    todo = [e for e in entries if e.get("status") == "raw" and e.get("excerpt_en")][: args.limit]
    print(f"待整理 {sum(1 for e in entries if e.get('status') == 'raw')} 條,本次處理 {len(todo)}")
    done = 0
    for e in todo:
        out = curate_one(client, e)
        if not out:
            continue
        e.update({"title_zh": out["title_zh"] or e.get("title_zh"), "summary_zh": out["summary_zh"],
                  "key_points_zh": out["key_points_zh"], "status": "curated",
                  "curated_by": MODEL, "curated_at": TODAY})
        e.pop("source_changed_at", None)
        done += 1
        print(f"  ✓ {e['title_zh']}:{e['summary_zh']}")
    if args.dry_run:
        print(f"(dry-run)整理 {done} 條,未寫檔"); return 0
    if done:
        save_knowledge(entries)
    print(f"整理完成 {done} 條")
    return 0


if __name__ == "__main__":
    sys.exit(main())
