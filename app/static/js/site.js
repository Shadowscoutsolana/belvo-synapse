/* Belvo frontend interactions — no dependencies.
   - mobile nav, scroll reveal, tilt cards
   - hero particle field: move cursor to disturb, click to recompose */
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Mobile nav
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Scroll reveal
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('in'); });
  }

  // Tilt
  if (!reduce) {
    document.querySelectorAll('[data-tilt]').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = 'perspective(900px) rotateX(' + (-y * 6).toFixed(2) + 'deg) rotateY(' + (x * 8).toFixed(2) + 'deg)';
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
  }

  // Hero particle field
  var hero = document.querySelector('.hero');
  var canvas = hero && hero.querySelector('canvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var W = 0, H = 0, parts = [], shape = 0, visible = true;
  var mouse = { x: -9999, y: -9999 };
  var ACCENT = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#ff5a2c';
  var COUNT = window.innerWidth < 700 ? 420 : 900;

  // Formations: each returns a target {x,y} for particle i of n
  var shapes = [
    function (i, n) { // grid
      var cols = Math.ceil(Math.sqrt(n * W / H)), rows = Math.ceil(n / cols);
      return { x: (i % cols + 0.5) * (W / cols), y: (Math.floor(i / cols) + 0.5) * (H / rows) };
    },
    function (i, n) { // concentric rings
      var ring = Math.floor(Math.sqrt(i)), a = (i * 2.399963) % (Math.PI * 2);
      var r = (ring + 1) * Math.min(W, H) / (Math.sqrt(n) * 1.5);
      return { x: W * 0.68 + Math.cos(a) * r, y: H * 0.45 + Math.sin(a) * r };
    },
    function (i, n) { // waves
      var t = i / n, x = t * W * 1.1 - W * 0.05, k = i % 5;
      return { x: x, y: H * (0.3 + k * 0.1) + Math.sin(t * 14 + k) * H * 0.07 };
    },
    function (i, n) { // golden spiral
      var a = i * 2.399963, r = Math.sqrt(i / n) * Math.min(W, H) * 0.55;
      return { x: W * 0.7 + Math.cos(a) * r, y: H * 0.45 + Math.sin(a) * r };
    }
  ];

  function resize() {
    var r = hero.getBoundingClientRect();
    W = r.width; H = r.height;
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    retarget(true);
  }
  function retarget(snap) {
    var n = COUNT;
    if (parts.length !== n) {
      parts = [];
      for (var i = 0; i < n; i++) parts.push({ x: Math.random() * W, y: Math.random() * H, vx: 0, vy: 0, tx: 0, ty: 0, s: 0.8 + Math.random() * 1.6, hot: Math.random() < 0.08 });
    }
    for (var j = 0; j < n; j++) {
      var t = shapes[shape](j, n);
      parts[j].tx = t.x; parts[j].ty = t.y;
      if (snap) { parts[j].x = t.x; parts[j].y = t.y; }
    }
  }
  function frame() {
    if (visible) {
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < parts.length; i++) {
        var p = parts[i];
        p.vx += (p.tx - p.x) * 0.012; p.vy += (p.ty - p.y) * 0.012;
        var dx = p.x - mouse.x, dy = p.y - mouse.y, d2 = dx * dx + dy * dy;
        if (d2 < 16000) { var f = (1 - d2 / 16000) * 2.2, d = Math.sqrt(d2) || 1; p.vx += dx / d * f; p.vy += dy / d * f; }
        p.vx *= 0.88; p.vy *= 0.88; p.x += p.vx; p.y += p.vy;
        ctx.fillStyle = p.hot ? ACCENT : 'rgba(243,240,234,0.55)';
        ctx.beginPath(); ctx.arc(p.x, p.y, p.s, 0, 6.2832); ctx.fill();
      }
    }
    if (!reduce) requestAnimationFrame(frame);
  }

  hero.addEventListener('pointermove', function (e) {
    var r = hero.getBoundingClientRect(); mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top;
  });
  hero.addEventListener('pointerleave', function () { mouse.x = mouse.y = -9999; });
  hero.addEventListener('click', function (e) {
    if (e.target.closest('a,button')) return;
    shape = (shape + 1) % shapes.length; retarget(false);
  });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (en) { visible = en[0].isIntersecting; }).observe(hero);
  }
  window.addEventListener('resize', resize);
  resize();
  if (reduce) { frame(); } else { requestAnimationFrame(frame); }
})();
