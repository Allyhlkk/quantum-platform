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
          <div class="entry-home-tap" title="Audio on">
            <span class="entry-home-tap-text">TAP TO START</span>
            <svg class="entry-home-audio" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
              <path d="M3 9v6h4l5 4V5L7 9H3z" fill="currentColor"></path>
              <path d="M16.5 12c0-1.77-1-3.29-2.5-4.03v8.05c1.5-.73 2.5-2.25 2.5-4.02z" fill="currentColor" opacity="0.7"></path>
              <path d="M19 12c0-2.97-1.63-5.56-4.06-6.94v2.27c1.31 1.01 2.06 2.58 2.06 4.67s-.75 3.66-2.06 4.67v2.27C17.37 17.56 19 14.97 19 12z" fill="currentColor" opacity="0.4"></path>
            </svg>
          </div>
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

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function createHomeEntanglementScene() {
    if (!document.body) return null;
    const old = document.querySelector(".home-entanglement-scene");
    if (old && old.__entanglement && typeof old.__entanglement.destroy === "function") {
      old.__entanglement.destroy();
    }
    if (old && old.parentNode) old.parentNode.removeChild(old);

    const scene = document.createElement("div");
    scene.className = "home-entanglement-scene";
    scene.innerHTML = `
      <canvas class="home-entanglement-canvas" aria-hidden="true"></canvas>
      <button type="button" class="home-entanglement-core home-entanglement-core-left" aria-label="激发左侧纠缠节点"></button>
      <button type="button" class="home-entanglement-core home-entanglement-core-right" aria-label="激发右侧纠缠节点"></button>
      <div class="home-entanglement-caption">ENTANGLED STATE // 点击任一节点触发联动</div>
    `;
    document.body.appendChild(scene);
    return scene;
  }

  function initHomeEntanglementScene(scene) {
    if (!scene) return null;
    const canvas = scene.querySelector(".home-entanglement-canvas");
    const ctx = canvas && canvas.getContext ? canvas.getContext("2d") : null;
    const coreButtons = Array.from(scene.querySelectorAll(".home-entanglement-core"));
    if (!canvas || !ctx || coreButtons.length < 2) return null;

    const state = {
      width: 0,
      height: 0,
      dpr: 1,
      mouseX: 0,
      mouseY: 0,
      mouseActive: false,
      raf: 0,
      running: true,
      packets: [],
      spheres: [],
      resizeTimer: null,
    };

    function makeSphere(side, hue, config = {}) {
      const particles = [];
      const count = Math.max(72, config.count || 104);
      for (let i = 0; i < count; i++) {
        particles.push({
          angle: (Math.PI * 2 * i) / count,
          band: Math.random(),
          speed: 0.35 + Math.random() * 0.82,
          phase: Math.random() * Math.PI * 2,
          drift: 0.25 + Math.random() * 0.8,
        alpha: 0.14 + Math.random() * 0.42,
        size: 0.75 + Math.random() * 1.55,
          trail: 0.06 + Math.random() * 0.08,
          x: 0,
          y: 0,
        });
      }

      return {
        side,
        hue,
        baseX: 0,
        baseY: 0,
        x: 0,
        y: 0,
        radius: 120,
        orbitScale: 1,
        pulse: 0,
        echo: 0,
        kick: 0,
        phase: Math.random() * Math.PI * 2,
        visibilityPhase: Math.random() * Math.PI * 2,
        visibilitySpeed: 0.35 + Math.random() * 0.38,
        visibilityDepth: 0.22 + Math.random() * 0.12,
        shape: {
          count,
          scaleX: config.scaleX || 1,
          scaleY: config.scaleY || 1,
          twist: config.twist || 0.5,
          wobble: config.wobble || 0.22,
          ringFloor: config.ringFloor || 0.14,
          ringSpan: config.ringSpan || 0.84,
          hueShift: config.hueShift || 0,
          lineAlpha: config.lineAlpha || 0.07,
          auraAlpha: config.auraAlpha || 0.26,
          mouseLift: config.mouseLift || 0.018,
        },
        particles,
      };
    }

    state.spheres = [
      makeSphere("left", 242, {
        count: 90,
        scaleX: 1.16,
        scaleY: 0.86,
        twist: 0.58,
        wobble: 0.18,
        ringFloor: 0.17,
        ringSpan: 0.82,
        hueShift: 0,
        lineAlpha: 0.08,
        auraAlpha: 0.28,
        mouseLift: 0.006,
      }),
      makeSphere("right", 188, {
        count: 118,
        scaleX: 0.92,
        scaleY: 1.08,
        twist: 0.32,
        wobble: 0.28,
        ringFloor: 0.11,
        ringSpan: 0.9,
        hueShift: 14,
        lineAlpha: 0.075,
        auraAlpha: 0.24,
        mouseLift: 0.005,
      }),
    ];

    function updateLayout() {
      const left = state.spheres[0];
      const right = state.spheres[1];
      const radius = clamp(Math.min(state.width, state.height) * 0.145, 96, 170);
      left.radius = radius;
      right.radius = radius * 0.98;
      left.baseX = state.width * 0.36;
      left.baseY = state.height * 0.52;
      right.baseX = state.width * 0.64;
      right.baseY = state.height * 0.47;

      coreButtons.forEach((btn, idx) => {
        const sphere = state.spheres[idx];
        const size = Math.round(sphere.radius * 2.4);
        btn.style.width = `${size}px`;
        btn.style.height = `${size}px`;
        btn.style.left = `${sphere.baseX}px`;
        btn.style.top = `${sphere.baseY}px`;
      });
    }

    function resize() {
      state.width = Math.max(1, scene.clientWidth || window.innerWidth || 1);
      state.height = Math.max(1, scene.clientHeight || window.innerHeight || 1);
      state.dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(state.width * state.dpr);
      canvas.height = Math.round(state.height * state.dpr);
      canvas.style.width = `${state.width}px`;
      canvas.style.height = `${state.height}px`;
      ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);
      updateLayout();
    }

    function pointOnCurve(start, ctrl, end, t) {
      const u = 1 - t;
      return {
        x: u * u * start.x + 2 * u * t * ctrl.x + t * t * end.x,
        y: u * u * start.y + 2 * u * t * ctrl.y + t * t * end.y,
      };
    }

    function edgePoint(from, to, radius) {
      const dx = to.x - from.x;
      const dy = to.y - from.y;
      const len = Math.hypot(dx, dy) || 1;
      return {
        x: from.x + (dx / len) * radius,
        y: from.y + (dy / len) * radius,
      };
    }

    function spawnPackets(sourceIndex, strength) {
      const count = Math.max(8, Math.round(12 + strength * 14));
      for (let i = 0; i < count; i++) {
        state.packets.push({
          from: sourceIndex,
          to: 1 - sourceIndex,
          t: Math.random(),
          speed: 0.14 + Math.random() * 0.18 + strength * 0.08,
          wobble: (Math.random() * 2 - 1) * 64,
          alpha: 0.36 + Math.random() * 0.5 * strength,
          hueShift: Math.random() * 48,
          trail: 0.08 + Math.random() * 0.1,
        });
      }
      if (state.packets.length > 96) {
        state.packets.splice(0, state.packets.length - 96);
      }
    }

    function pulseSphere(index, sourceIndex) {
      const sphere = state.spheres[index];
      const other = state.spheres[1 - index];
      sphere.pulse = 1;
      sphere.echo = 1;
      sphere.kick = 1;
      spawnPackets(sourceIndex, 1);

      window.setTimeout(() => {
        other.pulse = Math.max(other.pulse, 0.58);
        other.echo = Math.max(other.echo, 0.72);
        other.kick = Math.max(other.kick, 0.48);
        spawnPackets(1 - sourceIndex, 0.72);
      }, 140);
    }

    function updateMouse(e) {
      const rect = canvas.getBoundingClientRect();
      state.mouseX = e.clientX - rect.left;
      state.mouseY = e.clientY - rect.top;
      state.mouseActive = true;
    }

    function onMouseLeave() {
      state.mouseActive = false;
    }

    coreButtons[0].addEventListener("click", (e) => {
      e.preventDefault();
      pulseSphere(0, 0);
    });
    coreButtons[1].addEventListener("click", (e) => {
      e.preventDefault();
      pulseSphere(1, 1);
    });

    window.addEventListener("pointermove", updateMouse, { passive: true });
    window.addEventListener("pointerdown", updateMouse, { passive: true });
    window.addEventListener("pointerleave", onMouseLeave, { passive: true });
    window.addEventListener("blur", onMouseLeave);
    window.addEventListener("resize", resize);

    function drawSphere(sphere, other, time, dt) {
      const lane = sphere.side === "left" ? -1 : 1;
      const floatX = Math.sin(time * 0.72 + sphere.phase) * (26 + sphere.radius * 0.11);
      const floatY = Math.cos(time * 0.63 + sphere.phase * 0.7) * (18 + sphere.radius * 0.08);
      const driftX = Math.sin(time * 0.18 + sphere.phase * 1.3) * (60 + sphere.radius * 0.18) * lane;
      const driftY = Math.cos(time * 0.22 + sphere.phase * 0.9) * (36 + sphere.radius * 0.12);
      const microX = Math.sin(time * 1.6 + sphere.phase * 2.4) * 6;
      const microY = Math.cos(time * 1.4 + sphere.phase * 2.1) * 5;
      const swayX = floatX + driftX + microX;
      const swayY = floatY + driftY + microY;
      const vis = clamp(
        0.38 + Math.sin(time * sphere.visibilitySpeed + sphere.visibilityPhase) * sphere.visibilityDepth + sphere.pulse * 0.24,
        0.14,
        0.95
      );
      const mouseInfluence = state.mouseActive
        ? clamp(1 - Math.hypot(state.mouseX - sphere.baseX, state.mouseY - sphere.baseY) / (sphere.radius * 2.8), 0, 1)
        : 0;
      const moveX = state.mouseActive ? (state.mouseX - sphere.baseX) * sphere.shape.mouseLift * mouseInfluence : 0;
      const moveY = state.mouseActive ? (state.mouseY - sphere.baseY) * sphere.shape.mouseLift * mouseInfluence : 0;

      sphere.x = sphere.baseX + swayX + moveX;
      sphere.y = sphere.baseY + swayY + moveY;
      sphere.orbitScale = 0.92 + Math.sin(time * 0.9 + sphere.phase) * 0.07 + sphere.pulse * 0.05;

      sphere.pulse = Math.max(0, sphere.pulse - dt * 0.0011);
      sphere.echo = Math.max(0, sphere.echo - dt * 0.0007);
      sphere.kick = Math.max(0, sphere.kick - dt * 0.0012);

      const aura = ctx.createRadialGradient(sphere.x, sphere.y, sphere.radius * 0.05, sphere.x, sphere.y, sphere.radius * 1.42);
      aura.addColorStop(0, `hsla(${sphere.hue}, 88%, 78%, ${vis * (sphere.shape.auraAlpha + sphere.pulse * 0.12)})`);
      aura.addColorStop(0.38, `hsla(${sphere.hue + sphere.shape.hueShift + 10}, 70%, 68%, ${vis * (0.09 + sphere.echo * 0.07)})`);
      aura.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = aura;
      ctx.beginPath();
      ctx.arc(sphere.x, sphere.y, sphere.radius * (1.22 + sphere.pulse * 0.08), 0, Math.PI * 2);
      ctx.fill();

      const particles = sphere.particles;
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        const spin = time * (0.48 + p.speed * 0.34) + p.angle + sphere.pulse * 0.55;
        const ring = sphere.radius * (sphere.shape.ringFloor + p.band * sphere.shape.ringSpan) * sphere.orbitScale;
        const twist = sphere.shape.twist + Math.sin(p.phase + time * 0.35) * sphere.shape.wobble;
        const jitter = Math.sin(spin * 2.0 + p.phase) * sphere.radius * 0.032 * (0.55 + sphere.pulse);
        const x = sphere.x + Math.cos(spin + twist) * ring * sphere.shape.scaleX + Math.cos(p.phase + time * 0.7) * jitter;
        const y = sphere.y + Math.sin(spin * 0.92 - twist * 0.45) * (ring * sphere.shape.scaleY) + Math.sin(p.phase + time * 0.6) * jitter;
        const repel = state.mouseActive
          ? clamp(1 - Math.hypot(state.mouseX - x, state.mouseY - y) / (sphere.radius * 1.35), 0, 1)
          : 0;
        const push = repel * 0.04;
        p.x = x + (x - state.mouseX) * push;
        p.y = y + (y - state.mouseY) * push;

        const glowAlpha = clamp((p.alpha * vis) + sphere.pulse * 0.16 + sphere.kick * 0.08 - repel * 0.05, 0.08, 0.78);
        ctx.fillStyle = `hsla(${sphere.hue + 12 + p.drift * 18}, 72%, ${80 + p.band * 6}%, ${glowAlpha})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * (0.98 + sphere.pulse * 0.28), 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.strokeStyle = `hsla(${sphere.hue + 6}, 62%, 72%, ${vis * (sphere.shape.lineAlpha + sphere.pulse * 0.04)})`;
      ctx.lineWidth = 1.0;
      ctx.beginPath();
      for (let i = 0; i < particles.length; i++) {
        const a = particles[i];
        const b = particles[(i + 2) % particles.length];
        if (i === 0) ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
      }
      ctx.stroke();

      if (other) {
        const bridge = ctx.createLinearGradient(sphere.x, sphere.y, other.x, other.y);
        bridge.addColorStop(0, `hsla(${sphere.hue + 4}, 54%, 68%, ${vis * (0.06 + sphere.pulse * 0.03)})`);
        bridge.addColorStop(0.5, `rgba(224,226,240,${vis * (0.02 + sphere.echo * 0.012)})`);
        bridge.addColorStop(1, `hsla(${other.hue + 4}, 54%, 70%, ${vis * (0.06 + other.pulse * 0.03)})`);
        ctx.strokeStyle = bridge;
        ctx.lineWidth = 0.95;
        ctx.setLineDash([5, 22]);
        ctx.beginPath();
        const start = edgePoint(sphere, other, sphere.radius * 0.96);
        const end = edgePoint(other, sphere, other.radius * 0.96);
        const ctrl = {
          x: (start.x + end.x) / 2 + Math.sin(time * 0.8 + sphere.phase) * 48,
          y: (start.y + end.y) / 2 - 72 + Math.cos(time * 0.9 + sphere.phase) * 22,
        };
        ctx.moveTo(start.x, start.y);
        ctx.quadraticCurveTo(ctrl.x, ctrl.y, end.x, end.y);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    function drawPackets(time, dt) {
      ctx.save();
      ctx.globalCompositeOperation = "lighter";
      for (let i = state.packets.length - 1; i >= 0; i--) {
        const packet = state.packets[i];
        const from = state.spheres[packet.from];
        const to = state.spheres[packet.to];
        packet.t += dt * packet.speed / 1000;
        if (packet.t >= 1) {
          state.packets.splice(i, 1);
          continue;
        }

        const start = edgePoint(from, to, from.radius * 0.92);
        const end = edgePoint(to, from, to.radius * 0.92);
        const ctrl = {
          x: (start.x + end.x) / 2 + Math.sin(time * 1.2 + packet.wobble) * (34 + Math.abs(packet.wobble) * 0.18),
          y: (start.y + end.y) / 2 - 48 + packet.wobble * 0.35,
        };
        const pos = pointOnCurve(start, ctrl, end, packet.t);
        const prev = pointOnCurve(start, ctrl, end, Math.max(0, packet.t - packet.trail));

        ctx.strokeStyle = `hsla(${204 + packet.hueShift}, 60%, 76%, ${packet.alpha * 0.52})`;
        ctx.lineWidth = 1.45;
        ctx.beginPath();
        ctx.moveTo(prev.x, prev.y);
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();

        ctx.fillStyle = `hsla(${198 + packet.hueShift}, 66%, 82%, ${0.72})`;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 1.2 + packet.alpha * 1.2, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }

    function animate(now) {
      if (!state.running) return;
      const dt = Math.min(34, now - (state.last || now));
      state.last = now;
      const time = now * 0.001;

      ctx.clearRect(0, 0, state.width, state.height);
      ctx.globalCompositeOperation = "lighter";

      drawSphere(state.spheres[0], state.spheres[1], time, dt);
      drawSphere(state.spheres[1], state.spheres[0], time, dt);
      drawPackets(time, dt);

      ctx.globalCompositeOperation = "source-over";
      state.raf = window.requestAnimationFrame(animate);
    }

    resize();
    state.raf = window.requestAnimationFrame(animate);

    return {
      reveal() {
        scene.classList.add("is-visible");
      },
      destroy() {
        state.running = false;
        if (state.raf) window.cancelAnimationFrame(state.raf);
        window.removeEventListener("pointermove", updateMouse);
        window.removeEventListener("pointerdown", updateMouse);
        window.removeEventListener("pointerleave", onMouseLeave);
        window.removeEventListener("blur", onMouseLeave);
        window.removeEventListener("resize", resize);
      },
      pulseLeft() {
        pulseSphere(0, 0);
      },
      pulseRight() {
        pulseSphere(1, 1);
      },
    };
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
    const entanglementScene = createHomeEntanglementScene();
    const entanglement = initHomeEntanglementScene(entanglementScene);
    if (entanglementScene) {
      entanglementScene.__entanglement = entanglement;
    }

    let started = false;
    let finished = false;
    let fallbackTimer = null;

    function finishSequence() {
      if (finished) return;
      finished = true;
      if (fallbackTimer) {
        window.clearTimeout(fallbackTimer);
        fallbackTimer = null;
      }
      if (entanglement) {
        entanglement.reveal();
      } else if (entanglementScene) {
        entanglementScene.classList.add("is-visible");
      }
      finalizeHomeSplash(splash, 900);
    }

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
        p.catch(() => {
          window.setTimeout(finishSequence, 1800);
        });
      }
      fallbackTimer = window.setTimeout(finishSequence, 4200);
    }

    function onKeydown(e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        startSequence();
      }
    }

    audio.addEventListener("ended", finishSequence, { once: true });
    audio.addEventListener("error", finishSequence, { once: true });

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
