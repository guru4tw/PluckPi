# PluckAcademy 拔拔道場・計畫書

## 一句話

每週一清晨自動從授權允許的來源收集皮克敏知識,整理成中文條目、註明出處,以靜態網站呈現;全程免費。

## 設計原則:脈絡分明、簡單易懂

讀者打開網站只需要理解三層:

```
主題(道場地圖,7 個)
  └─ 條目(一張卡 = 一個知識點,有難度標記)
       └─ 出處(連回原始頁面,含版本與授權)
```

- **主題**由 `Docs/topics.md` 一個檔決定,順序即學習順序(由淺到深)。
- **條目**只有一種格式(見資料模型),沒有例外欄位。
- **出處**每條必有,沒有出處的知識不上站。

## 架構(三層全靜態,與 SatirDaily 相同)

| 層 | 角色 | 說明 |
|---|---|---|
| GitHub Actions | Scheduler | 每週一台北 05:00 觸發,跑收集 → 整理 → 驗證 → 建站 → commit |
| Python 腳本 | Collector / Builder | 從 Pikipedia API 抓摘要、合併進 `Docs/knowledge.json`、生成網站 |
| GitHub Pages | Frontend | 純靜態 HTML + JS,搜尋/篩選全在瀏覽器端 |

## 每週 pipeline(順序固定)

1. `Py/collect_pikipedia.py --limit 20` — 讀 `topics.md` 佇列,挑最多 20 個尚未收集的頁面,經 MediaWiki API 抓首段摘要、頁面網址、修訂版號、分類,合併寫入 `Docs/knowledge.json`(已有條目只更新原文與版號,中文整理保留)。
2. `Py/curate.py` — **選配**。有 `ANTHROPIC_API_KEY` 才跑:把 `status=raw` 的英文摘要整理成中文一句話摘要 + 2–4 個重點;沒有金鑰則略過,網站直接顯示英文原文並標「待整理」。
3. `Py/verify_sources.py` — 逐筆連回出處網址確認有效,寫 `link_ok`,產 `Docs/link_report.json`。
4. `Py/build_site.py` — 正規化 → 根 `knowledge.json`;生成 `topics/*.html`、`sources/index.html`、`sitemap.xml`;把道場地圖注入 `index.html`。
5. Actions 有變動才 commit + push,Pages 自動刷新。

為何「收集」與「整理」分開:收集是機械、可重跑、零成本;整理需要語言能力、可能花錢。分層後沒有金鑰也能上線,有金鑰品質更好,兩者互不阻塞。

## 資料模型(`Docs/knowledge.json` 單筆)

```json
{
  "id": "pikipedia-1188",
  "topic": "pikmin",
  "level": "入門",
  "title_zh": "紅色皮克敏",
  "title_en": "Red Pikmin",
  "summary_zh": "耐火、攻擊力高,是每一代最先遇到的皮克敏。",
  "key_points_zh": ["免疫火焰", "攻擊力在基本三色中最高", "由紅色洋蔥培育"],
  "excerpt_en": "Red Pikmin are a red species of Pikmin with ...",
  "games": ["Pikmin 1", "Pikmin 2", "Pikmin 3", "Pikmin 4"],
  "source": {
    "key": "pikipedia",
    "name": "Pikipedia",
    "url": "https://www.pikminwiki.com/Red_Pikmin",
    "revid": 353014,
    "license": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    "accessed": "2026-10-18"
  },
  "status": "curated",
  "curated_by": "manual",
  "fetched_at": "2026-10-18",
  "hidden": false
}
```

欄位分三組:

- **脈絡欄位**(來自 `topics.md`,每次收集同步):`topic` `level` `title_zh`
- **原料欄位**(來自來源,每次收集更新):`title_en` `excerpt_en` `games` `source` `fetched_at`
- **整理欄位**(curate 或人工寫,收集時保留不動):`summary_zh` `key_points_zh` `status` `curated_by` `curated_at`

衍生欄位(pipeline 自動加):`link_ok` `link_checked_at`(verify 寫)。

## 授權

- Pikipedia 內容為 CC BY-SA 4.0:可轉載摘要,須註明出處並以相同授權釋出 → 本站整理文字同樣採 CC BY-SA 4.0。
- 程式碼 MIT。
- Pikmin、皮克敏為任天堂商標;本站為粉絲整理,非官方,無任何關聯。

## 之後可加(不在骨架內)

- 第二個來源(Pikmin Fandom、日文 wiki)→ 加一支 `collect_*.py`,沿用同一資料模型。
- 「本週新知」RSS / LINE 推播。
- 條目間交叉連結(例如紅色皮克敏 ↔ 火焰陷阱)。
- 讀者投稿表單(GitHub Issue 範本)。
