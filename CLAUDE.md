# CLAUDE.md — 拔拔道場 PluckPi

> 讓人快速了解**怎麼玩手機遊戲 Pikmin Bloom**、以及它為什麼好玩的粉絲網站。靜態站:GitHub Pages + GitHub Actions + `knowledge.json`,全部免費。
> 重建 prompt 見 [Docs/prompt_bloom_rebuild.md](Docs/prompt_bloom_rebuild.md);舊設計書 [Docs/design.md](Docs/design.md)、[Docs/plan.md](Docs/plan.md) 是主機版時期寫的,版面原則可參考,內容範圍以本檔為準。

---

## 網站精神(動任何東西前先對這五條)

1. **只做 Pikmin Bloom** —— 手機版(2021 上市,Niantic 開發,2025-05 起 Scopely 營運)。不寫 Pikmin 1–4、Hey! Pikmin 或任何主機版內容;主機版概念(洋蔥戰術、原生生物戰鬥、隊長操作)Bloom 裡沒有就不提。注意遊戲名是 **Bloom**,不是 Boom
2. **首頁呈現好玩,不說明好玩** —— 首頁用可以動手的小體驗(例:滑動當走路、走過的地方長出花、點幼苗拔出皮克敏)讓人直接感受到好玩,不寫「這遊戲好玩在…」的說明文。「為什麼紅」的研究(`Docs/research/`)是給團隊真正理解遊戲用的,結論轉成體驗,不轉成文案。新手玩首頁 5 分鐘,要能說出「這遊戲在幹嘛、我第一天要做什麼」
3. **真的懂才寫** —— 每個事實都有出處,沒出處不上站;不確定標「待證」,不用推測補洞。用遊戲內繁中正式用語
4. **圖片零授權風險** —— 不用官方美術、Logo、官網圖、Pikipedia 上的遊戲圖(Nintendo / Niantic 版權,不是 CC)。可用:原創插畫、自己拍的實景照、逐張確認過的 CC0 / CC BY 圖。每張圖登記來源與授權
5. **網站本身要好玩** —— 可以有皮克敏的味道(葉、花苞、花、散步、花瓣),但不能抄:不描摹官方角色造型、不用官方字標、不拿官方配色當主視覺。好玩靠設計與互動,不靠誇張文案

---

## 寫作規則

- 教學內容與標題用 **STE100-Brief**:一句一件事、主動語態、一詞一義、不比喻。標題格式「名稱:特性」
- 每個條目先寫「玩家問題」,再寫答案;大分類順序照「新手第一週」排,不是照百科分類
- 每個大分類有一頁大綱:在講什麼、有哪些子分類、建議閱讀順序、每個子分類一句話
- **冷知識**是獨立大分類:只收 Pikmin Bloom 的(開發背景、命名由來、飾品與真實地點的對應、隱藏細節、官方訪談);每條要有出處,單一來源標「待證」,查不到出處的傳言不收
- 來源分級,卡片要看得出等級:A 官方(官網、官方部落格、遊戲內說明、Nintendo 遊戲頁)> B 社群百科(Pikipedia,CC BY-SA 4.0)> C 公開數據(註明發表者與日期)> D 玩家聲音(只歸納趨勢,不引原文、不放帳號)
- 「為什麼好玩」這類結論至少兩個獨立來源;單一來源標「待證」
- Pikmin Bloom 是持續營運的遊戲:活動、社群日、限時內容一律標有效期限與查閱日,過期要下架或改寫
- 走路遊戲要提醒安全與隱私(看路、生活日誌與明信片會露出地點)

---

## 現況(2026-10-25)

五階段重建([Docs/prompt_bloom_rebuild.md](Docs/prompt_bloom_rebuild.md))已走完一輪:研究 `Docs/research/why_fun.md` → 三層 `topics.md`(7 大分類、24 子分類、47 個玩家問題)→ 圖片策略 → 版面 → 內容。
**47 題已回答 44 題,其中 32 題標「待證」**(多數只有一個來源,或用到官方繁中名稱未確認的詞)。沒回答的 3 題來源不足:`petal-timing`、`battery`、`walking-safety`,頁面顯示「還沒寫」。
這 44 題由 Claude 讀來源起草、經 `ste.py` 檢查後存入(`curated_by: "claude"`),**還沒有人逐條校對**。主機版 19 條已從資料移除,舊網址由 `Docs/retired.json` 轉址。
`Py/ste.py` 只檢查寫法、不檢查範圍與正確性;範圍靠 `topics.md` 只收 Bloom 問題、正確性靠出處與人工校對。

---

## 脈絡結構(設計核心,改動前先想這個)

**大分類 → 子分類 → 條目 → 出處。** 首頁就是網站地圖。

