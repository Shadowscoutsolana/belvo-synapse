/* Belvo frontend interactions — no dependencies.
   - mobile nav, scroll reveal, tilt cards, divisions slide out of a dot box on scroll
   - hero: Belvo mark rendered as a 3D dot field (cursor tilts + scatters, click to burst) */
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

  // Careers: filter open positions by team
  var jobList = document.querySelector('[data-jobs]');
  if (jobList) {
    var chips = document.querySelectorAll('.job-filters .chip');
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var team = chip.getAttribute('data-team');
        chips.forEach(function (c) {
          var on = c === chip;
          c.classList.toggle('is-on', on);
          c.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        jobList.querySelectorAll('.job').forEach(function (job) {
          job.hidden = team !== 'all' && job.getAttribute('data-team') !== team;
        });
      });
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

  // -------------------------------------------------------------------------
  // 3D Gallery: scroll-reveal + floating + interactive 3D tilt on hover
  // -------------------------------------------------------------------------
  var g3dCards = document.querySelectorAll('.reveal-3d');
  if (g3dCards.length) {
    if ('IntersectionObserver' in window && !reduce) {
      var g3dIO = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add('in');
            // Start floating after the entrance animation finishes
            setTimeout(function () { e.target.classList.add('floating'); }, 1200);
            g3dIO.unobserve(e.target);
          }
        });
      }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });
      g3dCards.forEach(function (el) { g3dIO.observe(el); });
    } else {
      g3dCards.forEach(function (el) { el.classList.add('in'); el.classList.add('floating'); });
    }

    // Interactive 3D tilt on pointer move
    if (!reduce) {
      g3dCards.forEach(function (card) {
        card.addEventListener('pointermove', function (e) {
          var r = card.getBoundingClientRect();
          var x = (e.clientX - r.left) / r.width - 0.5;
          var y = (e.clientY - r.top) / r.height - 0.5;
          var rY = x * 16, rX = -y * 12;
          card.style.transform = 'perspective(900px) translateY(-14px) rotateX(' + rX.toFixed(2) + 'deg) rotateY(' + rY.toFixed(2) + 'deg) scale(1.03)';
          // Move the shine to follow the cursor
          var shine = card.querySelector('.g3d-shine');
          if (shine) {
            shine.style.transition = 'none';
            shine.style.transform = 'translateX(' + (x * 240).toFixed(1) + '%)';
          }
        });
        card.addEventListener('pointerleave', function () {
          card.style.transform = '';
          var shine = card.querySelector('.g3d-shine');
          if (shine) {
            shine.style.transition = '';
            shine.style.transform = 'translateX(-120%)';
          }
        });
      });
    }
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


  // ---------------------------------------------------------------------------
  // Divisions: a small 3D box made of dots rides in the corner while the page
  // scrolls normally. Each full-screen slide grows out of the box as it
  // scrolls into view; the lid opens and dots spill out while it does.
  // ---------------------------------------------------------------------------
  (function () {
    var root = document.querySelector('[data-xslides]');
    if (!root) return;
    var slides = root.querySelectorAll('.xslide'), panels = root.querySelectorAll('.xpanel');
    var box = root.querySelector('.dotbox'), bctx = box.getContext('2d');
    var N = slides.length, queued = false, act = 0, actShown = 0, inView = false, looping = false;
    var START = 70;      // px size the slide starts at, inside the box
    var GROW = 0.8;      // viewport heights of scrolling for a slide to fill the screen

    function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
    function ease(v) { v = clamp(v); return 1 - Math.pow(1 - v, 3); }

    // --- slides: scale each panel out of the box's mouth, driven by scroll ---
    function update() {
      queued = false;
      var vh = window.innerHeight, br = box.getBoundingClientRect();
      var mx = br.left + br.width * 0.5, my = br.top + br.height * 0.42; // box mouth on screen
      var a = 0;
      for (var i = 0; i < N; i++) {
        var sr = slides[i].getBoundingClientRect(), pnl = panels[i];
        var raw = clamp((vh - sr.top) / (vh * GROW));
        a = Math.max(a, Math.sin(Math.PI * raw));
        if (reduce) continue;
        if (sr.bottom < 0 || sr.top > vh) { pnl.style.opacity = raw >= 1 ? '' : '0'; continue; }
        var e = ease(raw);
        if (e >= 1) { pnl.style.transform = pnl.style.opacity = pnl.style.transformOrigin = ''; continue; }
        var px = sr.left + pnl.offsetLeft, py = sr.top + pnl.offsetTop; // untransformed panel corner
        var s0 = START / pnl.offsetWidth, s = s0 + (1 - s0) * e;
        pnl.style.transformOrigin = (mx - px).toFixed(1) + 'px ' + (my - py).toFixed(1) + 'px';
        pnl.style.transform = 'scale(' + s.toFixed(4) + ')';
        pnl.style.opacity = Math.min(1, e * 3).toFixed(3);
      }
      act = a;
      startBox();
    }
    function queue() { if (!queued) { queued = true; requestAnimationFrame(update); } }

    // --- the dot box ---
    var bdpr = Math.min(window.devicePixelRatio || 1, 2), BW = 0, BH = 0;
    var body = [], lid = [], sparks = [], t0 = performance.now();
    (function makeBox() {
      var E = 9, F = 5, v, k, j;
      // 8 edges of the body below the lid (y from -1 to 1), as dense dot lines
      var corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]];
      for (v = 0; v < 4; v++) {
        var c = corners[v], d = corners[(v + 1) % 4];
        for (k = 0; k <= E; k++) {
          var x = c[0] + (d[0] - c[0]) * k / E, z = c[1] + (d[1] - c[1]) * k / E;
          body.push([x, 1, z, 1]);                    // bottom square
          body.push([x, -1, z, 0.6]);                 // open top rim
          if (k) lid.push([x, z, 1]);                 // lid rim (top square)
        }
        for (k = 1; k < E; k++) body.push([c[0], -1 + 2 * k / E, c[1], 1]); // vertical edges
      }
      // faint dots filling the side faces and the lid
      for (j = 1; j < F; j++) for (k = 1; k < F; k++) {
        var u = -1 + 2 * j / F, w = -1 + 2 * k / F;
        body.push([u, w, 1, 0.35]); body.push([u, w, -1, 0.35]);
        body.push([1, w, u, 0.35]); body.push([-1, w, u, 0.35]);
        lid.push([u, w, 0.45]);
      }
    })();

    function sizeBox() {
      BW = box.clientWidth; BH = box.clientHeight;
      box.width = BW * bdpr; box.height = BH * bdpr;
      bctx.setTransform(bdpr, 0, 0, bdpr, 0, 0);
    }

    function drawBox(now) {
      var t = (now - t0) / 1000;
      actShown += (act - actShown) * 0.12;
      var ry = reduce ? 0.7 : t * 0.45 + 0.6, rx = -0.5;
      var cY = Math.cos(ry), sY = Math.sin(ry), cX = Math.cos(rx), sX = Math.sin(rx);
      var S = BW * 0.17, ox = BW * 0.5, oy = BH * 0.66, FOV = 5;
      var lidA = actShown * 1.9; // lid swings open (radians) while a slide is coming out
      bctx.clearRect(0, 0, BW, BH);

      function dot(x, y, z, r, col, alpha) {
        var x1 = x * cY + z * sY, z1 = -x * sY + z * cY;
        var y1 = y * cX - z1 * sX, z2 = y * sX + z1 * cX;
        var k = FOV / (FOV + z2);
        bctx.globalAlpha = alpha * Math.min(1, Math.max(0.25, 0.4 + (k - 0.9) * 2));
        bctx.fillStyle = col;
        bctx.beginPath(); bctx.arc(ox + x1 * S * k, oy + y1 * S * k, r * k, 0, 6.2832); bctx.fill();
      }
      var i, p;
      for (i = 0; i < body.length; i++) { p = body[i]; dot(p[0], p[1], p[2], p[3] < 1 ? 1 : 1.5, '#b9a2f5', p[3]); }
      // lid hinges on its back edge (z = -1) at the top (y = -1)
      var ca = Math.cos(lidA), sa = Math.sin(lidA);
      for (i = 0; i < lid.length; i++) {
        p = lid[i]; var dz = p[1] + 1;
        dot(p[0], -1 - sa * dz, -1 + ca * dz, p[2] < 1 ? 1 : 1.6, '#ff5a2c', p[2]);
      }
      // dots spilling out of the open box
      if (!reduce && actShown > 0.05 && Math.random() < actShown * 1.4) {
        for (var n = 0; n < 2; n++) sparks.push({ x: (Math.random() * 2 - 1) * 0.8, y: -1, z: (Math.random() * 2 - 1) * 0.8,
          vx: (Math.random() - 0.3) * 0.05, vy: -0.04 - Math.random() * 0.05, vz: (Math.random() - 0.5) * 0.04, life: 1 });
      }
      for (i = sparks.length - 1; i >= 0; i--) {
        p = sparks[i]; p.x += p.vx; p.y += p.vy; p.z += p.vz; p.life -= 0.02;
        if (p.life <= 0) { sparks.splice(i, 1); continue; }
        dot(p.x, p.y, p.z, 1.3, i % 4 ? '#f3f0ea' : '#ff5a2c', p.life);
      }
      bctx.globalAlpha = 1;
    }

    function loop(now) {
      if (!inView || reduce) { looping = false; return; }
      drawBox(now); requestAnimationFrame(loop);
    }
    function startBox() {
      if (reduce) { drawBox(performance.now()); return; }
      if (inView && !looping) { looping = true; requestAnimationFrame(loop); }
    }

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) { inView = en[0].isIntersecting; startBox(); }).observe(root);
    } else { inView = true; }
    window.addEventListener('scroll', queue, { passive: true });
    window.addEventListener('resize', function () { sizeBox(); queue(); });
    sizeBox(); update();
  })();

  // ---------------------------------------------------------------------------
  // Division slides: the division's icon drawn in dots behind the slide.
  // Dots assemble when the slide first appears and scatter around the cursor.
  // Add logos as static/img/ventures/<slug>-mark.png (icon only).
  // ---------------------------------------------------------------------------
  (function () {
    var panels = document.querySelectorAll('.xpanel[data-art]');
    if (!panels.length) return;
    Array.prototype.forEach.call(panels, function (pnl) {
      var cv = pnl.querySelector('.xart'), g = cv.getContext('2d'), dpr = Math.min(window.devicePixelRatio || 1, 2);
      var img = new Image(), dots = [], W = 0, H = 0, inView = false, running = false;
      var mouse = { x: -999, y: -999 };

      function build(scatter) {
        W = pnl.offsetWidth; H = pnl.offsetHeight;
        if (!W || !H || !img.width) return;
        cv.width = W * dpr; cv.height = H * dpr; g.setTransform(dpr, 0, 0, dpr, 0, 0);
        var wide = W > 760;
        var size = wide ? Math.min(W * 0.42, H * 0.72) : Math.min(W * 0.8, H * 0.42);
        var ar = img.width / img.height;
        var lw = ar >= 1 ? size : size * ar, lh = ar >= 1 ? size / ar : size;
        var ox = wide ? W * 0.72 - lw / 2 : (W - lw) / 2, oy = wide ? (H - lh) / 2 : H * 0.05;
        var gap = Math.max(5, Math.round(size / 90));
        var cols = Math.max(1, Math.round(lw / gap)), rows = Math.max(1, Math.round(lh / gap));
        var c = document.createElement('canvas'); c.width = cols; c.height = rows;
        var cg = c.getContext('2d'); cg.drawImage(img, 0, 0, cols, rows);
        var d = cg.getImageData(0, 0, cols, rows).data;
        dots = [];
        for (var y = 0; y < rows; y++) for (var x = 0; x < cols; x++) {
          var i = (y * cols + x) * 4;
          var al = d[i + 3] / 255;
          if (al < 0.12) continue; // low threshold keeps thin line-art logos (e.g. Sahay) visible
          var hx = ox + x * gap, hy = oy + y * gap, far = scatter && !reduce;
          dots.push({
            hx: hx, hy: hy,
            x: far ? hx + (Math.random() - 0.5) * W * 0.7 : hx,
            y: far ? hy + (Math.random() - 0.5) * H * 0.7 : hy,
            vx: 0, vy: 0, r: gap * (0.3 + Math.random() * 0.12) * (0.6 + 0.4 * al), a: Math.min(1, al * 1.6),
            c: 'rgb(' + d[i] + ',' + d[i + 1] + ',' + d[i + 2] + ')'
          });
        }
        draw();
      }

      function step() {
        var R = 110, R2 = R * R;
        for (var i = 0; i < dots.length; i++) {
          var p = dots[i];
          p.vx += (p.hx - p.x) * 0.045; p.vy += (p.hy - p.y) * 0.045;
          var dx = p.x - mouse.x, dy = p.y - mouse.y, d2 = dx * dx + dy * dy;
          if (d2 < R2) { var f = (1 - d2 / R2) * 3, dd = Math.sqrt(d2) || 1; p.vx += dx / dd * f; p.vy += dy / dd * f; }
          p.vx *= 0.82; p.vy *= 0.82; p.x += p.vx; p.y += p.vy;
        }
      }

      function draw() {
        g.clearRect(0, 0, W, H);
        for (var i = 0; i < dots.length; i++) {
          var p = dots[i];
          g.globalAlpha = p.a; g.fillStyle = p.c; g.beginPath(); g.arc(p.x, p.y, p.r, 0, 6.2832); g.fill();
        }
        g.globalAlpha = 1;
      }

      function loop() { if (!inView || reduce) { running = false; return; } step(); draw(); requestAnimationFrame(loop); }
      function go() { if (inView && !running && !reduce && dots.length) { running = true; requestAnimationFrame(loop); } }

      pnl.addEventListener('pointermove', function (e) {
        var r = pnl.getBoundingClientRect(), k = W / (r.width || 1);
        mouse.x = (e.clientX - r.left) * k; mouse.y = (e.clientY - r.top) * k;
      });
      pnl.addEventListener('pointerleave', function () { mouse.x = mouse.y = -999; });
      window.addEventListener('resize', function () { build(false); });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (en) { inView = en[0].isIntersecting; go(); }).observe(pnl);
      } else { inView = true; }
      img.onload = function () { build(true); go(); };
      img.src = pnl.getAttribute('data-art');
    });
  })();

  // ---------------------------------------------------------------------------
  // Numbers that count up when they scroll into view: <b data-count="1000" data-suffix="+">
  // ---------------------------------------------------------------------------
  (function () {
    var nums = document.querySelectorAll('[data-count]');
    if (!nums.length || reduce || !('IntersectionObserver' in window)) return;
    function run(el) {
      var end = +el.getAttribute('data-count'), suf = el.getAttribute('data-suffix') || '', t0 = performance.now();
      (function f(now) {
        var k = Math.min(1, (now - t0) / 1600), v = Math.round(end * (1 - Math.pow(1 - k, 3)));
        el.textContent = v.toLocaleString('en-US') + suf;
        if (k < 1) requestAnimationFrame(f);
      })(t0);
    }
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (e) { if (e.isIntersecting) { io.unobserve(e.target); run(e.target); } });
    }, { threshold: 0.6 });
    nums.forEach(function (el) { el.textContent = '0' + (el.getAttribute('data-suffix') || ''); io.observe(el); });
  })();

  // ---------------------------------------------------------------------------
  // The crowd: every dot is one intern. Active cohort (accent) at the centre,
  // trained alumni around it. Dots ripple in from the centre when the section
  // appears; they twinkle gently and swell under the cursor.
  // ---------------------------------------------------------------------------
  (function () {
    var cv = document.querySelector('.crowd');
    if (!cv) return;
    var cx2 = cv.getContext('2d'), dpr2 = Math.min(window.devicePixelRatio || 1, 2);
    var TRAINED = +cv.getAttribute('data-trained') || 1000, ACTIVE = +cv.getAttribute('data-active') || 500;
    var TOTAL = TRAINED + ACTIVE, dots = [], W = 0, H = 0, gap = 0, start = 0, seen = false, running = false, inView = false;
    var mouse = { x: -999, y: -999 };

    function build() {
      W = cv.clientWidth; H = cv.clientHeight;
      cv.width = W * dpr2; cv.height = H * dpr2; cx2.setTransform(dpr2, 0, 0, dpr2, 0, 0);
      var cols = Math.ceil(Math.sqrt(TOTAL * W / H)), rows = Math.ceil(TOTAL / cols);
      gap = Math.min(W / cols, H / rows);
      var ox = (W - gap * (cols - 1)) / 2, oy = (H - gap * (rows - 1)) / 2, cells = [];
      for (var r = 0; r < rows; r++) for (var c = 0; c < cols; c++) {
        var x = ox + c * gap, y = oy + r * gap;
        var d = Math.hypot((x - W / 2) / W, (y - H / 2) / H) + Math.random() * 0.06; // organic edge
        cells.push({ x: x, y: y, d: d, ph: Math.random() * 6.28 });
      }
      cells.sort(function (a, b) { return a.d - b.d; });
      dots = cells.map(function (c, i) { c.kind = i < ACTIVE ? 2 : i < TOTAL ? 1 : 0; c.order = i / cells.length; return c; });
    }

    function draw(now) {
      var t = seen ? (now - start) / 1000 : 0;
      cx2.clearRect(0, 0, W, H);
      var base = gap * 0.3;
      for (var i = 0; i < dots.length; i++) {
        var p = dots[i];
        var pop = reduce ? 1 : Math.max(0, Math.min(1, (t - p.order * 1.6) / 0.35)); // ripple outward
        if (pop <= 0) continue;
        var r = base * (p.kind === 0 ? 0.5 : 1) * (0.6 + 0.4 * pop);
        if (p.kind === 2 && !reduce) r *= 1 + 0.18 * Math.sin(now / 600 + p.ph); // active cohort breathes
        var dx = p.x - mouse.x, dy = p.y - mouse.y, d2 = dx * dx + dy * dy, R = gap * 5;
        if (d2 < R * R) r *= 1 + 0.9 * (1 - Math.sqrt(d2) / R);
        cx2.globalAlpha = pop * (p.kind === 0 ? 0.15 : p.kind === 1 ? 0.7 : 1);
        cx2.fillStyle = p.kind === 2 ? '#ff5a2c' : '#d6d3cb';
        cx2.beginPath(); cx2.arc(p.x, p.y, r, 0, 6.2832); cx2.fill();
      }
      cx2.globalAlpha = 1;
    }

    function loop(now) { if (!inView) { running = false; return; } draw(now); requestAnimationFrame(loop); }
    function go() { if (reduce) { draw(0); return; } if (inView && !running) { running = true; requestAnimationFrame(loop); } }

    cv.addEventListener('pointermove', function (e) { var r = cv.getBoundingClientRect(); mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top; });
    cv.addEventListener('pointerleave', function () { mouse.x = mouse.y = -999; });
    window.addEventListener('resize', function () { build(); if (reduce || !running) draw(performance.now()); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) {
        inView = en[0].isIntersecting;
        if (inView && !seen) { seen = true; start = performance.now(); }
        go();
      }, { threshold: 0.25 }).observe(cv);
    } else { seen = true; inView = true; }
    build(); go();
  })();

  // ---------------------------------------------------------------------------
  // Hero: the Belvo "B" mark as a 3D field of dots.
  // The logo image is sampled into points, given depth, rotated in 3D and
  // projected with perspective. The cursor tilts the mark and pushes dots
  // away; they spring back. Click to burst the mark apart and reassemble.
  // ---------------------------------------------------------------------------
  var hero = document.querySelector('.hero');
  var canvas = hero && hero.querySelector('canvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var LOGO = hero.getAttribute('data-logo') || '/static/img/belvo-mark.png';
  var COUNT = window.innerWidth < 760 ? 1500 : 3400; // number of dots
  var DEPTH = 0.18;   // thickness of the mark (logo half-size = 1)
  var FOV = 3.2;      // perspective strength (smaller = stronger)
  var SPRING = 0.022, DAMP = 0.88;

  var W = 0, H = 0, cx = 0, cy = 0, scale = 1, small = false;
  var parts = [], running = false, visible = true, t0 = performance.now();
  var mouse = { x: -9999, y: -9999, nx: 0, ny: 0 };
  var rot = { x: 0, y: 0 };

  // Read the logo pixels and keep the coloured (non-white, non-transparent) ones
  function sample(img) {
    var S = 300, r = Math.min(S / img.width, S / img.height);
    var w = Math.max(1, Math.round(img.width * r)), h = Math.max(1, Math.round(img.height * r));
    var c = document.createElement('canvas'); c.width = w; c.height = h;
    var g = c.getContext('2d'); g.drawImage(img, 0, 0, w, h);
    var d = g.getImageData(0, 0, w, h).data, pts = [];
    var x0 = w, y0 = h, x1 = 0, y1 = 0;
    for (var y = 0; y < h; y++) for (var x = 0; x < w; x++) {
      var i = (y * w + x) * 4, R = d[i], G = d[i + 1], B = d[i + 2];
      if (d[i + 3] < 128) continue; // transparent
      if (Math.max(R, G, B) - Math.min(R, G, B) < 40 || (R + G + B) / 3 > 235) continue; // white/grey background
      pts.push([x, y, R, G, B]);
      if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
    }
    return { pts: pts, cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, half: Math.max(x1 - x0, y1 - y0) / 2 || 1 };
  }

  function build(s) {
    var pts = s.pts; if (!pts.length) return;
    parts = [];
    for (var n = 0; n < COUNT; n++) {
      var p = pts[(Math.random() * pts.length) | 0];
      var lift = 0.3; // brighten the logo colour so it glows on the dark hero
      var R = p[2] + (255 - p[2]) * lift, G = p[3] + (255 - p[3]) * lift, B = p[4] + (255 - p[4]) * lift;
      var spark = Math.random() < 0.05;
      // start scattered in a wide sphere so the mark assembles on load
      var a = Math.random() * 6.2832, b = Math.acos(Math.random() * 2 - 1), rad = 2 + Math.random() * 2;
      parts.push({
        hx: (p[0] + Math.random() - 0.5 - s.cx) / s.half,
        hy: (p[1] + Math.random() - 0.5 - s.cy) / s.half,
        hz: (Math.random() * 2 - 1) * DEPTH,
        x: Math.sin(b) * Math.cos(a) * rad, y: Math.sin(b) * Math.sin(a) * rad, z: Math.cos(b) * rad,
        vx: 0, vy: 0, vz: 0,
        s: 0.7 + Math.random() * 1.1,
        c: spark ? '#ffffff' : 'rgb(' + (R | 0) + ',' + (G | 0) + ',' + (B | 0) + ')'
      });
    }
    if (reduce) settle();
  }

  function layout() {
    var r = hero.getBoundingClientRect();
    W = r.width; H = r.height; small = W < 760;
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (small) { cx = W * 0.5; cy = H * 0.28; scale = Math.min(W * 0.4, H * 0.22); }
    else { cx = W * 0.7; cy = H * 0.45; scale = Math.min(W * 0.25, H * 0.36); }
    if (!running) draw();
  }

  // Snap every dot into place (used for reduced motion)
  function settle() {
    for (var i = 0; i < parts.length; i++) { var p = parts[i]; p.x = p.hx; p.y = p.hy; p.z = p.hz; }
    draw();
  }

  function step(now) {
    var t = (now - t0) / 1000;
    // gentle idle sway + cursor tilt, eased
    var ty = Math.sin(t * 0.35) * 0.45 + mouse.nx * 0.6;
    var tx = Math.sin(t * 0.27) * 0.12 + mouse.ny * 0.35;
    rot.y += (ty - rot.y) * 0.05; rot.x += (tx - rot.x) * 0.05;
    var cY = Math.cos(rot.y), sY = Math.sin(rot.y), cX = Math.cos(rot.x), sX = Math.sin(rot.x);
    var RR = scale * 0.32, R2 = RR * RR;

    for (var i = 0; i < parts.length; i++) {
      var p = parts[i];
      // home position rotated into world space
      var x1 = p.hx * cY + p.hz * sY, z1 = -p.hx * sY + p.hz * cY;
      var y1 = p.hy * cX - z1 * sX, z2 = p.hy * sX + z1 * cX;
      p.vx += (x1 - p.x) * SPRING; p.vy += (y1 - p.y) * SPRING; p.vz += (z2 - p.z) * SPRING;

      // cursor pushes dots outward on screen and toward the viewer
      var k = FOV / (FOV + p.z);
      var dx = cx + p.x * scale * k - mouse.x, dy = cy + p.y * scale * k - mouse.y, d2 = dx * dx + dy * dy;
      if (d2 < R2) {
        var f = (1 - d2 / R2) * 0.03, d = Math.sqrt(d2) || 1;
        p.vx += dx / d * f; p.vy += dy / d * f; p.vz -= f * 0.8;
      }
      p.vx *= DAMP; p.vy *= DAMP; p.vz *= DAMP;
      p.x += p.vx; p.y += p.vy; p.z += p.vz;
    }
    draw();
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    var fade = small ? 0.6 : 1; // keep text readable on phones, where it overlaps
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i];
      if (p.z <= -FOV + 0.2) continue;
      var k = FOV / (FOV + p.z);
      ctx.globalAlpha = Math.min(1, Math.max(0.15, 0.3 + (k - 0.9) * 2.4)) * fade;
      ctx.fillStyle = p.c;
      ctx.beginPath();
      ctx.arc(cx + p.x * scale * k, cy + p.y * scale * k, p.s * k, 0, 6.2832);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function tick(now) { if (!running) return; step(now); requestAnimationFrame(tick); }
  function start() { if (running || reduce || !visible || !parts.length) return; running = true; requestAnimationFrame(tick); }
  function stop() { running = false; }

  // Click (not on a link/button) bursts the mark; the springs pull it back together
  function burst() {
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i], a = Math.random() * 6.2832, b = Math.acos(Math.random() * 2 - 1), v = 0.08 + Math.random() * 0.16;
      p.vx += Math.sin(b) * Math.cos(a) * v; p.vy += Math.sin(b) * Math.sin(a) * v; p.vz += Math.cos(b) * v;
    }
  }

  hero.addEventListener('pointermove', function (e) {
    var r = hero.getBoundingClientRect();
    mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top;
    mouse.nx = (mouse.x - cx) / (W / 2); mouse.ny = (mouse.y - cy) / (H / 2);
  });
  hero.addEventListener('pointerleave', function () { mouse.x = mouse.y = -9999; mouse.nx = mouse.ny = 0; });
  hero.addEventListener('click', function (e) {
    if (e.target.closest('a,button') || reduce) return;
    burst();
  });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (en) { visible = en[0].isIntersecting; if (visible) start(); else stop(); }).observe(hero);
  }
  window.addEventListener('resize', layout);
  layout();

  var img = new Image();
  img.onload = function () { build(sample(img)); start(); };
  img.src = LOGO;
})();

/* ---------- Products & Services: 3D Flip Cards — Click to Flip (all devices) ---------- */
(function () {
  var cards = document.querySelectorAll('.flip-card');
  if (!cards.length) return;

  cards.forEach(function (card) {
    /* Accessibility attributes */
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');

    /* Click: toggle flip; let links and buttons inside pass through normally */
    card.addEventListener('click', function (e) {
      if (e.target.closest('a, button')) return;
      card.classList.toggle('is-flipped');
    });

    /* Keyboard: Enter or Space toggles flip */
    card.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        card.classList.toggle('is-flipped');
      }
    });
  });
})();

