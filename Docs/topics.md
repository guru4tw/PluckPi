# 拔拔道場・分類脈絡與收集佇列(Pikmin Bloom)

> **這是唯一需要人工維護的知識脈絡檔。** 網站首頁的網站地圖、每個大分類的大綱頁、子分類頁、
> 每條知識歸哪一類,全部由這個檔決定。範圍只有手機遊戲 Pikmin Bloom。
>
> 格式(`Py/common.py` 的 `parse_categories` 解析,認不得的行直接報錯並附行號):
>
> - `# 數字. 大分類中文名 (slug)` —— 大分類。下一行 `> ...` 是一行大綱(首頁與大綱頁顯示)。
> - `## 大分類號.子分類號 子分類中文名 (slug) · 預設難度` —— 子分類,必須在它的大分類底下。
>   下一行 `> ...` 是一句話說明。子分類的順序就是建議閱讀順序。
> - `- 玩家問題 (條目slug) | 來源 | 難度(可省) | key=value…` —— 條目,一行一個玩家問題。
>   - 來源:`pikipedia:頁名` 或完整網址,多個用 `;` 分開;每條至少要有一個 A(官方)或 B(Pikipedia)來源。
>   - 難度:`入門` / `進階` / `達人`,只能放第 3 欄,省略就用子分類預設。
>   - 具名欄位:`先讀=條目slug`、`狀態=待證`(只有一個來源或來源不夠硬)、`期限=YYYY-MM-DD`(活動類)。
> - 選配 `>> en: 英文名 — 英文說明`,放在大分類或子分類標題下一行。
> - slug 只用英文小寫、數字、`-`;大分類、子分類、條目的 slug 全站不可重複。條目 slug 就是網址,定了不改。
>
> 用語以遊戲內繁中官方用語為準,見 `Docs/glossary.md`。研究依據見 `Docs/research/why_fun.md`。
> 大分類順序依「新手第一週」:先讓計步跑起來,再成長、認識皮克敏、和別人一起玩、留下記錄;
> 冷知識與安全設定放最後,但安全的重點會在「開始玩」先提一次。

# 1. 開始玩 (start)
> 裝好遊戲、打開計步、拔出第一隻皮克敏。第一天只要做五件事。

## 1.1 認識這個遊戲 (about) · 入門
> 一分鐘知道 Pikmin Bloom 在玩什麼。
- Pikmin Bloom 是什麼遊戲? (what-is-bloom) | pikipedia:Pikmin Bloom; https://pikminbloom.com/zh_hant/
- 要花錢才能玩嗎? (is-it-free) | pikipedia:Pikmin Bloom; https://www.nintendo.com/au/games/mobile/pikmin-bloom/

## 1.2 下載與設定 (setup) · 入門
> 裝好 app、登入帳號、打開計步權限。
- 怎麼登入?登入失敗怎麼辦? (sign-in) | https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/2360-help-with-sign-in-issues/ | 狀態=待證
- iPhone 的計步權限要怎麼開? (step-permission-ios) | https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/2861-my-steps-aren-t-being-counted-correctly-ios/ | 狀態=待證
- Android 要怎麼選計步方式? (step-permission-android) | https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/2862-my-steps-aren-t-being-counted-correctly-android/; https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/3162-faq-and-known-issues/ | 狀態=待證

## 1.3 第一天要做的事 (first-day) · 入門
> 走路、拔皮克敏、餵精華、收花瓣、種花:第一天的五個動作。
- 第一天要做什麼? (first-day-todo) | pikipedia:Pikmin Bloom; https://pikminbloom.com/zh_hant/ | 狀態=待證
- 地圖畫面上的東西各是什麼? (map-screen) | pikipedia:Pikmin Bloom interface | 狀態=待證

# 2. 走路與成長 (grow)
> 走路讓花苗長大,拔出皮克敏,餵精華讓牠開花,再把花瓣種在路上。

## 2.1 步數 (steps) · 入門
> 步數是這個遊戲的燃料。算不到步數,其他都不會動。
- 我走路為什麼沒算到步數? (steps-not-counted) | https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/3162-faq-and-known-issues/; https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/2861-my-steps-aren-t-being-counted-correctly-ios/; https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/2862-my-steps-aren-t-being-counted-correctly-android/
- 背景計步很耗電怎麼辦? (battery) | https://apps.apple.com/us/app/-/id1556357398; https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/3162-faq-and-known-issues/ | 狀態=待證

