# 拔拔道場 PluckPi

網站:https://guru4tw.github.io/PluckPi/

每週自動收集皮克敏(Pikmin)知識,整理成中文條目,**每一條都註明出處**。讀者只需理解三層:

```
主題(道場地圖,7 個)→ 條目(入門 / 進階 / 達人)→ 出處(來源・版本・授權)
```

**架構**:GitHub Pages(顯示)+ GitHub Actions(每週一排程)+ `knowledge.json`(資料)。全部免費,前端純靜態。

## 檔案

| 檔 | 說明 |
|---|---|
| `Docs/topics.md` | 主題脈絡 + 收集佇列,**唯一要手改的知識脈絡檔** |
| `Docs/sources.md` | 允許的來源與授權 |
| `Docs/knowledge.json` | 原始條目(腳本合併寫入;中文整理可人工填) |
| `Py/collect_pikipedia.py` | 從 Pikipedia API 收集(零依賴) |
| `Py/curate.py` | 選配:Claude 整理成中文(有金鑰才跑) |
| `Py/verify_sources.py` | 出處連結驗證 |
| `Py/build_site.py` | 建站:根 `knowledge.json`、主題頁、來源頁、sitemap |
| `index.html` + `assets/style.css` | 前端 |
| `.github/workflows/weekly.yml` | 每週一台北 05:00 自動更新 |

## 本地預覽

```bash
python3 -m http.server 8766
```

開 http://localhost:8766/(前端 `fetch` 不支援 `file://`)。

## 本地跑一次 pipeline

```bash
python3 Py/collect_pikipedia.py --limit 20 && python3 Py/verify_sources.py; python3 Py/build_site.py
```

## 新增知識

在 `Docs/topics.md` 對應主題下加一行 `- Pikipedia 頁名 | 中文標題`,下次排程自動收集。

## 授權

- 程式碼 MIT。
- 知識內容整理自 [Pikipedia](https://www.pikminwiki.com/)(CC BY-SA 4.0),本站整理文字同樣採 CC BY-SA 4.0;每條卡片底部有出處、修訂版號與查閱日。
- Pikmin／皮克敏為任天堂商標。本站為粉絲整理的非官方資源,與任天堂無任何關聯。
