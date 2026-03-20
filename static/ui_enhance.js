(function () {
  const storageKey = "kq_fx_off";
  const cinematicKey = "kq_fx_cinematic";
  const bar = document.getElementById("global-loadbar");
  let timer = null;
  let progress = 0;

  function applyFxPref() {
    try {
      const off = localStorage.getItem(storageKey) === "1";
      document.body.classList.toggle("fx-lite-off", off);
      const cinematicRaw = localStorage.getItem(cinematicKey);
      const cinematic = cinematicRaw === null ? true : cinematicRaw === "1";
      document.body.classList.toggle("fx-cinematic", cinematic);
    } catch (_) {
      document.body.classList.add("fx-cinematic");
    }
  }

  function setBar(pct) {
    if (!bar) return;
    const v = Math.max(0, Math.min(100, pct));
    bar.style.transform = `scaleX(${v / 100})`;
  }

  function startLoadBar() {
    if (!bar) return;
    if (timer) window.clearInterval(timer);
    progress = 8;
    bar.classList.remove("done");
    bar.classList.add("show");
    setBar(progress);
    timer = window.setInterval(() => {
      if (progress >= 88) return;
      progress += Math.max(0.6, (92 - progress) * 0.08);
      setBar(progress);
    }, 90);
  }

  function finishLoadBar() {
    if (!bar) return;
    if (timer) {
      window.clearInterval(timer);
      timer = null;
    }
    progress = 100;
    setBar(progress);
    window.setTimeout(() => {
      bar.classList.add("done");
      bar.classList.remove("show");
      setBar(0);
    }, 220);
  }

  function setCinematic(enabled) {
    const on = !!enabled;
    document.body.classList.toggle("fx-cinematic", on);
    try {
      localStorage.setItem(cinematicKey, on ? "1" : "0");
    } catch (_) {}
  }

  function getCinematic() {
    return document.body.classList.contains("fx-cinematic");
  }

  function isTopLevelWindow() {
    try {
      return window.top === window.self;
    } catch (_) {
      return false;
    }
  }

  function normalizePath(pathname) {
    const p = String(pathname || "/").trim();
    return p || "/";
  }

  function shouldRunAnalysisEntry(moduleName, path) {
    return moduleName === "analysis" && (path === "/analysis" || path === "/analysis/");
  }

  function shouldRunHomeEntry(moduleName, path) {
    return moduleName === "home" && path === "/";
  }

  function clearHomeEntryMask() {
    if (!document.body) return;
    document.body.classList.remove("home-entry-prehide");
    document.body.classList.remove("home-entry-loading");
  }

  function createAnalysisSplash() {
    if (!document.body) return null;
    const old = document.querySelector(".entry-splash");
    if (old) old.remove();
    const splash = document.createElement("div");
    splash.className = "entry-splash entry-analysis";
    splash.innerHTML = `
      <div class="entry-card">
        <div class="entry-title">Quantum Platform Boot</div>
        <div class="entry-sub">正在加载分析模块...</div>
        <div class="entry-bar"><div></div></div>
        <div class="entry-foot">
          <span data-role="status">初始化图形引擎</span>
          <span data-role="percent">0%</span>
        </div>
      </div>
    `;
    document.body.appendChild(splash);
    return splash;
  }

  function createHomeSplash() {
    if (!document.body) return null;
    const old = document.querySelector(".entry-splash");
    if (old) old.remove();
    document.body.classList.add("home-entry-loading");
    const splash = document.createElement("div");
    splash.className = "entry-splash entry-home";
    splash.innerHTML = `
      <div class="entry-home-wrap">
        <div class="entry-home-title">QUANTUM PLATFORM</div>
        <div class="entry-home-sub">LOADING HOME SCENE</div>
        <div class="entry-home-bar"><div></div></div>
        <div class="entry-home-foot">
          <span data-role="status">正在初始化主页背景</span>
          <span data-role="percent">0%</span>
        </div>
        <div class="entry-home-message" data-role="start" role="button" tabindex="0" aria-live="polite" aria-label="Tap to start audio">
          <div class="entry-home-welcome">WELCOME</div>
          <div class="entry-home-tap">TAP TO START</div>
          <div class="entry-home-transcript">Controls are handed to you, pilot.</div>
        </div>
      </div>
    `;
    document.body.appendChild(splash);
    return splash;
  }

  function updateAnalysisStatus(splash, pct) {
    const statusEl = splash.querySelector('[data-role="status"]');
    if (!statusEl) return;
    if (pct < 28) {
      statusEl.textContent = "初始化图形引擎";
      return;
    }
    if (pct < 55) {
      statusEl.textContent = "加载量子公式资源";
      return;
    }
    if (pct < 82) {
      statusEl.textContent = "构建交互可视化组件";
      return;
    }
    if (pct < 100) {
      statusEl.textContent = "同步界面状态";
      return;
    }
    statusEl.textContent = "就绪";
  }

  function updateHomeStatus(splash, pct) {
    const statusEl = splash.querySelector('[data-role="status"]');
    if (!statusEl) return;
    if (pct < 30) {
      statusEl.textContent = "正在初始化主页背景";
      return;
    }
    if (pct < 62) {
      statusEl.textContent = "正在载入可视化组件";
      return;
    }
    if (pct < 90) {
      statusEl.textContent = "正在同步交互动画";
      return;
    }
    statusEl.textContent = "主页就绪";
  }

  function animateSplash(splash, barSelector, statusUpdater, duration, onComplete) {
    if (!splash) return;
    const barInner = splash.querySelector(barSelector);
    const pctEl = splash.querySelector('[data-role="percent"]');
    if (!barInner || !pctEl) return;

    const start = performance.now();

    function step(now) {
      const t = Math.max(0, Math.min(1, (now - start) / duration));
      const eased = 1 - Math.pow(1 - t, 2.4);
      const pct = Math.round(eased * 100);
      barInner.style.width = `${pct}%`;
      pctEl.textContent = `${pct}%`;
      statusUpdater(splash, pct);
      if (t < 1) {
        window.requestAnimationFrame(step);
        return;
      }
      if (typeof onComplete === "function") {
        onComplete(splash);
        return;
      }
      window.setTimeout(() => {
        splash.classList.add("done");
        window.setTimeout(() => splash.remove(), 480);
      }, 180);
    }

    window.requestAnimationFrame(step);
  }

  function runAnalysisSplash() {
    const splash = createAnalysisSplash();
    const duration = 1050 + Math.random() * 550;
    animateSplash(splash, ".entry-bar > div", updateAnalysisStatus, duration);
  }

  function finalizeHomeSplash(splash, delayMs) {
    const delay = Math.max(0, Number(delayMs) || 0);
    window.setTimeout(() => {
      splash.classList.add("done");
      clearHomeEntryMask();
      document.body.classList.remove("home-entry-loading");
      document.body.classList.add("home-entry-reveal");
      window.setTimeout(() => {
        document.body.classList.remove("home-entry-reveal");
      }, 1600);
      window.setTimeout(() => splash.remove(), 480);
    }, delay);
  }

  function runHomeReadySequence(splash) {
    if (!splash) return;
    splash.classList.add("is-ready");
    const startArea = splash.querySelector('[data-role="start"]');
    const audio = new Audio(encodeURI("/static/pilot control.wav"));
    audio.preload = "auto";
    audio.volume = 1.0;

    let started = false;

    function startSequence() {
      if (started) return;
      started = true;
      splash.classList.add("is-speaking");
      if (startArea) {
        startArea.classList.add("is-disabled");
        startArea.setAttribute("aria-disabled", "true");
      }
      const p = audio.play();
      if (p && typeof p.catch === "function") {
        p.catch(() => {});
      }
      finalizeHomeSplash(splash, 3000);
    }

    function onKeydown(e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        startSequence();
      }
    }

    if (startArea) {
      startArea.addEventListener("click", startSequence);
      startArea.addEventListener("keydown", onKeydown);
    }

    splash.addEventListener("click", startSequence);
    document.addEventListener("keydown", onKeydown);
  }

  function runHomeSplash() {
    const splash = createHomeSplash();
    const duration = 1800 + Math.random() * 1000;
    animateSplash(splash, ".entry-home-bar > div", updateHomeStatus, duration, runHomeReadySequence);
  }

  function runEntrySplash() {
    const moduleName = document.body.getAttribute("data-module") || "default";
    const path = normalizePath(window.location.pathname);
    const isHomeEntry = shouldRunHomeEntry(moduleName, path);
    const isAnalysisEntry = shouldRunAnalysisEntry(moduleName, path);

    if (!isTopLevelWindow()) {
      if (moduleName === "home") clearHomeEntryMask();
      return;
    }

    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      if (isHomeEntry) clearHomeEntryMask();
      return;
    }
    if (isAnalysisEntry) {
      runAnalysisSplash();
      return;
    }
    if (isHomeEntry) {
      runHomeSplash();
      return;
    }
    if (moduleName === "home") clearHomeEntryMask();
  }

  function bootEnhance() {
    applyFxPref();
    runEntrySplash();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootEnhance, { once: true });
  } else {
    bootEnhance();
  }

  window.addEventListener("pageshow", (e) => {
    if (e.persisted) runEntrySplash();
  });

  window.KQEnhance = {
    startLoadBar,
    finishLoadBar,
    applyFxPref,
    setCinematic,
    getCinematic,
    runEntrySplash,
    storageKey,
    cinematicKey,
  };
})();
