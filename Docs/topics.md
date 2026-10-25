# 拔拔道場・主題脈絡與收集佇列

> **這是唯一需要人工維護的知識脈絡檔。**
> 網站的「道場地圖」(主題分類)、每條知識歸哪一類、每週要去抓哪些頁面,全部由這一個檔決定。
>
> 格式規則(腳本 `Py/collect_pikipedia.py` 會解析):
>
> - `## 數字. 主題中文名 (slug) · 預設難度` — 一個主題一段。slug 只用英文小寫,會變成網址 `topics/<slug>.html`。
> - 主題下第一行 `> ...` 是主題說明(顯示在網站上),只能一行。
> - 選配:`>> en: 英文主題名 — 英文說明` 給英文版用(說明可省)。英文不要寫進 `##` 標題。
> - `- Pikipedia 頁名 | 中文標題 | 難度(可省略)` — 一行一個待收集頁面。頁名要跟 Pikipedia 網址一致(空白可用空白)。
> - 難度只有三級:`入門`、`進階`、`達人`。省略就用主題預設。難度只能放第 3 欄。
> - 選配具名欄位放在最後:`先讀=Pikipedia 頁名`(跨主題前置建議)。例:`- Purple Pikmin | 紫色皮克敏 | 進階 | 先讀=Red Pikmin`
> - 第一個 `##` 之後,認不得的行會讓收集與建站直接報錯(附行號),不會默默略過。
> - 刪掉一行不會刪掉已收集的條目(資料在 `Docs/knowledge.json`);要下架請在 build 前把該條目 `hidden` 設 true。
>
> 脈絡設計原則:**由淺到深、由物到事**。先認識角色(皮克敏、生物),再學怎麼用(戰術),最後才是世界觀考據。

## 1. 入門基礎 (basics) · 入門
> 第一次接觸皮克敏要先知道的事:這是什麼遊戲、基本單位是什麼、一天怎麼過。
- Pikmin series | 皮克敏系列總覽
- Pikmin family | 皮克敏是什麼(物種總覽)
- Onion | 洋蔥(皮克敏的母艦)
- Leader | 隊長(玩家操作的角色)
- Day | 一天的循環與日落
- Pellet | 顆粒(增加皮克敏的基本資源)

## 2. 皮克敏圖鑑 (pikmin) · 入門
> 各色皮克敏的特性、免疫與用途。選對顏色就是成功的一半。
- Red Pikmin | 紅色皮克敏
- Yellow Pikmin | 黃色皮克敏
- Blue Pikmin | 藍色皮克敏
- Purple Pikmin | 紫色皮克敏 | 進階
- White Pikmin | 白色皮克敏 | 進階
- Rock Pikmin | 岩石皮克敏 | 進階
- Winged Pikmin | 飛行皮克敏 | 進階
- Ice Pikmin | 冰凍皮克敏 | 進階
- Glow Pikmin | 發光皮克敏 | 進階
- Bulbmin | 寄生皮克敏 | 達人

## 3. 原生生物 (creatures) · 進階
> PNF-404 上的生物圖鑑:常見敵人、頭目與牠們的弱點。
- Bulborb | 查比(大嘴怪)
- Fiery Blowhog | 噴火豬
- Dwarf Bulborb | 小查比
- Breadbug | 麵包蟲
- Burrowing Snagret | 鑽地鷺(蛇鳥)
- Emperor Bulblax | 帝王查比
- Waterwraith | 水幽靈 | 達人
- Smoky Progg | 煙霧蛙 | 達人

## 4. 寶物與收集 (collectibles) · 入門
> 每代要收的東西不一樣:太空船零件、寶物、水果、遇難者。
- Ship part | 太空船零件(一代)
- Treasure | 寶物(二代、四代)
- Fruit | 水果(三代)
- Castaway | 遇難者(四代)
- Piklopedia | 皮克敏圖鑑系統

## 5. 戰術與攻略 (strategy) · 進階
> 怎麼把皮克敏用得又快又省:投擲、衝鋒、分隊、段取り(Dandori)。
- Throw | 投擲
- Charge | 衝鋒
- Swarm | 群攻(一、二代)
- Dandori | 段取り(四代的效率哲學)
- Multitasking | 多工分隊
- Pikmin extinction | 皮克敏滅絕(全滅機制)
- Oatchi | 歐慶(四代救難犬)
- Spicy spray | 辣椒噴霧(紅色強化)
- Bitter spray | 苦味噴霧(石化) | 達人

## 6. 世界觀與考據 (lore) · 達人
> 角色、星球與公司:歐利瑪、Hocotate 運輸、PNF-404 的真相。
- Captain Olimar | 歐利瑪船長
- Louie | 路易
- Hocotate Freight | Hocotate 運輸公司
- PNF-404 | PNF-404(皮克敏的星球)
- Hocotate | Hocotate 星
- Koppai | Koppai 星(三代)
- Alph | 阿爾夫
- Brittany | 布莉特妮
- Charlie | 查理

## 7. 系列作品 (games) · 入門
> 每一代的定位與差異,想入坑從哪一代開始。
- Pikmin (game) | 皮克敏 1(2001)
- Pikmin 2 | 皮克敏 2(2004)
- Pikmin 3 | 皮克敏 3(2013)
- Pikmin 4 | 皮克敏 4(2023)
- Pikmin Bloom | Pikmin Bloom(手機)
- Hey! Pikmin | Hey! Pikmin(3DS)
