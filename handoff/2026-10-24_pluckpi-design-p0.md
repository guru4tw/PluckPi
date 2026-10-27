# Handoff: PluckPi 網站設計書 + P0 地基完成

**Date**: 2026-10-24 21:44
**Status**: milestone

## TL;DR

寫了網站設計書 `Docs/design.md`(極簡 UI、中英語系、撥洋蔥教學、P0–P4),經獨立子代理對抗審查 15 條後修訂;接著實作並推上 P0(條目獨立網址、單一卡片渲染器、舊網址轉址、可重現建站),commit `4df3785` 已 push,線上 `zh-hant/k/red-pikmin/` 回 200。
下一步:等週一 05:00(台北)第一次跑新 workflow 確認無誤,再決定 P1(語系)何時開工——設計書明說 P1 之後要等內容量跟上。

## 已交付

- `Docs/design.md` — 網站設計書;§九 有 15 條審查裁決;P0 列已標「2026-10-24 完成」
- `Py/common.py` — 新增 `make_slug()`、`ensure_slugs()`
- `Py/collect_pikipedia.py` — 每次收集補缺的 `slug`(含「沒有要抓的頁面」提前結束分支)
- `Py/build_site.py` — 整支改寫:`zh-hant/topics/{slug}/`、`zh-hant/k/{slug}/`、`zh-hant/sources/`、舊網址轉址頁、`Docs/retired.json` 支援、日期改取資料(不讀 `TODAY`)
- `index.html` — 拿掉 JS `card()`、難度鈕、「只看本週新增」;只留搜尋清單 + 舊首頁錨點轉址
- `assets/style.css` — 加 `.results`、`.entry`;刪 `.chip*`、`.new`
- `Docs/knowledge.json` — 19 筆回填 `slug`
- `.github/workflows/weekly.yml` — `git add -A zh-hant/ topics/ sources/`
- `CLAUDE.md`、`Log/history.md` — 同步檔案地圖、紀律(卡片只一份、網址是承諾)

## 未竟事項

**首要(下一步即做)**:

1. 確認週一自動 workflow 在新結構下正常(這是新 build 第一次在 Actions 跑,收集會新增約 20 條、要產新 slug 與條目頁)
   - A(建議)— 週一後 `gh run list --workflow weekly-knowledge -L 1` 看結果,再 `git pull` 檢查新條目都有 `slug` 與 `zh-hant/k/<slug>/index.html`
   - B — 現在手動觸發 `gh workflow run weekly-knowledge -f limit=5` 提前驗證;代價:提早消耗本週爬蟲額度、產生一個 bot commit

**其後**:

2. P1 語系(`/en/`、根網址改 x-default 入口、hreflang、`i18n.json`、`topics.md` parser 改寫)
   - A(建議)— 先做 parser 改寫 + `unittest`(`Py/common.py:32` `HEADING_RE`、`:34` `ITEM_RE` 會默默吞掉新格式),不動網址
   - B — 整包 P1 一次做;代價:英文內容幾乎沒有(19 條都無 `summary_en`),設計書規定 `/en/` 達門檻前要 `noindex`
3. curate.py 仍「未實測」(CLAUDE.md 標註);P2 grounding 依賴它 — `python3 Py/curate.py --limit 5 --dry-run`(需 `ANTHROPIC_API_KEY`)

## 易踩坑 / Session-only 知識

- **影片筆記不在專案內** — 在上層 `../Video_Notes/2026-10-24_D-SVFneJ_Nk_v2/01_摘要與Claude效能方法.md`,不是 `PluckPi/Video_Notes/`
- **P0 就用最終網址** — 深層頁直接放 `zh-hant/`(而非先放根目錄),避免 P1 再搬一次;首頁仍在根目錄,P1 才變語言入口
- **slug 由 collect 產,不由 build 產** — build 遇缺 slug 直接 exit 1;理由是 build 要維持「資料的純函數」、不寫回 `Docs/`
- **轉址頁無 JS 時會丟 `#錨點`** — meta refresh 只到主題頁;有 JS 才能 `#pikipedia-xxx` → 條目頁。GitHub Pages 無法發 301
- **可重現性驗證法** — 用假日期跑兩次 build 比 md5:monkeypatch `datetime.date.today` 再 `runpy.run_path("Py/build_site.py")`(腳本在 scratchpad,已不保存;要用照此重寫)。2030/2031/今天三次輸出 md5 皆 `98dbdd6395b00488fdb9160bb31a7a57`(會隨資料變)
- **「最近更新」改成 2026-10-18** — 是資料日期(`fetched_at`),不是 bug;舊版顯示 10-22 是建站日
- **port 8766 已被一個外部 `python3 -m http.server`(PID 25528,cwd=專案根)占用** — `preview_start pluckpi-static` 會失敗,直接 navigate `http://localhost:8766/` 即可
- **審查裁決重點(已進設計書 §九)** — 代數篩選延後到 P3(`games` 是出現代數不是規則差異,19 條有 12 條四代全有);grounding 只做警告不擋上線;Lighthouse 只擋 PR 不擋每週更新;首頁只放地圖不放卡片
- **`handoff/` 未加入 gitignore 也未 add** — 版控與否由使用者決定
