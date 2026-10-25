// 首頁走路體驗(草稿)。滑動 = 走路:留下腳印、種出花;每 1000 步長出一株花苗,點它拔出芽芽,芽芽跟著手指走。
// 只是小遊戲,不寫任何「為什麼好玩」的說明。關掉動畫(prefers-reduced-motion)時照樣能玩,只是沒有彈跳。
(() => {
  const field = document.getElementById("field");
  if (!field) return;
  const IMG = field.dataset.img;
  const FLOWERS = ["flower-coral", "flower-lilac", "flower-sun", "flower-mint"];
  const STEP_PX = 1;            // 每 1 px 移動算 1 步(手機上來回滑三四次就有 1000 步)
  const SEED_AT = 1000;          // 幾步長一株花苗(遊戲裡紅色花苗是 1,000 步)
  const MAX_BUDDIES = 5, MAX_SPRITES = 160;
  const $steps = field.querySelector("[data-steps]"), $bar = field.querySelector(".bar i"),
        $hint = field.querySelector(".hint");
  let steps = 0, sinceSeed = 0, last = null, sinceFoot = 0, sinceFlower = 0, foot = 0;
  let seed = null, buddies = [], pointer = {x: 0, y: 0};

  function sprite(cls, src, x, y) {
    const el = new Image();
    el.src = `${IMG}/${src}.svg`; el.alt = ""; el.className = `sprite ${cls}`;
    el.style.left = x + "px"; el.style.top = y + "px";
    field.appendChild(el);
    const all = field.querySelectorAll(".sprite");
    if (all.length > MAX_SPRITES) all[0].remove();
    return el;
  }

  function addSteps(n, x, y) {
    steps += n; sinceSeed += n;
    $steps.textContent = Math.floor(steps).toLocaleString();
    $bar.style.width = Math.min(100, sinceSeed / SEED_AT * 100) + "%";
    if (sinceSeed >= SEED_AT && !seed) growSeed(x, y);
  }

  function growSeed(x, y) {
    seed = document.createElement("button");
    seed.className = "seed"; seed.type = "button";
    seed.setAttribute("aria-label", "花苗長好了,點一下拔出來");
    seed.innerHTML = `<img src="${IMG}/seedling.svg" alt="">`;
    seed.style.left = x + "px"; seed.style.top = y + "px";
    seed.addEventListener("pointerdown", e => e.stopPropagation());
    seed.addEventListener("click", pluck);
    field.appendChild(seed);
    $hint.textContent = "花苗長好了,點它";
  }

  function pluck() {
    const x = parseFloat(seed.style.left), y = parseFloat(seed.style.top);
    seed.remove(); seed = null; sinceSeed = 0; $bar.style.width = "0%";
    const b = new Image();
    b.src = `${IMG}/${buddies.length % 2 ? "mascot-bloom" : "mascot-bud"}.svg`; b.alt = "";
    b.className = "buddy new"; b.style.left = x + "px"; b.style.top = y + "px";
    field.appendChild(b);
    buddies.push(b);
    if (buddies.length > MAX_BUDDIES) buddies.shift().remove();
    $hint.textContent = buddies.length === 1 ? "牠會跟著你走" : `隊伍裡有 ${buddies.length} 隻`;
    follow();
  }

  function follow() {
    // 一隻跟一隻,排成小隊
    buddies.forEach((b, i) => {
      const ang = Math.PI * 0.75 + i * 0.5, r = 34 + i * 10;
      b.style.left = pointer.x + Math.cos(ang) * r + "px";
      b.style.top = pointer.y + Math.sin(ang) * r + 20 + "px";
    });
  }

  function walk(x, y) {
    pointer = {x, y};
    if (last) {
      const d = Math.hypot(x - last.x, y - last.y);
      if (d > 80) { last = {x, y}; return; }        // 跳太遠視為重新落指,不算步數
      sinceFoot += d; sinceFlower += d;
      addSteps(d * STEP_PX, x, y);
      if (sinceFoot > 26) {
        sinceFoot = 0; foot++;
        const ang = Math.atan2(y - last.y, x - last.x) + Math.PI / 2;
        const off = foot % 2 ? 7 : -7;
        const fp = sprite("fp", "footprints", x + Math.cos(ang) * off, y + Math.sin(ang) * off);
        fp.style.transform = `translate(-50%,-50%) rotate(${ang * 180 / Math.PI}deg)`;
      }
      if (sinceFlower > 60) {
        sinceFlower = 0;
        sprite("fl", FLOWERS[Math.floor(Math.random() * FLOWERS.length)],
               x + (Math.random() - .5) * 26, y + (Math.random() - .5) * 26);
      }
    }
    last = {x, y};
    follow();
  }

  const pos = e => { const r = field.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
  let down = false;
  field.addEventListener("pointerdown", e => { down = true; last = null; field.setPointerCapture(e.pointerId); walk(...pos(e)); });
  field.addEventListener("pointermove", e => { if (down || e.pointerType === "mouse") walk(...pos(e)); });
  field.addEventListener("pointerup", () => { down = false; last = null; });
  field.addEventListener("pointerleave", () => { last = null; });

  // 不能滑動的人(鍵盤、輔助科技)用按鈕走路
  field.querySelector(".walk-btn").addEventListener("click", e => {
    e.stopPropagation();
    const r = field.getBoundingClientRect();
    let x = 40 + Math.random() * (r.width - 80), y = 60 + Math.random() * (r.height - 120);
    last = {x, y};
    for (let i = 0; i < 30; i++) { x += 7 + Math.random() * 4; y += (Math.random() - .5) * 8; walk(Math.min(x, r.width - 20), y); }
  });
})();
