/**
 * Belvo Insights & 3D Interactive Ecosystem Engine
 * High-performance 3D Canvas Particle Network, Filter Systems & Interactions
 */
(function () {
  'use strict';

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // =========================================================================
  // 1. FULL-BLEED MESMERIZING 3D ECOSYSTEM HERO CANVAS
  // =========================================================================
  var heroSection = document.getElementById('hero');
  var canvas = document.getElementById('ecosystem3d-canvas');

  if (canvas && heroSection) {
    var ctx = canvas.getContext('2d');
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var W = 0, H = 0, cx = 0, cy = 0, scale = 1;
    var running = false, inView = true;
    var t0 = performance.now();

    var mouse = { x: -9999, y: -9999, nx: 0, ny: 0 };
    var rot = { x: -0.38, y: 0 };
    var hoveredNode = null;

    var COUNT = window.innerWidth < 768 ? 850 : 1600;
    var FOV = 3.6;
    var particles = [];

    // Exactly 9 Venture Orbital Nodes with Verified Metadata
    var VENTURE_NODES = [
      { id: 1, name: "CAPVANTA", sector: "Business Advisory & Funding", slug: "capvanta", angle: 0, r: 1.45, color: "#8a5cf6" },
      { id: 2, name: "VERDICT", sector: "Legal Services", slug: "verdict", angle: (Math.PI * 2 / 9) * 1, r: 1.5, color: "#b9a2f5" },
      { id: 3, name: "KLYRO", sector: "Digital Solutions", slug: "klyro", angle: (Math.PI * 2 / 9) * 2, r: 1.44, color: "#6366f1" },
      { id: 4, name: "FYNDRA", sector: "Finance & Accounting", slug: "fyndra", angle: (Math.PI * 2 / 9) * 3, r: 1.52, color: "#8a5cf6" },
      { id: 5, name: "TATTVA", sector: "Interior Design", slug: "tattva", angle: (Math.PI * 2 / 9) * 4, r: 1.46, color: "#b9a2f5" },
      { id: 6, name: "BELVO DIGITAL", sector: "Digital Marketing & Creative", slug: "belvo-digital", angle: (Math.PI * 2 / 9) * 5, r: 1.5, color: "#ff5a2c" },
      { id: 7, name: "HRIDAYAM", sector: "Education & Courses", slug: "hridayam", angle: (Math.PI * 2 / 9) * 6, r: 1.45, color: "#b9a2f5" },
      { id: 8, name: "SAHAYA", sector: "NGO & Social Impact", slug: "sahaya", angle: (Math.PI * 2 / 9) * 7, r: 1.52, color: "#3ddc97" },
      { id: 9, name: "BELQORA", sector: "SaaS & Business Software", slug: "belqora", angle: (Math.PI * 2 / 9) * 8, r: 1.58, color: "#a855f7" }
    ];

    function initParticles() {
      particles = [];
      for (var i = 0; i < COUNT; i++) {
        var arm = i % 3;
        var armAngle = arm * (Math.PI * 2 / 3);
        var dist = Math.pow(Math.random(), 0.65) * 1.85;
        var theta = dist * 3.4 + armAngle + (Math.random() - 0.5) * 0.35;
        var zDist = (Math.random() - 0.5) * 0.3 * (1 + dist);

        if (i < COUNT * 0.22) {
          dist = Math.random() * 0.55;
          theta = Math.random() * Math.PI * 2;
          zDist = (Math.random() - 0.5) * 0.18;
        }

        var isPurple = Math.random() > 0.32;
        var isAccent = Math.random() < 0.08;
        var col = isAccent ? '#ff5a2c' : isPurple ? (Math.random() > 0.5 ? '#b9a2f5' : '#8a5cf6') : '#ffffff';

        particles.push({
          x: Math.cos(theta) * dist,
          y: Math.sin(theta) * dist,
          z: zDist,
          ox: Math.cos(theta) * dist,
          oy: Math.sin(theta) * dist,
          oz: zDist,
          vx: 0,
          vy: 0,
          size: 0.75 + Math.random() * 1.35,
          color: col,
          alpha: 0.3 + Math.random() * 0.65,
          speed: 0.0003 + Math.random() * 0.0006
        });
      }
    }

    function resize() {
      var r = heroSection.getBoundingClientRect();
      W = r.width || window.innerWidth;
      H = r.height || window.innerHeight;
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      if (W < 900) {
        cx = W * 0.5;
        cy = H * 0.28;
        scale = Math.min(W * 0.42, H * 0.24);
      } else {
        cx = W * 0.72;
        cy = H * 0.46;
        scale = Math.min(W * 0.26, H * 0.38);
      }
    }

    function step(now) {
      var t = (now - t0) * 0.001;

      // Smooth Inertial Sway + Cursor Parallax
      var targetRotY = Math.sin(t * 0.25) * 0.32 + mouse.nx * 0.45;
      var targetRotX = -0.38 + Math.sin(t * 0.2) * 0.08 + mouse.ny * 0.25;
      rot.y += (targetRotY - rot.y) * 0.045;
      rot.x += (targetRotX - rot.x) * 0.045;

      var cY = Math.cos(rot.y), sY = Math.sin(rot.y);
      var cX = Math.cos(rot.x), sX = Math.sin(rot.x);

      ctx.clearRect(0, 0, W, H);

      // 1. Ambient Central Core Nebula Glow
      var coreGlow = ctx.createRadialGradient(cx, cy, 4, cx, cy, scale * 0.7);
      coreGlow.addColorStop(0, 'rgba(138, 92, 246, 0.26)');
      coreGlow.addColorStop(0.45, 'rgba(76, 29, 149, 0.1)');
      coreGlow.addColorStop(1, 'rgba(12, 12, 16, 0)');
      ctx.fillStyle = coreGlow;
      ctx.beginPath();
      ctx.arc(cx, cy, scale * 0.7, 0, Math.PI * 2);
      ctx.fill();

      // 2. Faint 3D Orbital Plane Rings
      var ringRadii = [1.1, 1.5];
      for (var rIdx = 0; rIdx < ringRadii.length; rIdx++) {
        var rr = ringRadii[rIdx] * scale;
        ctx.save();
        ctx.translate(cx, cy);
        ctx.scale(1, Math.abs(cX) * 0.7 + 0.3);
        ctx.rotate(rot.y * 0.2);
        ctx.strokeStyle = 'rgba(138, 92, 246, 0.12)';
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 8]);
        ctx.beginPath();
        ctx.arc(0, 0, rr, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      }

      // 3. Project 9 Venture Nodes in 3D
      var projectedNodes = [];
      var newlyHovered = null;

      for (var n = 0; n < VENTURE_NODES.length; n++) {
        var node = VENTURE_NODES[n];
        var curAngle = node.angle + t * 0.1;
        var nx = Math.cos(curAngle) * node.r;
        var ny = Math.sin(curAngle) * node.r;
        var nz = Math.sin(curAngle * 2) * 0.14;

        var x1 = nx * cY + nz * sY;
        var z1 = -nx * sY + nz * cY;
        var y1 = ny * cX - z1 * sX;
        var z2 = ny * sX + z1 * cX;

        var k = FOV / (FOV + z2);
        var px = cx + x1 * scale * k;
        var py = cy + y1 * scale * k;
        var nodeSize = (window.innerWidth < 680 ? 5 : 6.5) * k;

        // Hover test
        var distToMouse = Math.hypot(mouse.x - px, mouse.y - py);
        var isNodeHovered = distToMouse < Math.max(24, nodeSize * 2.5);
        if (isNodeHovered) {
          newlyHovered = node;
        }

        projectedNodes.push({
          id: node.id,
          name: node.name,
          sector: node.sector,
          slug: node.slug,
          color: node.color,
          px: px,
          py: py,
          k: k,
          size: nodeSize,
          isHovered: isNodeHovered
        });

        // Delicate Laser Beam to Central Core
        var beamAlpha = isNodeHovered ? 0.65 : 0.18 * k;
        ctx.strokeStyle = isNodeHovered ? 'rgba(255, 90, 44, ' + beamAlpha + ')' : 'rgba(138, 92, 246, ' + beamAlpha.toFixed(3) + ')';
        ctx.lineWidth = (isNodeHovered ? 2 : 1) * k;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(px, py);
        ctx.stroke();

        // Pulsing Light Packet along laser beam
        var pulseProgress = ((t * 0.35 + n * 0.11) % 1.0);
        var pX = cx + (px - cx) * pulseProgress;
        var pY = cy + (py - cy) * pulseProgress;
        ctx.fillStyle = isNodeHovered ? '#ff5a2c' : '#ffffff';
        ctx.beginPath();
        ctx.arc(pX, pY, Math.max(1.2, 2.2 * k), 0, Math.PI * 2);
        ctx.fill();
      }

      // Connecting Constellation Filament Ring
      for (var p = 0; p < projectedNodes.length; p++) {
        var nextP = (p + 1) % projectedNodes.length;
        ctx.strokeStyle = 'rgba(185, 162, 245, 0.1)';
        ctx.lineWidth = 0.8;
        ctx.beginPath();
        ctx.moveTo(projectedNodes[p].px, projectedNodes[p].py);
        ctx.lineTo(projectedNodes[nextP].px, projectedNodes[nextP].py);
        ctx.stroke();
      }

      // 4. Draw Stratified Particle Cloud with Interactive Cursor Ripple
      var RR = scale * 0.38, R2 = RR * RR;

      for (var i = 0; i < particles.length; i++) {
        var pt = particles[i];
        var cosO = Math.cos(pt.speed);
        var sinO = Math.sin(pt.speed);
        var newX = pt.x * cosO - pt.y * sinO;
        var newY = pt.x * sinO + pt.y * cosO;
        pt.x = newX;
        pt.y = newY;

        var px1 = pt.x * cY + pt.z * sY;
        var pz1 = -pt.x * sY + pt.z * cY;
        var py1 = pt.y * cX - pz1 * sX;
        var pz2 = pt.y * sX + pz1 * cX;

        var pk = FOV / (FOV + pz2);
        var scrX = cx + px1 * scale * pk;
        var scrY = cy + py1 * scale * pk;

        // Interactive Cursor Ripple
        var ddx = scrX - mouse.x, ddy = scrY - mouse.y, d2 = ddx * ddx + ddy * ddy;
        if (d2 < R2) {
          var f = (1 - d2 / R2) * 0.012, dd = Math.sqrt(d2) || 1;
          pt.x += (ddx / dd) * f;
          pt.y += (ddy / dd) * f;
        }

        if (scrX < -20 || scrX > W + 20 || scrY < -20 || scrY > H + 20) continue;

        ctx.globalAlpha = Math.max(0.06, Math.min(0.9, pt.alpha * pk));
        ctx.fillStyle = pt.color;
        ctx.beginPath();
        ctx.arc(scrX, scrY, Math.max(0.6, pt.size * pk), 0, Math.PI * 2);
        ctx.fill();
      }

      // 5. Render Venture Nodes & Labels on top with depth
      for (var m = 0; m < projectedNodes.length; m++) {
        var pn = projectedNodes[m];
        ctx.globalAlpha = Math.max(0.4, Math.min(1, pn.k));

        // Sonar Wave for Hovered Node
        if (pn.isHovered) {
          ctx.strokeStyle = 'rgba(255, 90, 44, 0.8)';
          ctx.lineWidth = 1.8;
          ctx.beginPath();
          ctx.arc(pn.px, pn.py, pn.size * 2.2, 0, Math.PI * 2);
          ctx.stroke();
        }

        // Glowing Node Core
        ctx.fillStyle = pn.color;
        ctx.beginPath();
        ctx.arc(pn.px, pn.py, pn.size, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = pn.isHovered ? '#ff5a2c' : '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(pn.px, pn.py, pn.size + 2.5, 0, Math.PI * 2);
        ctx.stroke();

        // Node Label with Crisp Background Shadow
        if (pn.k > 0.82) {
          ctx.save();
          ctx.font = '600 ' + (pn.isHovered ? '11px' : '9.5px') + ' "Inter Tight", sans-serif';
          ctx.textAlign = 'center';
          ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
          ctx.shadowBlur = 6;
          ctx.fillStyle = pn.isHovered ? '#ff5a2c' : '#ffffff';
          ctx.fillText(pn.name, pn.px, pn.py + pn.size + 14);
          ctx.restore();
        }
      }

      // 6. Central Belvo Monogram Core
      ctx.globalAlpha = 1;
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(cx, cy, 7, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = '#ff5a2c';
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      ctx.arc(cx, cy, 14, 0, Math.PI * 2);
      ctx.stroke();

      // Update Cursor state
      hoveredNode = newlyHovered;
      canvas.style.cursor = hoveredNode ? 'pointer' : 'default';
    }

    function loop(now) {
      if (!inView || reduce) { running = false; return; }
      step(now);
      requestAnimationFrame(loop);
    }

    function start() {
      if (reduce) { step(performance.now()); return; }
      if (inView && !running) {
        running = true;
        requestAnimationFrame(loop);
      }
    }

    // Pointer Interactivity (Cursor Tracking)
    window.addEventListener('pointermove', function (e) {
      var rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
      mouse.nx = (mouse.x - cx) / (W * 0.5 || 1);
      mouse.ny = (mouse.y - cy) / (H * 0.5 || 1);
    });

    window.addEventListener('pointerleave', function () {
      mouse.x = -9999;
      mouse.y = -9999;
      mouse.nx = 0;
      mouse.ny = 0;
      hoveredNode = null;
    });

    canvas.addEventListener('click', function () {
      if (hoveredNode) {
        window.location.href = '/ventures/' + hoveredNode.slug;
      }
    });

    initParticles();
    resize();
    window.addEventListener('resize', resize);

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        inView = entries[0].isIntersecting;
        if (inView) start();
        else running = false;
      }).observe(canvas);
    }

    start();
  }

  // =========================================================================
  // 2. BELQORA 12-CATEGORY SWITCHER
  // =========================================================================
  var catPills = document.querySelectorAll('[data-cat-target]');
  var catDecks = document.querySelectorAll('[data-cat-deck]');
  if (catPills.length && catDecks.length) {
    catPills.forEach(function (pill) {
      pill.addEventListener('click', function () {
        var target = pill.getAttribute('data-cat-target');
        catPills.forEach(function (p) { p.classList.toggle('active', p === pill); });
        catDecks.forEach(function (deck) {
          if (deck.getAttribute('data-cat-deck') === target) {
            deck.style.display = 'grid';
            deck.classList.add('in');
          } else {
            deck.style.display = 'none';
          }
        });
      });
    });
  }

  // =========================================================================
  // 3. EDITORIAL SEARCH & CATEGORY FILTERING (SECTION 15)
  // =========================================================================
  var searchInput = document.getElementById('insights-search');
  var articleFilterPills = document.querySelectorAll('[data-filter-cat]');
  var articleCards = document.querySelectorAll('[data-article-item]');
  var articleCountEl = document.getElementById('articles-count-text');
  var currentCat = 'all';

  function filterArticles() {
    var query = (searchInput ? searchInput.value.toLowerCase().trim() : '');
    var visibleCount = 0;

    articleCards.forEach(function (card) {
      var cat = card.getAttribute('data-article-cat') || '';
      var title = (card.querySelector('.article-card-title') || {}).textContent || '';
      var desc = (card.querySelector('.article-card-excerpt') || {}).textContent || '';
      var combined = (title + ' ' + desc + ' ' + cat).toLowerCase();

      var matchesCat = (currentCat === 'all' || cat === currentCat);
      var matchesQuery = (!query || combined.indexOf(query) !== -1);

      if (matchesCat && matchesQuery) {
        card.style.display = '';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    if (articleCountEl) {
      articleCountEl.textContent = 'Showing ' + visibleCount + ' of ' + articleCards.length + ' articles';
    }
  }

  if (searchInput) {
    searchInput.addEventListener('input', filterArticles);
  }

  if (articleFilterPills.length) {
    articleFilterPills.forEach(function (pill) {
      pill.addEventListener('click', function () {
        articleFilterPills.forEach(function (p) { p.classList.toggle('active', p === pill); });
        currentCat = pill.getAttribute('data-filter-cat') || 'all';
        filterArticles();
      });
    });
  }

  // =========================================================================
  // 4. INTERACTIVE SHARE MODAL
  // =========================================================================
  var shareModal = document.getElementById('share-modal');
  var shareTriggers = document.querySelectorAll('[data-share-trigger]');
  var shareClose = document.getElementById('share-modal-close');
  var activeShareUrl = window.location.href;
  var activeShareTitle = document.title;

  if (shareModal) {
    shareTriggers.forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        activeShareUrl = btn.getAttribute('data-share-url') || window.location.href;
        activeShareTitle = btn.getAttribute('data-share-title') || document.title;
        shareModal.classList.add('open');
      });
    });

    if (shareClose) {
      shareClose.addEventListener('click', function () {
        shareModal.classList.remove('open');
      });
    }

    shareModal.addEventListener('click', function (e) {
      if (e.target === shareModal) shareModal.classList.remove('open');
    });

    var copyBtn = document.getElementById('share-copy-btn');
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        navigator.clipboard.writeText(activeShareUrl).then(function () {
          copyBtn.textContent = 'Copied!';
          setTimeout(function () { copyBtn.textContent = 'Copy Link'; }, 2000);
        });
      });
    }

    var liBtn = document.getElementById('share-li-btn');
    if (liBtn) {
      liBtn.addEventListener('click', function () {
        window.open('https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(activeShareUrl), '_blank');
      });
    }

    var xBtn = document.getElementById('share-x-btn');
    if (xBtn) {
      xBtn.addEventListener('click', function () {
        window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent(activeShareTitle) + '&url=' + encodeURIComponent(activeShareUrl), '_blank');
      });
    }

    var waBtn = document.getElementById('share-wa-btn');
    if (waBtn) {
      waBtn.addEventListener('click', function () {
        window.open('https://api.whatsapp.com/send?text=' + encodeURIComponent(activeShareTitle + ' ' + activeShareUrl), '_blank');
      });
    }
  }

  // =========================================================================
  // 5. NEWSLETTER SUBMISSION MOCK WITH INLINE FEEDBACK
  // =========================================================================
  var newsletterForm = document.getElementById('newsletter-form');
  var newsletterMsg = document.getElementById('newsletter-msg');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = newsletterForm.querySelector('input[type="email"]');
      if (input && input.value) {
        if (newsletterMsg) {
          newsletterMsg.style.display = 'block';
          newsletterMsg.textContent = 'Thank you for subscribing to Belvo Insights.';
        }
        input.value = '';
      }
    });
  }

  // =========================================================================
  // 6. NINE VENTURES CLEAN HORIZONTAL SLIDER WITH ARROW CONTROLS
  // =========================================================================
  var vViewport = document.getElementById('v-slider-viewport');
  var vTrack = document.getElementById('v-slider-track');
  var vArrowPrev = document.getElementById('v-arrow-prev');
  var vArrowNext = document.getElementById('v-arrow-next');
  var vCounter = document.getElementById('v-nav-counter');
  var vProgress = document.getElementById('v-slider-progress');

  if (vViewport && vTrack) {
    var vItems = vTrack.querySelectorAll('.v-slider-item');
    var totalItems = vItems.length;

    function getCardStep() {
      if (vItems.length > 1) {
        var r0 = vItems[0].getBoundingClientRect();
        var r1 = vItems[1].getBoundingClientRect();
        return r1.left - r0.left;
      }
      return vViewport.offsetWidth * 0.8;
    }

    function updateNavState() {
      var scrollLeft = vViewport.scrollLeft;
      var maxScroll = vViewport.scrollWidth - vViewport.clientWidth;
      var step = getCardStep();

      // Estimate current active card (1-based)
      var curIndex = Math.min(totalItems, Math.max(1, Math.round(scrollLeft / (step || 1)) + 1));

      if (vCounter) {
        vCounter.textContent = (curIndex < 10 ? '0' : '') + curIndex + ' / ' + (totalItems < 10 ? '0' : '') + totalItems;
      }

      if (vProgress) {
        var progressRatio = maxScroll > 0 ? scrollLeft / maxScroll : 0;
        var translateX = progressRatio * (240 - (240 * (1 / totalItems)));
        vProgress.style.transform = 'translateX(' + translateX.toFixed(1) + 'px)';
      }

      if (vArrowPrev) {
        vArrowPrev.disabled = scrollLeft <= 8;
      }
      if (vArrowNext) {
        vArrowNext.disabled = scrollLeft >= maxScroll - 8;
      }
    }

    if (vArrowNext) {
      vArrowNext.addEventListener('click', function () {
        var step = getCardStep();
        vViewport.scrollBy({ left: step, behavior: 'smooth' });
      });
    }

    if (vArrowPrev) {
      vArrowPrev.addEventListener('click', function () {
        var step = getCardStep();
        vViewport.scrollBy({ left: -step, behavior: 'smooth' });
      });
    }

    vViewport.addEventListener('scroll', updateNavState, { passive: true });
    window.addEventListener('resize', updateNavState);
    setTimeout(updateNavState, 150);

    // Simple Drag-to-scroll for desktop mouse
    var isPointerDown = false;
    var startX = 0;
    var startScrollLeft = 0;
    var dragMoved = 0;

    vViewport.addEventListener('mousedown', function (e) {
      isPointerDown = true;
      startX = e.pageX - vViewport.offsetLeft;
      startScrollLeft = vViewport.scrollLeft;
      dragMoved = 0;
      vViewport.classList.add('is-dragging');
    });

    window.addEventListener('mouseup', function () {
      if (isPointerDown) {
        isPointerDown = false;
        vViewport.classList.remove('is-dragging');
      }
    });

    vViewport.addEventListener('mousemove', function (e) {
      if (!isPointerDown) return;
      e.preventDefault();
      var x = e.pageX - vViewport.offsetLeft;
      var walk = (x - startX) * 1.4;
      vViewport.scrollLeft = startScrollLeft - walk;
      dragMoved += Math.abs(walk);
    });

    // Suppress accidental click when dragged
    var itemLinks = vTrack.querySelectorAll('a');
    itemLinks.forEach(function (link) {
      link.addEventListener('click', function (e) {
        if (dragMoved > 8) {
          e.preventDefault();
          e.stopPropagation();
        }
      });
    });
  }

  // =========================================================================
  // 7. STICKY SUBNAV SCROLL SPY
  // =========================================================================
  var subnavLinks = document.querySelectorAll('.subnav-links a');
  if (subnavLinks.length) {
    var sectionTargets = [];
    subnavLinks.forEach(function (link) {
      var href = link.getAttribute('href');
      if (href && href.startsWith('#')) {
        var el = document.getElementById(href.substring(1));
        if (el) sectionTargets.push({ link: link, el: el });
      }
    });

    window.addEventListener('scroll', function () {
      var scrollPos = window.scrollY + 140;
      var cur = sectionTargets[0] ? sectionTargets[0].link : null;
      for (var s = 0; s < sectionTargets.length; s++) {
        if (sectionTargets[s].el.offsetTop <= scrollPos) {
          cur = sectionTargets[s].link;
        }
      }
      subnavLinks.forEach(function (lnk) { lnk.classList.toggle('active', lnk === cur); });
    }, { passive: true });
  }

  // =========================================================================
  // 7. INTERACTIVE 3D TILT & LIGHT SHINE TRACKER FOR FLOATING CARDS
  // =========================================================================
  var cards3D = document.querySelectorAll('.float-3d-card, .v-card, .b-product-card, .office-snap-card, .tech-tile, .article-card');
  if (cards3D.length && !reduce) {
    cards3D.forEach(function (card) {
      card.addEventListener('pointermove', function (e) {
        var r = card.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        var rY = x * 14, rX = -y * 10;
        card.style.transform = 'perspective(900px) translateY(-10px) rotateX(' + rX.toFixed(2) + 'deg) rotateY(' + rY.toFixed(2) + 'deg) scale(1.02)';
        var shine = card.querySelector('.float-3d-shine, .g3d-shine');
        if (shine) {
          shine.style.transition = 'none';
          shine.style.transform = 'translateX(' + (x * 240).toFixed(1) + '%)';
        }
      });
      card.addEventListener('pointerleave', function () {
        card.style.transform = '';
        var shine = card.querySelector('.float-3d-shine, .g3d-shine');
        if (shine) {
          shine.style.transition = '';
          shine.style.transform = 'translateX(-120%)';
        }
      });
    });
  }

})();
