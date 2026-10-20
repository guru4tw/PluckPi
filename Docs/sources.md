# 拔拔道場・知識來源與授權

> **人工維護。** 列出本站允許引用的來源、授權條件、抓取方式與狀態。
> 新增來源前先確認授權允許轉載摘要並註明出處;不允許的來源只貼連結、不抓內容。

| key | 來源 | 網址 | 授權 | 抓取方式 | 狀態 |
|---|---|---|---|---|---|
| `pikipedia` | Pikipedia(英文皮克敏百科) | https://www.pikminwiki.com/ | CC BY-SA 4.0 | MediaWiki API(`api.php` extracts + info + categories) | `ready` |
| `nintendo` | 任天堂官方皮克敏網站 | https://www.nintendo.com/ | 版權所有,僅連結 | 不抓內容,人工補連結 | `link-only` |
| `pikmin_fandom` | Pikmin Fandom Wiki | https://pikmin.fandom.com/ | CC BY-SA 3.0 | MediaWiki API | `todo` |

## 狀態說明

| 值 | 意義 |
|---|---|
| `ready` | 已寫好收集腳本,每週自動抓 |
| `todo` | 授權確認可用,腳本待開發 |
| `link-only` | 授權不允許轉載,只能連結 |

## 引用規範(每一條知識都要有)

每條知識的 `source` 欄位必填:來源名稱、原始頁面網址、修訂版號(wiki 的 `revid`,讓讀者能對到當時的版本)、授權、查閱日期。
網站卡片底部一律顯示「出處:來源〈頁名〉・版本 revid・授權・查閱日期」,並連回原始頁面。

## 爬蟲禮儀

- User-Agent:`PluckPiBot/0.1 (+https://github.com/guru4tw/PluckPi)`
- Pikipedia `robots.txt` 要求 `Crawl-delay: 1`;腳本每次請求間隔 1.5 秒,一次最多 10 個頁名合併查詢。
- 每週只抓一次、每次最多 20 個新頁面,不做全站掃描。
