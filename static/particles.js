/* ========================================================
   particles.js
   Global fullscreen particles + links + mouse disturbance.
   ======================================================== */
(function () {
  const canvas = document.getElementById("bg-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const moduleName = document.body.dataset.module || "home";
  const COLORS = {
    home: [123, 108, 246],
    schmidt: [160, 140, 255],
    chsh: [255, 120, 180],
    analysis: [145, 128, 255],
  };
  const [R, G, B] = COLORS[moduleName] || COLORS.home;

  let width = 0;
  let height = 0;
  let particles = [];
  const spawnMargin = 64;
  const maxDist = 148;
  const maxSpeed = 1.85;
  const fps = 36;
  const frameInterval = 1000 / fps;
  const densityDivisor = moduleName === "home" ? 8200 : 9800;
  const minCount = moduleName === "home" ? 120 : 95;
  const maxCount = moduleName === "home" ? 240 : 190;

  const mouse = {
    x: null,
    y: null,
    px: null,
    py: null,
    vx: 0,
    vy: 0,
    active: false,
    radius: 180,
    force: 0.22,
    lastMoveAt: 0,
  };
  const mouseActiveWindowMs = 260;

  function clamp(v, lo, hi) {
    return Math.max(lo, Math.min(hi, v));
  }

  function calcParticleCount() {
    const byArea = Math.round((width * height) / densityDivisor);
    return clamp(byArea, minCount, maxCount);
  }

  function isMouseHot(nowTs) {
    if (!mouse.active || mouse.x === null || mouse.y === null) return false;
    return nowTs - mouse.lastMoveAt <= mouseActiveWindowMs;
  }

  class Particle {
    constructor() {
      this.x = -spawnMargin + Math.random() * (width + spawnMargin * 2);
      this.y = -spawnMargin + Math.random() * (height + spawnMargin * 2);
      this.baseVx = (Math.random() - 0.5) * 0.42;
      this.baseVy = (Math.random() - 0.5) * 0.42;
      this.vx = this.baseVx;
      this.vy = this.baseVy;
      this.r = Math.random() * 1.8 + 0.55;
    }

    update(mouseHot) {
      if (mouseHot && mouse.x !== null && mouse.y !== null) {
        const dx = this.x - mouse.x;
        const dy = this.y - mouse.y;
        const d = Math.hypot(dx, dy);
        if (d < mouse.radius && d > 0.0001) {
          const n = 1 - d / mouse.radius;
          const nx = dx / d;
          const ny = dy / d;
          const mouseBoostX = mouse.vx * 0.015 * n;
          const mouseBoostY = mouse.vy * 0.015 * n;
          this.vx += nx * mouse.force * n + (-ny) * 0.03 * n + mouseBoostX;
          this.vy += ny * mouse.force * n + nx * 0.03 * n + mouseBoostY;
        }
      }

      this.vx += (this.baseVx - this.vx) * 0.016;
      this.vy += (this.baseVy - this.vy) * 0.016;
      this.vx *= 0.992;
      this.vy *= 0.992;
      this.vx = clamp(this.vx, -maxSpeed, maxSpeed);
      this.vy = clamp(this.vy, -maxSpeed, maxSpeed);

      this.x += this.vx;
      this.y += this.vy;

      if (this.x < -spawnMargin || this.x > width + spawnMargin) this.vx *= -1;
      if (this.y < -spawnMargin || this.y > height + spawnMargin) this.vy *= -1;
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${R},${G},${B},0.82)`;
      ctx.fill();
    }
  }

  function syncParticleCount() {
    const target = calcParticleCount();
    if (particles.length < target) {
      const extra = target - particles.length;
      for (let i = 0; i < extra; i++) particles.push(new Particle());
      return;
    }
    if (particles.length > target) {
      particles.length = target;
    }
  }

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    syncParticleCount();
  }

  function updateMousePosition(x, y) {
    if (mouse.px === null || mouse.py === null) {
      mouse.vx = 0;
      mouse.vy = 0;
    } else {
      mouse.vx = (x - mouse.px) * 0.7;
      mouse.vy = (y - mouse.py) * 0.7;
    }
    mouse.px = x;
    mouse.py = y;
    mouse.x = x;
    mouse.y = y;
    mouse.active = true;
    mouse.lastMoveAt = performance.now();
  }

  window.addEventListener("mousemove", (e) => {
    updateMousePosition(e.clientX, e.clientY);
  });

  window.addEventListener(
    "touchmove",
    (e) => {
      const t = e.touches && e.touches[0];
      if (!t) return;
      updateMousePosition(t.clientX, t.clientY);
    },
    { passive: true }
  );

  function clearMouse() {
    mouse.active = false;
    mouse.x = null;
    mouse.y = null;
    mouse.px = null;
    mouse.py = null;
    mouse.vx = 0;
    mouse.vy = 0;
    mouse.lastMoveAt = 0;
  }

  window.addEventListener("mouseout", clearMouse);
  window.addEventListener("touchend", clearMouse, { passive: true });
  window.addEventListener("touchcancel", clearMouse, { passive: true });
  window.addEventListener("resize", resize);

  function drawLinks() {
    const len = particles.length;
    for (let i = 0; i < len; i++) {
      const p1 = particles[i];
      for (let j = i + 1; j < len; j++) {
        const p2 = particles[j];
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const d = Math.hypot(dx, dy);
        if (d >= maxDist) continue;
        const alpha = Math.pow(1 - d / maxDist, 1.28) * 0.72;
        ctx.strokeStyle = `rgba(${R},${G},${B},${alpha})`;
        ctx.lineWidth = 0.62;
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      }
    }
  }

  function drawMouseLinks(mouseHot) {
    if (!mouseHot || mouse.x === null || mouse.y === null) return;
    const distMax = mouse.radius * 1.05;
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      const dx = p.x - mouse.x;
      const dy = p.y - mouse.y;
      const d = Math.hypot(dx, dy);
      if (d >= distMax) continue;
      const alpha = (1 - d / distMax) * 0.28;
      ctx.strokeStyle = `rgba(${R},${G},${B},${alpha})`;
      ctx.lineWidth = 0.9;
      ctx.beginPath();
      ctx.moveTo(mouse.x, mouse.y);
      ctx.lineTo(p.x, p.y);
      ctx.stroke();
    }
  }

  let lastTime = 0;
  function animate(now) {
    if (now - lastTime < frameInterval) {
      requestAnimationFrame(animate);
      return;
    }
    lastTime = now;

    const mouseHot = isMouseHot(now);
    ctx.clearRect(0, 0, width, height);
    for (let i = 0; i < particles.length; i++) {
      particles[i].update(mouseHot);
      particles[i].draw();
    }
    drawLinks();
    drawMouseLinks(mouseHot);
    requestAnimationFrame(animate);
  }

  resize();
  requestAnimationFrame(animate);
})();
