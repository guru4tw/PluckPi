// 首頁站名下的「X版:一句話」。每 1 分鐘自動換一句,前後 ‹ › 手動切上一句/下一句:句子洗牌輪完 31 句才重複,換場特效也每次抽、不連續重複。
// 句子由 build_site.py 從 Docs/pikmin_bloom_oneliners.md 放進 data-quips;關掉 JS 時看到建站時的第一句。
(() => {
  const box = document.querySelector(".quip");
  if (!box) return;
  let quips;
  try { quips = JSON.parse(box.dataset.quips); } catch { return; }
  if (!quips || quips.length < 2) return;
  const EVERY = 60 * 1000;
  const GLYPHS = "花葉苗芽菇瓣步拔種";
  const still = matchMedia("(prefers-reduced-motion: reduce)");
  const $sr = box.querySelector(".sr"), $label = box.querySelector("b"), $q = box.querySelector(".q");
  const mascot = document.querySelector(".brand img");
  const rand = (a, b) => a + Math.random() * (b - a);
  const pick = a => a[Math.floor(Math.random() * a.length)];

  // 洗牌輪播:一輪內不重複,新一輪的第一句也不會跟上一句一樣
  let deck = [], last = -1;
  function next() {
    if (!deck.length) {
      deck = quips.map((_, i) => i).sort(() => Math.random() - .5);
      if (deck[deck.length - 1] === last) deck.unshift(deck.pop());
    }
    return last = deck.pop();
  }

  function chars(text, fx) {
    $q.className = `q fx-${fx}`;
    $q.textContent = "";
    [...text].forEach((c, i) => {
      const s = document.createElement("span");
      s.textContent = c;
      s.style.setProperty("--i", i);
      s.style.setProperty("--dx", rand(-120, 120).toFixed(0) + "px");
      s.style.setProperty("--dy", rand(-60, 60).toFixed(0) + "px");
      s.style.setProperty("--r", rand(-200, 200).toFixed(0) + "deg");
      $q.appendChild(s);
    });
    return [...$q.children];
  }

  // 每種特效:把 text 放進 $q。CSS 動畫的特效只要分字加 class;打字與亂碼由 JS 逐格改字
  const FX = {
    sprout: t => chars(t, "sprout"),     // 每個字像花苗從土裡冒出來
    petals: t => chars(t, "petals"),     // 字像花瓣從四處飄回原位
    hop:    t => chars(t, "hop"),        // 字一個一個跳進來,像走路
    drop:   t => chars(t, "drop"),       // 整句從上面掉下來彈一下
    type(t) {                            // 一個字一個字打出來
      const ss = chars(t, "type");
      ss.forEach((s, i) => setTimeout(() => s.classList.add("on"), 45 * i));
    },
    scramble(t) {                        // 先是一串花葉菇,再一格一格變成真句子
      const ss = chars(t, "scramble"), real = [...t];
      let tick = 0;
      const id = setInterval(() => {
        tick++;
        ss.forEach((s, i) => { s.textContent = i < tick - 6 ? real[i] : (real[i] === " " ? " " : pick(GLYPHS)); });
        if (tick - 6 > real.length) clearInterval(id);
      }, 40);
    },
  };
  const NAMES = Object.keys(FX);
  let lastFx = "";

  function show(i, animate) {
    const [label, text] = quips[i];
    $sr.textContent = `${label}:${text}`;
    $label.textContent = label;
    if (!animate || still.matches) { $q.className = "q"; $q.textContent = text; return; }
    let fx;
    do fx = pick(NAMES); while (fx === lastFx);
    lastFx = fx;
    FX[fx](text);
    $label.classList.remove("pop"); void $label.offsetWidth; $label.classList.add("pop");
    if (mascot) { mascot.classList.remove("hop"); void mascot.offsetWidth; mascot.classList.add("hop"); }
  }

  // 看過的句子記成一串,‹ 往回翻、› 往前翻;翻到最新一句再按 › 就抽新的
  const seen = [next()];
  let pos = 0, busy = false, timer = 0;

  function go(step) {
    if (busy) return;
    if (step < 0 && pos === 0) return;
    pos += step;
    if (pos === seen.length) seen.push(next());
    if (still.matches) { show(seen[pos], false); return; }
    busy = true;
    box.classList.add("out");                  // 舊句被拔走
    setTimeout(() => { box.classList.remove("out"); show(seen[pos], true); busy = false; }, 380);
  }

  // 自動每分鐘往下一句;手動按過就從那一刻重新計時,不會剛按完就被換掉
  function restart() {
    clearInterval(timer);
    timer = setInterval(() => { if (!document.hidden) go(1); }, EVERY);
  }

  box.querySelectorAll(".qnav").forEach(btn => {
    btn.hidden = false;
    btn.addEventListener("click", () => { go(+btn.dataset.step); restart(); });
  });

  show(seen[0], true);                         // 進站就抽一句,不固定是第一句
  restart();
})();
