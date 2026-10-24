# 修改紀錄

精簡紀錄有意義的改動;逐 commit 細節看 `git log`。

- 2026-10-24 P0 地基:每條知識有獨立網址 `zh-hant/k/{slug}/`(slug 由 collect 產生並回填 19 筆),主題頁搬到 `zh-hant/topics/{slug}/`,舊 `topics/*.html`、`sources/` 改為 build 產的轉址頁(保留 #錨點);首頁拿掉 JS 卡片渲染與難度/本週新增鈕,只留搜尋清單;build 不再讀系統日期,可重現。
- 2026-10-24 新增 `Docs/design.md` 網站設計書:每語言獨立網址(`/zh-hant/`、`/en/`,根網址自動判斷)、卡片四層撥洋蔥 + 難度三圈、單一 SSG 卡片渲染器、grounding 對原文查核、CI 預算;尚未實作。
- 2026-10-21 專案改名 PluckSkill → PluckPi:資料夾、網址(guru4tw.github.io/PluckPi)、bot UA、workflow 與 launch 名稱全部同步;中文名「拔拔道場」不變。
- 2026-10-18 專案改名 PluckAcademy → PluckPi:資料夾、網址(guru4tw.github.io/PluckPi)、bot UA、workflow 與 launch 名稱全部同步;中文名「拔拔道場」不變。
- 2026-10-18 建立骨架:主題脈絡 `Docs/topics.md`(7 主題)、來源清單、四支腳本(collect / curate / verify / build)、前端首頁、每週 workflow。以 Pikipedia(CC BY-SA 4.0)為第一個來源,首批收集 20 條,皮克敏圖鑑 10 條人工寫中文摘要。