| 層 | 定義在哪 | 頁面(站內路徑) | 規則 |
|---|---|---|---|
| 大分類 | `Docs/topics.md` 的 `#` | 大綱頁 `zh-hant/c/{slug}/`:這分類在講什麼、子分類與一句話、建議閱讀順序 | 順序即新手學習順序,含「冷知識」一類 |
| 子分類 | `Docs/topics.md` 的 `##` | 子分類頁 `zh-hant/topics/{slug}/`:玩家問題清單 + 讀完種花 | 子分類順序就是閱讀順序 |
| 條目 | `topics.md` 的 `-` 行(問題、難度、待證)+ `Docs/knowledge.json`(答案、出處) | 條目頁 `zh-hant/k/{slug}/` | 一頁 = 一個玩家問題的答案。條目 slug 是網址,定了不改 |
| 出處 | 條目的 `sources[]` | 條目頁底部 + 來源總表 | 至少一個 A(官方)或 B(Pikipedia)。沒有出處的知識不上站 |

**首頁 = 走路小遊戲 + 網站地圖**:滑動當走路、長花苗、拔出吉祥物芽芽;下方列出全部大分類的大綱與子分類。網站地圖是純 HTML,關掉 JS 或動畫照樣能用。不寫「這遊戲好玩在…」的說明文。

---

## 收集流程(人工,2026-10-25 起取代每週排程)

1. 新問題先寫進 `Docs/topics.md`(問題、slug、來源、難度、待證)
2. 本機 `python3 Py/desk.py` → http://127.0.0.1:8767/ ,左側佇列依大分類 › 子分類列出全部問題
3. 選一題 → 自動抓來源:Pikipedia 抓摘要與版號(`collect_pikipedia.fetch_pages`);官方網址列出連結,自己點開讀
4. 寫 STE100(答案事實、怎麼做、例外、詞彙);`Py/ste.py` 即時檢查,**沒過不能存**
5. 「存入」→ 以條目 slug 寫回 `Docs/knowledge.json`;來源清單從 `topics.md` 產生(Pikipedia 記版號與授權,官方記查閱日;非 A/B 網域直接擋)
6. 本機 `python3 Py/verify_sources.py && python3 Py/build_site.py`,或 push 後由 `.github/workflows/build.yml` 跑

分類、問題文字、難度、待證、期限只認 `topics.md`;`knowledge.json` 只放答案與出處。一個來源頁可以給多個問題共用。

---

## 檔案地圖

| 檔 | 狀態 | 說明 |
|---|---|---|
| `Docs/topics.md` | **人工維護** | 三層:`# 數字. 大分類 (slug)` + `> 一行大綱`;`## 大.子 子分類 (slug) · 預設難度` + `> 一句話`;`- 玩家問題 (條目slug) \| pikipedia:頁名; 網址 \| 難度(可省) \| 先讀=/狀態=待證/期限=`。`parse_categories()` 解析,格式錯直接報錯 |
| `Docs/pikmin_bloom_oneliners.md` | **人工維護** | 首頁輪播的 31 句「X版:一句話」,`## 31 句` 底下 `N. **X版:** 句子`;`build_site.load_oneliners()` 解析 |
| `Docs/glossary.md` | **人工維護** | STE100 詞彙表 `- 標準詞 \| 禁用詞 \| 白話定義`;標準詞以官方繁中用語為準,找不到的標(待確認) |
| `Docs/research/why_fun.md` | 研究 | 為什麼好玩、為什麼紅(MDA、數據、top tasks)。給團隊理解,不上站 |
| `Docs/images.md` | 規則 | 圖片策略:授權決策樹、原創界線、調色盤;截圖決定 A+C(只放手機系統設定截圖) |
| `Docs/images.json` + `assets/img/` | 已建 | 圖片登記簿與原創 SVG。沒登記的圖不上站,`tests/test_images.py` 擋 |
| `Docs/knowledge.json` | 收集台寫入 | 條目答案與出處(扁平陣列,以 slug 為鍵) |
| `Docs/retired.json` | 人工 | 舊網址轉址 `{"entries": {slug: 路徑}, "topics": {slug: 路徑}}`,路徑空字串 = 首頁 |
| `Docs/link_report.json` | 自動產生 | 出處連結驗證報告 |
| `Docs/mockup/bloom/` | 草稿 | 階段 4 版面草稿與素材預覽(`_gen.py` 產),不上站 |
| `Docs/design.md`、`Docs/plan.md`、`Docs/sources.md` | 舊 | 主機版時期的設計與計畫,版面原則可參考,範圍以本檔為準 |
| `Py/common.py` | 已建 | 路徑、`topics.md` 解析、來源分級(`source_grade`:A 官方網域 / B Pikipedia)、knowledge 讀寫 |
| `Py/desk.py` + `Py/desk.html` | 已建 | 收集台(stdlib http.server,只綁 127.0.0.1:8767)。API:`/api/queue` `/api/fetch?slug=` `/api/lint` `/api/save`;`save()` 也可在 Python 裡直接呼叫(同一條檢查路徑) |
| `Py/ste.py` | 已建 | STE100 檢查:事實 ≤25 字、無比喻/被動/一句兩事/代名詞開頭/誇張/禁用詞、步驟 ≤6、詞彙「詞 = 定義」。關鍵字比對,誤判就改寫句子,不放寬規則 |
| `Py/build_site.py` | 已建 | 建整站(見上表路徑)+ `knowledge.json` + 轉址頁 + `sitemap.xml`。`zh-hant/`、`topics/`、`sources/`、`index.html` 每次重建,勿手改。不讀系統日期 |
| `Py/verify_sources.py` | 已建 | 逐一連回每個出處(同網址只查一次),寫各來源 `ok` 與條目 `link_ok`。exit 0 全通過 / 2 有失效 / 1 讀檔失敗 |
| `Py/collect_pikipedia.py` | 只剩函式 | `fetch_pages()` 給收集台用;直接執行只印說明 |
| `Py/curate.py` | **舊、不相容** | 主機版時期的 Claude 整理腳本,產舊格式 `summary_zh`,不要用 |
| `assets/style.css`、`assets/js/` | 手寫 | 全站樣式(含暗色、reduced-motion);`walk.js` 首頁小遊戲、`progress.js` 讀完種花(localStorage)、`quip.js` 首頁站名下一句話輪播 |
| `index.html`、`zh-hant/`、`knowledge.json`(根)、`sitemap.xml`、`topics/*.html`、`sources/` | 自動產生 | 勿手改 |
| `tests/` | 已建 | `python3 -m unittest discover -s tests`:topics 解析、STE100、收集台存檔、條目頁、圖片登記 |
| `Log/history.md` | 人工 | 精簡修改 log |

