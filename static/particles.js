/* ========================================================
   particles.js - 最终整合版
   职责：负责全站 Canvas 背景的粒子运动与连线
   ======================================================== */
const canvas = document.getElementById("bg-canvas");
const ctx = canvas.getContext("2d");

// 获取模块名，用于切换颜色
const moduleName = document.body.dataset.module || "home";

/* --- 颜色配置：刻晴色系 --- */
const COLORS = {
  home: [123, 108, 246],    // 刻晴紫
  schmidt: [160, 140, 255], // 亮紫
  chsh: [255, 120, 180]     // 霓裳粉
};

const [R, G, B] = COLORS[moduleName] || COLORS.home;

let width, height;
let particles = [];
const particleCount = 60; // 粒子数量
const maxDist = 120;      // 连线最大距离

const mouse = { x: null, y: null };

/* --- 1. 画布自适应 --- */
function resize() {
  width = canvas.width = window.innerWidth;
  height = canvas.height = window.innerHeight;
}
window.addEventListener("resize", resize);
resize();

/* --- 2. 交互监听 --- */
window.addEventListener("mousemove", e => {
  mouse.x = e.clientX;
  mouse.y = e.clientY;
});
window.addEventListener("mouseout", () => {
  mouse.x = mouse.y = null;
});

/* --- 3. 粒子类定义 (回归你最稳的原版逻辑) --- */
class Particle {
  constructor() {
    this.x = Math.random() * width;
    this.y = Math.random() * height;
    // 速度：0.3 比较优雅，不会太乱
    this.vx = (Math.random() - 0.5) * 0.3; 
    this.vy = (Math.random() - 0.5) * 0.3;
    this.r = Math.random() * 1.5 + 0.5;
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;

    // 边界反弹逻辑
    if (this.x < 0 || this.x > width) this.vx *= -1;
    if (this.y < 0 || this.y > height) this.vy *= -1;
  }

  draw() {
    ctx.beginPath();
    // 还原为你喜欢的圆形粒子
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${R},${G},${B},0.8)`;
    ctx.fill();
  }
}

/* --- 4. 初始化 --- */
function init() {
  particles = Array.from({length: particleCount}, () => new Particle());
}
init();

/* --- 5. 连线逻辑 --- */
function connect() {
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x;
      const dy = particles[i].y - particles[j].y;
      const d = Math.hypot(dx, dy);
      
      if (d < maxDist) {
        // 连线透明度随距离消失
        ctx.strokeStyle = `rgba(${R},${G},${B},${1 - d / maxDist})`;
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(particles[i].x, particles[i].y);
        ctx.lineTo(particles[j].x, particles[j].y);
        ctx.stroke();
      }
    }
  }
}

/* --- 6. 限帧动画引擎 (30FPS) --- */
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

// 启动
requestAnimationFrame(animate);