## 2.2 花苗 (seedlings) · 入門
> 花苗靠步數長大,長好就能拔出皮克敏。
- 花苗要走幾步才會長大? (seedling-steps) | pikipedia:Seedling | 狀態=待證
- 花苗從哪裡來? (seedling-sources) | pikipedia:Seedling; https://scopelyexplore.helpshift.com/hc/en/11-pikmin-bloom/faq/2182-items-and-the-effects/
- 花苗包滿了怎麼辦? (seedling-slots) | pikipedia:Slot; pikipedia:Seedling; https://niantic.helpshift.com/hc/zh/23-pikmin-bloom/faq/3040-storage-size-of-each-item/ | 進階 | 狀態=待證

## 2.3 拔皮克敏 (pluck) · 入門
> 拔出來的皮克敏會加入隊伍,跟著你走。
- 拔出來的皮克敏會做什麼? (after-pluck) | https://pikminbloom.com/zh_hant/; pikipedia:Pikmin Bloom
- 地圖上的皮克敏剪影是什麼? (pikmin-silhouette) | https://pikminbloom.com/news/nov25-icepikmin-welcome | 進階 | 狀態=待證

## 2.4 精華與花瓣 (nectar-petals) · 入門
> 水果變成精華,精華讓皮克敏開花,花開了收花瓣。
- 精華從哪裡來? (nectar-sources) | https://pikminbloom.com/zh_hant/; pikipedia:Pikmin Bloom | 狀態=待證
- 什麼時候餵精華,花瓣收得比較多? (petal-timing) | pikipedia:Pikmin Bloom | 進階 | 狀態=待證

## 2.5 種花 (planting) · 入門
> 邊走邊把花瓣種在地圖上,留下自己的花徑。
- 種花有什麼用? (why-plant) | https://pikminbloom.com/zh_hant/; pikipedia:Pikmin Bloom
- 為什麼我種不了花? (cant-plant) | https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/2877-i-can-t-plant-flowers-1636017814/ | 狀態=待證

## 2.6 等級 (levels) · 進階
> 完成等級任務就升級,升級會開放新的皮克敏和功能。
- 等級怎麼升?最高幾級? (level-up) | pikipedia:Level | 狀態=待證
- 金幣怎麼賺、要花在哪? (coins) | pikipedia:Pikmin Bloom | 狀態=待證

# 3. 認識皮克敏 (pikmin)
> Bloom 有 8 種顏色的皮克敏。跟牠們變熟,牠們會變成穿著發現地點造型的飾品皮克敏。

## 3.1 皮克敏種類 (types) · 入門
> 8 種皮克敏、各在幾級出現。
- Bloom 有哪幾種皮克敏? (pikmin-types) | pikipedia:Seedling; https://pikminbloom.com/news/nov25-icepikmin-welcome | 狀態=待證
- 每種皮克敏在幾級出現? (type-unlock-levels) | pikipedia:Seedling | 狀態=待證

## 3.2 友好度 (friendship) · 入門
> 皮克敏跟你越熟,越會帶禮物回來。
- 友好度怎麼提升? (raise-friendship) | pikipedia:Friendship; https://pikminbloom.com/zh_hant/

## 3.3 飾品皮克敏 (decor) · 進階
> 皮克敏的造型由花苗的發現地點決定,收集最有樂趣的部分。
- 飾品皮克敏是什麼? (what-is-decor) | https://pikminbloom.com/zh_hant/; pikipedia:Decor Pikmin
- 怎麼拿到想要的飾品皮克敏? (get-decor) | pikipedia:Decor Pikmin; pikipedia:Seedling | 狀態=待證
- 怎麼把 Pikmin 4 的飾品花苗送到 Bloom? (pikmin4-link) | https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/5260-how-to-send-the-seedlings-for-decor-pikmin-found-in-pikmin-4-to-pikmin-bloom/ | 達人 | 狀態=待證

# 4. 一起玩 (together)
> 不用約時間也能一起玩:探險、蘑菇、巨大花朵、朋友、活動。

## 4.1 探險 (expeditions) · 入門
> 派皮克敏去遠處搬水果和花苗回來。
- 探險是什麼?會帶回什麼? (what-is-expedition) | pikipedia:Expedition; https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/4926-expedition-snapshots/; https://pikminbloom.com/zh_hant/ | 狀態=待證

## 4.2 蘑菇 (mushrooms) · 進階
> 地圖上的蘑菇要和其他玩家一起打。
- 蘑菇怎麼打? (mushroom-battle) | pikipedia:Mushroom battle; https://pikminbloom.com/zh_hant/ | 狀態=待證
- 打蘑菇有什麼獎勵? (mushroom-rewards) | https://scopelyexplore.helpshift.com/hc/en/11-pikmin-bloom/faq/2158-rewards-for-clearing-mushrooms/; pikipedia:Mushroom battle; https://pikminbloom.com/zh_hant/

