# CLAUDE.md — 拔拔道場 PluckPi

> 每週自動收集皮克敏(Pikmin)知識、中文整理、註明出處的靜態網站。GitHub Pages + GitHub Actions + `knowledge.json`,全部免費。
> 架構與 SatirDaily 同源(三層全靜態),差別在:資料是「知識條目」不是「活動」,排程是每週不是每天。完整計畫見 [Docs/plan.md](Docs/plan.md)。

---

## 專案目標

每週一清晨主動從授權允許的來源收集皮克敏相關知識,整理成中文,**每一條都註明出處(來源、網址、修訂版號、授權、查閱日)**。
網站框架必須**脈絡分明、簡單易懂**:讀者只需理解三層 —— 主題 → 條目 → 出處。

---

## 三層脈絡(設計核心,改動前先想這個)

| 層 | 定義在哪 | 規則 |
|---|---|---|
| 主題(道場地圖) | `Docs/topics.md` 的 `##` 標題 | 7 個,順序即學習順序(由淺到深、由物到事)。加主題只改這個檔 |
| 條目(卡片) | `Docs/knowledge.json` 單筆 | 一張卡 = 一個知識點,有難度(入門/進階/達人)。格式唯一,見資料模型 |
| 出處 | 條目的 `source` 欄位 | 必填。沒有出處的知識不上站 |

---

## 每週 pipeline(順序固定,`.github/workflows/weekly.yml`)

1. `Py/collect_pikipedia.py --limit 20` — 讀 `topics.md` 佇列,挑尚未收集的頁面,MediaWiki API 抓摘要/網址/版號/分類,合併進 `Docs/knowledge.json`
2. `Py/curate.py` — **選配**,有 `ANTHROPIC_API_KEY` 才跑:英文摘要 → 中文一句話 + 重點;沒金鑰自動略過
3. `Py/verify_sources.py` — 逐筆連回出處驗證,寫 `link_ok`,產 `Docs/link_report.json`
4. `Py/build_site.py` — 正規化 → 根 `knowledge.json`、`topics/*.html`、`sources/index.html`、`sitemap.xml`、首頁注入
5. Actions 有變動才 commit + push

**為何收集與整理分開**:收集機械、免費、可重跑;整理要語言能力、可能花錢。分層後沒金鑰也能上線,有金鑰品質更好。

---

## 檔案地圖

| 檔 | 狀態 | 說明 |
|---|---|---|
| `Docs/topics.md` | **人工維護** | 主題脈絡 + 收集佇列。`## 數字. 中文名 (slug) · 預設難度`,底下 `- Pikipedia 頁名 \| 中文標題 \| 難度(可省)` |
| `Docs/sources.md` | **人工維護** | 允許的來源、授權、抓取方式、狀態(`ready`/`todo`/`link-only`) |
| `Docs/knowledge.json` | 腳本合併寫入 | 原始條目(扁平陣列)。中文整理欄位可人工填,收集時不會被洗掉 |
| `Docs/link_report.json` | 自動產生 | 出處連結驗證報告 |
| `Py/common.py` | 已建 | 共用:路徑、`topics.md` 解析、knowledge 讀寫、排序 |
| `Py/collect_pikipedia.py` | 已建 | Pikipedia 收集器(urllib,零依賴)。`--limit N` / `--refresh` / `--dry-run` |
| `Py/curate.py` | 已建、**未實測** | 選配 Claude 整理(`anthropic` SDK,`claude-opus-5-5`,JSON Schema 結構化輸出,含 server-side fallback) |
| `Py/verify_sources.py` | 已建 | 出處連結驗證。exit 0 全通過 / 2 有失效 / 1 讀檔失敗 |
| `Py/build_site.py` | 已建 | 建站。`topics/`、`sources/` 每次 `rmtree` 重建,勿手改 |
| `index.html` | 手寫 + 注入 | 首頁。`<!-- MAP -->` / `<!-- STATS -->` 標記之間由 build 注入,其餘手改 |
| `assets/style.css` | 手寫 | 首頁與子頁共用樣式 |
| `knowledge.json`(根) | 自動產生 | 前端 fetch 的檔,勿手改 |
| `topics/{slug}.html`、`sources/index.html`、`sitemap.xml` | 自動產生 | SSG 子頁 |
| `Log/history.md` | 人工 | 精簡修改 log |

---

## 資料模型(`Docs/knowledge.json` 單筆)

欄位分三組,**收集腳本只動前兩組**:

- 脈絡欄位(來自 `topics.md`):`topic` `level` `title_zh`
- 原料欄位(來自來源):`title_en` `excerpt_en` `games` `source{key,name,url,revid,license,license_url,accessed}` `fetched_at`
- 整理欄位(curate / 人工):`summary_zh` `key_points_zh` `status`(`raw`/`curated`)`curated_by` `curated_at`

衍生:`link_ok` `link_checked_at`(verify 寫)、`source_changed_at`(原文版號變了,整理內容可能要複核)、`hidden`(true 則不上站)。
完整範例見 `Docs/plan.md`。

---

## 開發紀律

- **新增知識** — 在 `Docs/topics.md` 對應主題下加一行,下次收集自動抓。不要手動在 `knowledge.json` 造條目。
- **人工寫中文** — 可直接編 `Docs/knowledge.json` 的 `summary_zh` / `key_points_zh`,並把 `status` 設 `curated`、`curated_by` 設 `manual`;收集時保留。
- **新增來源** — 先在 `Docs/sources.md` 確認授權允許轉載摘要;寫一支 `Py/collect_<key>.py`,沿用 `common.py` 與同一資料模型、同樣的合併規則(只更新原料欄位)。
- **引用規範** — 卡片一律顯示「出處:來源〈頁名〉・版本 revid・授權・查閱日」並連回原頁;`source.revid` 讓讀者對得到被引用的版本。
- **爬蟲禮儀** — UA `PluckPiBot/0.1`,請求間隔 1.5 秒,一週一次、每次最多 20 頁,不全站掃描。
- **卡片 HTML 兩份** — `index.html` 的 JS `card()` 與 `build_site.py` 的 `card_html()` 要同步改。
- **Python** — UTF-8、`# -*- coding: utf-8 -*-`、dataclass + type hint;腳本用 `__file__` 錨定路徑,任何 cwd 都能跑。本機 Python 3.9 可跑(collect/verify/build 零依賴)。

---

## 環境

- 本機預覽:`python3 -m http.server 8766`(或 `.claude/launch.json` 的 `pluckpi-static`),開 http://localhost:8766/
- 本機跑整條:`python3 Py/collect_pikipedia.py && python3 Py/verify_sources.py && python3 Py/build_site.py`
- 選配整理:`pip install anthropic`,`export ANTHROPIC_API_KEY=...`,`python3 Py/curate.py --limit 5 --dry-run` 先看結果
- 網站:https://guru4tw.github.io/PluckPi/(repo 建好、Pages 設 main 分支根目錄後生效)
