/* ============================================================
   Scroll Animations – anime.js-inspired initialiser
   ============================================================ */

(function () {
  'use strict';

  /* Respect prefers-reduced-motion */
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  /* Export as global so anime-animations.js (module) can share the same check */
  window.SA_REDUCED_MOTION = reducedMotion;

  /* ── 1. Scroll Progress Bar ──────────────────────────────── */
  var bar = document.getElementById('scroll-progress');

  function updateProgressBar() {
    if (!bar) { return; }
    var docH = document.documentElement.scrollHeight - window.innerHeight;
    var pct  = docH > 0 ? (window.scrollY / docH * 100) : 0;
    bar.style.width = pct.toFixed(2) + '%';
    /* Item 9: reward user for nearing the end of the page */
    if (pct > 85) {
      bar.classList.add('sa-bar-glow');
    } else {
      bar.classList.remove('sa-bar-glow');
    }
  }

  window.addEventListener('scroll', updateProgressBar, { passive: true });
  updateProgressBar();

  /* ── 2. Section-title animated underline ─────────────────── */
  document.querySelectorAll('h2.section-title.fade-in').forEach(function (el) {
    var line = document.createElement('span');
    line.className = 'sa-title-line';
    line.setAttribute('aria-hidden', 'true');
    el.appendChild(line);
  });

  /* ── 3. Stagger delays for card grids ────────────────────── */
  /* Override the per-card inline transition-delay so each batch
     always cascades from index 0 with 85 ms spacing.           */
  var STAGGER_MS = 85;

  [
    '.interests-grid  .interest-card.fade-in',
    '.projects-grid   .project-card.fade-in',
    '.clinical-grid   .clinical-card.fade-in',
    '.materials-grid  .material-card.fade-in',
  ].forEach(function (sel) {
    document.querySelectorAll(sel).forEach(function (card, i) {
      card.style.transitionDelay = (i * STAGGER_MS) + 'ms';
    });
  });

  /* ── 4. Counter animation for [data-count] ───────────────── */
  function easeOutExpo(t) {
    return t >= 1 ? 1 : 1 - Math.pow(2, -10 * t);
  }

  function runCounter(el) {
    var target   = parseInt(el.getAttribute('data-count'), 10);
    var duration = 1280;
    var startTs  = null;
    /* SVG ring: r=28, circumference = 2π×28 ≈ 175.93 */
    var CIRC     = 2 * Math.PI * 28;
    var ringWrap = el.closest ? el.closest('.stat-ring-wrap') : null;
    var ringFill = ringWrap ? ringWrap.querySelector('.stat-ring-fill') : null;
    if (ringFill) {
      ringFill.style.strokeDasharray  = CIRC + 'px';
      ringFill.style.strokeDashoffset = CIRC + 'px';
    }

    el.classList.add('sa-counting');

    if (reducedMotion) {
      el.textContent = target;
      el.classList.remove('sa-counting');
      if (ringFill) { ringFill.style.strokeDashoffset = '0px'; }
      return;
    }

    function step(ts) {
      if (!startTs) { startTs = ts; }
      var progress = Math.min((ts - startTs) / duration, 1);
      var ease     = easeOutExpo(progress);
      el.textContent = Math.round(ease * target);
      if (ringFill) {
        ringFill.style.strokeDashoffset = (CIRC * (1 - ease)).toFixed(2) + 'px';
      }
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = target;
        el.classList.remove('sa-counting');
        if (ringFill) { ringFill.style.strokeDashoffset = '0px'; }
      }
    }

    requestAnimationFrame(step);
  }

  var counterObs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        runCounter(e.target);
        counterObs.unobserve(e.target);
      }
    });
  }, { threshold: 0.6 });

  document.querySelectorAll('[data-count]').forEach(function (el) {
    counterObs.observe(el);
  });

  /* ── 5. 3-D tilt on card hover ───────────────────────────── */
  if (!reducedMotion) {
    [
      '.interest-card',
      '.project-card',
      '.clinical-card',
    ].forEach(function (sel) {
      document.querySelectorAll(sel).forEach(function (card) {
      card.addEventListener('mouseenter', function () {
          card.style.transition = 'transform 0.096s ease, box-shadow 0.096s ease';
        });

        card.addEventListener('mousemove', function (e) {
          var rect = card.getBoundingClientRect();
          var dx   = (e.clientX - rect.left  - rect.width  / 2) / (rect.width  / 2);
          var dy   = (e.clientY - rect.top   - rect.height / 2) / (rect.height / 2);
          card.style.transform =
            'perspective(600px) ' +
            'rotateY(' + (dx * 7).toFixed(1) + 'deg) ' +
            'rotateX(' + (-dy * 5).toFixed(1) + 'deg) ' +
            'translateY(-4px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function () {
          /* Spring-feel elastic snap back via a bouncy cubic-bezier */
          card.style.transition = 'transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)';
          card.style.transform  = '';
          var onEnd = function () {
            card.style.transition = '';
            card.removeEventListener('transitionend', onEnd);
          };
          card.addEventListener('transitionend', onEnd);
        });
      });
    });
  }

  /* ── 6. Fast anchor smooth scroll (520 ms) ──────────────── */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) { return; }
    var hash = a.getAttribute('href');
    var id   = hash.slice(1);
    var el   = id ? document.getElementById(id) : document.documentElement;
    if (!el) { return; }
    e.preventDefault();
    var targetY = el === document.documentElement
      ? 0
      : el.getBoundingClientRect().top + window.scrollY;

    if (reducedMotion) {
      window.scrollTo(0, targetY);
      try { history.pushState(null, '', hash); } catch (_) {}
      return;
    }

    var startY    = window.scrollY;
    var diff      = targetY - startY;
    var DURATION  = 416;
    var startTs   = null;

    function easeInOutQuart(t) {
      return t < 0.5 ? 8 * t * t * t * t : 1 - Math.pow(-2 * t + 2, 4) / 2;
    }

    function step(ts) {
      if (!startTs) { startTs = ts; }
      var progress = Math.min((ts - startTs) / DURATION, 1);
      window.scrollTo(0, startY + diff * easeInOutQuart(progress));
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        try { history.pushState(null, '', hash); } catch (_) {}
      }
    }

    requestAnimationFrame(step);
  });

}());
