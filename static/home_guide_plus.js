(function () {
  const rail = document.getElementById("home-guide-rail");
  if (!rail) return;

  const panel = rail.querySelector(".home-guide-panel");
  const items = Array.from(rail.querySelectorAll(".home-guide-item"));
  if (!panel || !items.length) return;

  let progressWrap = panel.querySelector(".home-guide-progress");
  let progressText = panel.querySelector(".home-guide-progress-text");

  if (!progressWrap) {
    progressWrap = document.createElement("div");
    progressWrap.className = "home-guide-progress";
    progressWrap.innerHTML = '<div id="home-guide-progress-bar"></div>';
    panel.insertBefore(progressWrap, items[0]);
  }

  if (!progressText) {
    progressText = document.createElement("div");
    progressText.className = "home-guide-progress-text";
    panel.insertBefore(progressText, items[0]);
  }

  const progressBar = progressWrap.querySelector("div") || progressWrap;

  function getActiveIndex() {
    const idx = items.findIndex((x) => x.classList.contains("active"));
    return idx >= 0 ? idx : 0;
  }

  function syncProgress() {
    const idx = getActiveIndex();
    const ratio = items.length > 1 ? idx / (items.length - 1) : 1;
    if (progressBar) progressBar.style.width = `${Math.round(ratio * 100)}%`;
    if (progressText) progressText.textContent = `${idx + 1} / ${items.length}`;
  }

  function jumpDelta(delta) {
    const cur = getActiveIndex();
    const next = Math.max(0, Math.min(items.length - 1, cur + delta));
    if (next === cur) return;
    items[next].click();
  }

  window.addEventListener("keydown", (e) => {
    const tag = (e.target && e.target.tagName ? e.target.tagName : "").toLowerCase();
    if (tag === "input" || tag === "textarea" || tag === "select") return;

    if (e.key === "ArrowDown" || e.key === "PageDown") {
      e.preventDefault();
      jumpDelta(1);
      return;
    }
    if (e.key === "ArrowUp" || e.key === "PageUp") {
      e.preventDefault();
      jumpDelta(-1);
    }
  });

  let touchStartY = null;
  window.addEventListener(
    "touchstart",
    (e) => {
      const t = e.touches && e.touches[0];
      if (!t) return;
      touchStartY = t.clientY;
    },
    { passive: true }
  );

  window.addEventListener(
    "touchend",
    (e) => {
      if (touchStartY === null) return;
      const t = e.changedTouches && e.changedTouches[0];
      if (!t) return;
      const dy = t.clientY - touchStartY;
      touchStartY = null;
      if (Math.abs(dy) < 40) return;
      if (dy < 0) jumpDelta(1);
      else jumpDelta(-1);
    },
    { passive: true }
  );

  const observer = new MutationObserver(syncProgress);
  items.forEach((el) => {
    observer.observe(el, { attributes: true, attributeFilter: ["class"] });
    el.addEventListener("click", () => {
      window.setTimeout(syncProgress, 50);
    });
  });

  syncProgress();
})();
