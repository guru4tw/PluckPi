# 修改紀錄

精簡紀錄有意義的改動;逐 commit 細節看 `git log`。

- 2026-10-25 階段 5 上站:`build_site.py` 重寫(首頁走路小遊戲 + 網站地圖、大綱頁、子分類頁、條目頁、來源總表、轉址);收集台改以條目 slug 為鍵、來源分級 A/B;`ste.py` 步驟上限 3 → 6、標題檢查改選配;`verify_sources.py` 支援多出處;Claude 起草 44 題(32 題待證)經 STE100 檢查存入;主機版 19 條移除並由 `retired.json` 轉址;詞彙表加入官方用字「私人區域」「花徑」「冰凍皮克敏」。
- 2026-10-25 階段 4 網站體驗草稿 `Docs/mockup/bloom/`:`_gen.py` 讀 topics.md 產出首頁(走路小遊戲 + 道場地圖 + 大分類快捷列)、7 個大綱頁、24 個子分類頁(讀完種花,存 localStorage)、1 個範例條目(iPhone 計步權限,依官方說明中心);`bloom.css` 新調色盤含暗色模式與 reduced-motion。截圖決定 A+C 已寫進 images.md 與測試。
- 2026-10-25 階段 3 圖片策略:`Docs/images.md`(授權決策樹、原創界線、調色盤)、`Docs/images.json` 登記簿、`assets/img/` 9 張原創 SVG(吉祥物芽芽花苞/開花、花苗、四色花、花瓣、腳印)、`tests/test_images.py`;素材預覽 `Docs/mockup/bloom/art-sheet.html`。遊戲截圖待決定。
- 2026-10-25 轉向 Pikmin Bloom:新增 `Docs/research/why_fun.md`(階段 1 研究);`topics.md` 全面改寫為大分類 → 子分類 → 玩家問題三層(7/24/47),每條附 A/B 來源,單一來源標待證;`glossary.md` 改官方繁中用語(花苗、精華、探險、巨大花朵、生活記錄);`common.py` parser 改三層(`parse_categories`),`tests/test_topics.py` 重寫。主機版 19 條暫時不上站(topic 已不存在,build 會略過)。
- 2026-10-25 收集改人工 + STE100:新增本機收集台 `Py/desk.py`/`desk.html`(挑頁面 → 抓原文 → 寫 STE100 → 檢查過才存回 `Docs/knowledge.json`)、`Py/ste.py` 檢查器、`Docs/glossary.md` 詞彙表;資料模型加 `headline_zh` `facts_zh` `steps_zh` `exceptions_zh` `terms_zh`,`card_html()` 有 STE 欄位就用新版面;`weekly.yml` 改名 `build.yml`,拿掉排程收集與 curate,改成 push 後驗證 + 建站。舊 19 條輸出不變,待逐條改寫。新增 `tests/test_desk.py`(15 項)。
- 2026-10-25 P1 前置:`topics.md` parser 改寫 —— 支援 `>> en:` 英文行與 `先讀=` 具名欄位,認不得的行報錯(附行號)不再默默吞掉;新增 `tests/test_topics.py`(21 項)。現有 topics.md 解析結果與建站輸出不變。
- 2026-10-24 P0 地基:每條知識有獨立網址 `zh-hant/k/{slug}/`(slug 由 collect 產生並回填 19 筆),主題頁搬到 `zh-hant/topics/{slug}/`,舊 `topics/*.html`、`sources/` 改為 build 產的轉址頁(保留 #錨點);首頁拿掉 JS 卡片渲染與難度/本週新增鈕,只留搜尋清單;build 不再讀系統日期,可重現。
- 2026-10-24 新增 `Docs/design.md` 網站設計書:每語言獨立網址(`/zh-hant/`、`/en/`,根網址自動判斷)、卡片四層撥洋蔥 + 難度三圈、單一 SSG 卡片渲染器、grounding 對原文查核、CI 預算;尚未實作。
- 2026-10-21 專案改名 PluckSkill → PluckPi:資料夾、網址(guru4tw.github.io/PluckPi)、bot UA、workflow 與 launch 名稱全部同步;中文名「拔拔道場」不變。
- 2026-10-18 專案改名 PluckAcademy → PluckPi:資料夾、網址(guru4tw.github.io/PluckPi)、bot UA、workflow 與 launch 名稱全部同步;中文名「拔拔道場」不變。
- 2026-10-18 建立骨架:主題脈絡 `Docs/topics.md`(7 主題)、來源清單、四支腳本(collect / curate / verify / build)、前端首頁、每週 workflow。以 Pikipedia(CC BY-SA 4.0)為第一個來源,首批收集 20 條,皮克敏圖鑑 10 條人工寫中文摘要。
