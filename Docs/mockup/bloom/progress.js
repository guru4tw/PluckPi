// 讀完一個子分類就種一朵花。只存在這台瀏覽器(localStorage),讀不到也不影響網站使用。
(() => {
  const KEY = "pluckpi.read";
  const load = () => { try { return new Set(JSON.parse(localStorage.getItem(KEY) || "[]")); } catch { return new Set(); } };
  const save = s => { try { localStorage.setItem(KEY, JSON.stringify([...s])); } catch {} };
  const read = load();

  // 網站地圖與大綱頁:讀過的子分類亮出小花
  document.querySelectorAll("[data-topic]").forEach(el => el.classList.toggle("read", read.has(el.dataset.topic)));
  document.querySelectorAll("[data-count-read]").forEach(el => {
    const slugs = el.dataset.countRead.split(",");
    const n = slugs.filter(s => read.has(s)).length;
    el.textContent = n ? `已種 ${n}/${slugs.length} 朵` : "";
  });

  // 子分類頁:「讀完了」按鈕
  const box = document.querySelector("[data-done]");
  if (box) {
    const slug = box.dataset.done, btn = box.querySelector("button");
    const paint = () => {
      const on = read.has(slug);
      box.classList.toggle("on", on);
      btn.setAttribute("aria-pressed", on);
      btn.textContent = on ? "已種一朵花" : "讀完了,種一朵花";
    };
    btn.addEventListener("click", () => { read.has(slug) ? read.delete(slug) : read.add(slug); save(read); paint(); });
    paint();
  }
})();
