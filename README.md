# 拔拔道場 PluckPi

網站:https://guru4tw.github.io/PluckPi/

手機遊戲 **Pikmin Bloom** 的非官方玩法筆記。每個玩家問題用 STE100 簡明中文(一句一件事)回答,**每一條都註明出處**。

```
大分類(7)→ 子分類(24)→ 玩家問題(47)→ 出處(A 官方 / B Pikipedia)
```

首頁是一個走路小遊戲,同時是整站的網站地圖。

**架構**:本機收集台 `Py/desk.py`(撰寫)+ `Py/build_site.py`(靜態建站)+ GitHub Actions(push 後驗證出處與建站)+ GitHub Pages。全部免費,零第三方依賴。

## 檔案

| 檔 | 說明 |
|---|---|
| `Docs/topics.md` | 分類與玩家問題(含來源、難度、待證),**唯一要手改的脈絡檔** |
| `Docs/glossary.md` | STE100 詞彙表(官方繁中用語,一詞一義) |
| `Docs/knowledge.json` | 每題的答案與出處(收集台寫入) |
| `Docs/images.md` + `Docs/images.json` | 圖片授權規則與登記簿;`assets/img/` 全是原創 SVG |
| `Docs/research/why_fun.md` | 研究:為什麼好玩、為什麼紅 |
| `Py/desk.py` + `Py/desk.html` | 收集台 |
| `Py/ste.py` | STE100 檢查 |
| `Py/verify_sources.py` | 出處連結驗證 |
| `Py/build_site.py` | 建站 |
| `.github/workflows/build.yml` | push 改到資料時驗證出處 + 建站 |

## 本地預覽

```bash
python3 -m http.server 8766
```

開 http://localhost:8766/ 。

## 寫一題、建一次站

```bash
python3 Py/desk.py
```

開 http://127.0.0.1:8767/ 寫答案並存入,然後:

```bash
python3 Py/verify_sources.py && python3 Py/build_site.py
```

## 新增玩家問題

在 `Docs/topics.md` 對應子分類下加一行 `- 玩家問題 (slug) | pikipedia:頁名; 官方網址`,再到收集台寫答案。

## 授權

- 程式碼 MIT。
- 本站文字與插畫採 CC BY-SA 4.0;部分內容轉述自 [Pikipedia](https://www.pikminwiki.com/)(CC BY-SA 4.0)與官方說明,每條都附出處。
- 非官方粉絲網站,與任天堂、Niantic、Scopely 無關。Pikmin Bloom 遊戲 © Niantic / Scopely;皮克敏角色、美術、音樂 © Nintendo。