---

## 資料模型(`Docs/knowledge.json` 單筆)

- 鍵:`slug`(= `id`,= topics.md 的條目 slug)、`topic`
- 答案:`facts_zh[]` `steps_zh[]` `exceptions_zh[]` `terms_zh[{term,def}]`
- 出處:`sources[{kind: pikipedia|url, grade: A|B, name, url, title?, revid?, license?, license_url?, accessed, ok?}]`
- 狀態:`status`(`curated`)`curated_by`(`manual` / `claude`)`curated_at` `hidden` `link_ok` `link_checked_at`
- 問題文字、難度、待證、期限、先讀**不存這裡**,建站時從 `topics.md` 合併

---

## 開發紀律

- **新增知識** — 先確認是 Pikmin Bloom 的內容、能對到 A 或 B 來源,再寫進 `Docs/topics.md`,到收集台寫答案。不要手動在 `knowledge.json` 造條目
- **只寫來源有寫的事** — 來源沒回答就留「還沒寫」,不要用推論補。單一來源或用語未確認 → `狀態=待證`
- **寫中文** — 一律過 `ste.py`。改規則改 `Py/ste.py`(附測試),改用詞改 `Docs/glossary.md`
- **引用規範** — 條目頁列出每個出處:名稱〈頁名〉、等級、Pikipedia 版本與授權、查閱日,並連回原頁
- **爬蟲禮儀** — UA `PluckPiBot/0.1`,請求間隔 1.5 秒;一次抓一頁、人按才抓,不全站掃描
- **HTML 只在 `build_site.py` 產**;JS 只做小遊戲與讀完種花,不渲染內容
- **網址是承諾** — 條目與子分類 slug 不改;要刪就寫進 `Docs/retired.json` 留去處
- **圖片** — 先過 `Docs/images.md` 檢查表並登記 `Docs/images.json`
- **Python** — UTF-8、`# -*- coding: utf-8 -*-`、dataclass + type hint;腳本用 `__file__` 錨定路徑。本機 Python 3.9 可跑,零第三方依賴

---

## 環境

- 本機預覽:`python3 -m http.server 8766`(或 `.claude/launch.json` 的 `pluckpi-static`),開 http://localhost:8766/
- 收集台:`python3 Py/desk.py`,開 http://127.0.0.1:8767/
- 本機建站:`python3 Py/verify_sources.py && python3 Py/build_site.py`
- 測試:`python3 -m unittest discover -s tests`
- 網站:https://guru4tw.github.io/PluckPi/(repo 建好、Pages 設 main 分支根目錄後生效)