## 4.3 巨大花朵 (big-flowers) · 進階
> 地標上的巨大花朵,附近玩家一起種花才會開。
- 巨大花朵怎麼讓它開? (bloom-big-flower) | pikipedia:Big Flower; https://pikminbloom.com/zh_hant/; pikipedia:Expedition | 狀態=待證

## 4.4 朋友 (friends) · 入門
> 加朋友、寄明信片、一起做每週挑戰。
- 怎麼加朋友? (add-friend) | pikipedia:Friend | 狀態=待證
- 每週挑戰怎麼玩? (weekly-challenge) | https://pikminbloom.com/zh_hant/; pikipedia:Weekly challenge; pikipedia:Pikmin Bloom

## 4.5 活動與社群日 (events) · 進階
> 每月的社群日和實體活動。活動內容會變,每條都標查閱日。
- 社群日要做什麼? (community-day) | pikipedia:Community Day; pikipedia:Expedition | 狀態=待證
- 實體活動怎麼報名? (live-events) | https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/5200-registering-for-live-events/; https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/3886/; https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/4804/ | 狀態=待證

# 5. 記錄與分享 (memories)
> 遊戲幫你記住每一天:生活記錄和明信片。

## 5.1 生活記錄 (lifelog) · 入門
> 每天晚上回顧步數、路線和照片。
- 生活記錄會記下什麼? (what-is-lifelog) | https://pikminbloom.com/zh_hant/; pikipedia:Lifelog

## 5.2 明信片 (postcards) · 入門
> 皮克敏帶回的風景,可以寄給朋友。
- 明信片從哪裡來?怎麼寄? (send-postcard) | pikipedia:Postcard; pikipedia:Friend; https://pikminbloom.com/zh_hant/; https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/4926-expedition-snapshots/ | 狀態=待證
- 明信片滿了怎麼辦? (postcard-storage) | https://pikminbloom.com/news/nov25-icepikmin-welcome; pikipedia:Postcard; https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/4926-expedition-snapshots/ | 進階 | 狀態=待證

# 6. 冷知識 (trivia)
> 跟玩法無關、但玩過的人會想知道的事。每條都有出處,只有一個來源的標「待證」。

## 6.1 遊戲的誕生 (origins) · 入門
> 這款遊戲怎麼來的、開發者怎麼看它。
- 這是系列第一款沒有敵人的皮克敏遊戲? (no-enemies) | pikipedia:Pikmin Bloom | 狀態=待證
- 上市時開放了多少個市場? (launch-markets) | pikipedia:Pikmin Bloom | 狀態=待證
- Pikmin 4 的開發者怎麼看 Bloom? (devs-on-bloom) | https://www.nintendo.com/us/whatsnew/ask-the-developer-vol-10-pikmin-4-part-3/ | 狀態=待證

## 6.2 地圖與數字 (numbers) · 入門
> 地圖上的設計從哪來、全世界的玩家走了多遠。
- 巨大花朵的位置是怎麼決定的? (big-flower-locations) | pikipedia:Big Flower | 狀態=待證
- 綁任天堂帳號會拿到什麼? (nintendo-account-gift) | pikipedia:Pikmin Bloom | 狀態=待證

# 7. 安全與設定 (safety)
> 走路要看路;花徑和分享畫面會透露你去過哪裡,先設好隱私。

## 7.1 走路安全 (walk-safe) · 入門
> 邊走邊玩要注意的事。
- 走路玩的時候要注意什麼? (walking-safety) | https://niantic.helpshift.com/hc/zh-hant/23-pikmin-bloom/section/259-safety-security/ | 狀態=待證

## 7.2 隱私 (privacy) · 入門
> 花徑別人看得到。設好私人區域,再決定要分享什麼。
- 別人看得到我的花徑嗎? (trail-visibility) | https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/2874-information-shared-with-others/; https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/3277-privacy-zone/
- 怎麼設私人區域? (privacy-zone) | https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/3277-privacy-zone/ | 狀態=待證
- 朋友看得到我的哪些資料? (shared-info) | https://niantic.helpshift.com/hc/en/23-pikmin-bloom/faq/2874-information-shared-with-others/ | 狀態=待證

## 7.3 帳號規則 (account) · 進階
> 用假定位或自動走路會被停權。
- 用假 GPS 或自動走路會怎樣? (spoofing) | https://niantic.helpshift.com/hc/zh-hant/23-pikmin-bloom/faq/2868-three-strike-discipline-policy/; https://niantic.helpshift.com/hc/zh-hant/23-pikmin-bloom/section/259-safety-security/ | 狀態=待證
