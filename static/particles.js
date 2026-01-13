const canvas = document.getElementById("bg-canvas");
const ctx = canvas.getContext("2d");

const module = document.body.dataset.module || "home";

const COLORS = {
  home: [123,108,246],
  schmidt: [160,140,255],
  chsh: [255,120,180]
};

const [R, G, B] = COLORS[module] || COLORS.home;

let width, height;
let particles = [];
const particleCount = 60;
const maxDist = 120;

const mouse = { x: null, y: null };

function resize() {
  width = canvas.width = window.innerWidth;
  height = canvas.height = window.innerHeight;
}
window.addEventListener("resize", resize);
resize();

window.addEventListener("mousemove", e => {
  mouse.x = e.clientX;
  mouse.y = e.clientY;
});
window.addEventListener("mouseout", () => {
  mouse.x = mouse.y = null;
});

class Particle {
  constructor() {
    this.x = Math.random() * width;
    this.y = Math.random() * height;
    this.vx = (Math.random() - 0.5) * 0.3;
    this.vy = (Math.random() - 0.5) * 0.3;
    this.r = Math.random() * 1.5 + 0.5;
  }
  update() {
    this.x += this.vx;
    this.y += this.vy;
    if (this.x < 0 || this.x > width) this.vx *= -1;
    if (this.y < 0 || this.y > height) this.vy *= -1;
  }
  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${R},${G},${B},0.8)`;
    ctx.fill();
  }
}

function init() {
  particles = Array.from({length: particleCount}, () => new Particle());
}
init();

function connect() {
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x;
      const dy = particles[i].y - particles[j].y;
      const d = Math.hypot(dx, dy);
      if (d < maxDist) {
        ctx.strokeStyle = `rgba(${R},${G},${B},${1-d/maxDist})`;
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(particles[i].x, particles[i].y);
        ctx.lineTo(particles[j].x, particles[j].y);
        ctx.stroke();
      }
    }
  }
}

/* ===== 限帧动画 ===== */
let lastTime = 0;
const FPS = 30;
const interval = 1000 / FPS;

function animate(time) {
  if (time - lastTime < interval) {
    requestAnimationFrame(animate);
    return;
  }
  lastTime = time;

  ctx.clearRect(0, 0, width, height);
  particles.forEach(p => {
    p.update();
    p.draw();
  });
  connect();

  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
