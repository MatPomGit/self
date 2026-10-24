/* ============================================================
   Anime.js Animations – additional page effects
   Uses anime.js v4 ES module
   https://animejs.com/documentation/getting-started/module-imports
   ============================================================ */

import { animate, stagger, spring } from './anime.esm.min.js';

(function () {
  'use strict';

  /* Item 10: Use the shared constant set by scroll-animations.js (regular script
     that runs before this deferred module). Fall back to a fresh media-query
     check if the global isn't available for any reason.                        */
  var reducedMotion = window.SA_REDUCED_MOTION !== undefined
    ? window.SA_REDUCED_MOTION
    : window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reducedMotion) { return; }

  /* ── 1. Navigation links stagger entrance ─────────────── */
  /* Set initial state before DOMContentLoaded fires         */
  document.querySelectorAll('.nav-links li').forEach(function (li) {
    li.style.opacity = '0';
  });

  document.addEventListener('DOMContentLoaded', function () {

    animate('.nav-links li', {
      opacity:    [0, 1],
      translateY: [-10, 0],
      scale:      [0.92, 1],
      delay:      stagger(48, { start: 280 }),
      duration:   384,
      ease:       'easeOutCubic',
    });

    /* ── 2. Hero tags individual stagger ─────────────────── */
    var tagsWrap = document.querySelector('.hero-tags');
    if (tagsWrap) {
      tagsWrap.classList.remove('fade-in');
      tagsWrap.style.opacity   = '1';
      tagsWrap.style.transform = 'none';

      var tagEls = tagsWrap.querySelectorAll('.tag');
      tagEls.forEach(function (t) {
        t.style.opacity   = '0';
        t.style.transform = 'translateY(12px) scale(0.88)';
      });

      animate(tagEls, {
        opacity:    [0, 1],
        translateY: [10, 0],
        scale:      [0.82, 1],
        delay:      stagger(55, { start: 650 }),
        duration:   440,
        ease:       spring({ stiffness: 110, damping: 13, mass: 0.9 }),
      });
    }

    /* ── 2b. Hero subtitle typewriter entrance ────────────── */
    /* Fires after the .hero-name shatter animation finishes.
       shatter: baseDelay=50, stagger=60, ~21 animated chars, duration=500ms
       → last char: 50 + 20×60 = 1250 ms starts, +500 ms = 1750 ms finishes  */
    var SHATTER_ANIMATION_END_MS = 1850; /* 50 + 20×60 + 500 + 100ms buffer  */
    var heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
      heroTitle.classList.remove('fade-in');
      heroTitle.style.opacity = '0'; /* pre-hide while shattering plays */

      var rawText = heroTitle.textContent;
      heroTitle.textContent = '';
      heroTitle.style.opacity = '1';

      var twChars = [];
      rawText.split('').forEach(function (ch) {
        var span = document.createElement('span');
        if (ch === ' ' || ch === '\u00a0') {
          span.className   = 'tw-space';
          span.textContent = '\u00a0';
        } else {
          span.className   = 'tw-char';
          span.textContent = ch;
          span.style.opacity = '0';
          twChars.push(span);
        }
        heroTitle.appendChild(span);
      });

      setTimeout(function () {
        animate(twChars, {
          opacity:  [0, 1],
          delay:    stagger(35),
          duration: 208,
          ease:     'easeOutQuad',
        });
      }, SHATTER_ANIMATION_END_MS);
    }

    /* ── 3. Hero CTA pulsing glow + click ripple ─────────── */
    var ctaBtn = document.querySelector('.hero-cta');
    if (ctaBtn) {
      ctaBtn.style.position = 'relative'; /* needed for ripple + magnetic */

      animate(ctaBtn, {
        boxShadow: '0 4px 28px rgba(6,182,212,0.55)',
        alternate: true,
        loop:      true,
        duration:  1440,
        ease:      'easeInOutSine',
      });

      /* Click ripple */
      ctaBtn.addEventListener('click', function (e) {
        var ripple = document.createElement('span');
        var rect   = ctaBtn.getBoundingClientRect();
        var size   = Math.max(rect.width, rect.height) * 2;
        ripple.className = 'aa-ripple';
        ripple.style.width  = size + 'px';
        ripple.style.height = size + 'px';
        ripple.style.left   = (e.clientX - rect.left  - size / 2) + 'px';
        ripple.style.top    = (e.clientY - rect.top   - size / 2) + 'px';
        ctaBtn.appendChild(ripple);

        animate(ripple, {
          scale:      [0, 1],
          opacity:    [0.5, 0],
          duration:   560,
          ease:       'easeOutQuart',
          onComplete: function () { ripple.remove(); },
        });
      });

      /* ── 7. Magnetic hover on CTA ───────────────────────── */
      var heroSection = document.getElementById('hero');
      if (heroSection) {
        var magX = 0, magY = 0;

        heroSection.addEventListener('mousemove', function (e) {
          var rect  = ctaBtn.getBoundingClientRect();
          var btnCx = rect.left + rect.width  / 2;
          var btnCy = rect.top  + rect.height / 2;
          var dx    = e.clientX - btnCx;
          var dy    = e.clientY - btnCy;
          var dist  = Math.sqrt(dx * dx + dy * dy);
          var maxDist = 130;
          if (dist < maxDist && dist > 0) {
            var factor = (1 - dist / maxDist) * 0.12;
            magX = Math.max(-8, Math.min(8, dx * factor));
            magY = Math.max(-8, Math.min(8, dy * factor));
            ctaBtn.style.transform = 'translate(' + magX.toFixed(1) + 'px,' + magY.toFixed(1) + 'px)';
          } else if (magX !== 0 || magY !== 0) {
            magX = 0; magY = 0;
            ctaBtn.style.transform = '';
          }
        });

        heroSection.addEventListener('mouseleave', function () {
          var fromX = magX, fromY = magY;
          magX = 0; magY = 0;
          /* Clear inline transform so anime.js takes over cleanly */
          ctaBtn.style.transform = '';
          animate(ctaBtn, {
            translateX: [fromX, 0],
            translateY: [fromY, 0],
            duration:   560,
            ease:       spring({ stiffness: 220, damping: 18, mass: 0.9 }),
          });
        });
      }
    }

    /* ── 8. Nav active-section underline indicator ──────── */
    var navList = document.getElementById('navLinks');
    if (navList) {
      var indicator = document.createElement('span');
      indicator.className = 'nav-indicator';
      indicator.setAttribute('aria-hidden', 'true');
      navList.appendChild(indicator);

      var sectionIds  = ['about', 'interests', 'research', 'projects', 'clinical'];
      var sectionLinks = {};
      sectionIds.forEach(function (id) {
        var a = navList.querySelector('a[href="#' + id + '"]');
        if (a) { sectionLinks[id] = a; }
      });

      var activeId = null;

      function moveIndicator(sectionId) {
        var link = sectionLinks[sectionId];
        if (!link) { indicator.style.opacity = '0'; return; }
        var listRect = navList.getBoundingClientRect();
        var linkRect = link.getBoundingClientRect();
        var targetX  = linkRect.left - listRect.left;
        var targetW  = linkRect.width;
        indicator.style.width   = targetW + 'px';
        indicator.style.opacity = '1';
        if (activeId === null) {
          /* First time – jump immediately */
          animate(indicator, { translateX: targetX, duration: 0 });
        } else {
          animate(indicator, {
            translateX: targetX,
            duration:   256,
            ease:       'easeOutQuart',
          });
        }
        activeId = sectionId;
      }

      var navSectionObs = new IntersectionObserver(function (entries) {
        /* Pick the most-visible intersecting entry */
        var best = null;
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            if (!best || e.intersectionRatio > best.intersectionRatio) { best = e; }
          }
        });
        if (best) { moveIndicator(best.target.id); }
      }, { threshold: [0.25, 0.5] });

      sectionIds.forEach(function (id) {
        var el = document.getElementById(id);
        if (el) { navSectionObs.observe(el); }
      });
    }

    /* ── 9. Scroll-progress glow is handled by CSS keyframe ─ */
    /* scroll-animations.js adds/removes .sa-bar-glow when pct > 85;
       the sa-bar-pulse @keyframe in scroll-animations.css drives the pulse. */

  }); /* end DOMContentLoaded */

  /* ── 4. Research list items stagger on scroll ─────────── */
  var RESEARCH_ITEM_OFFSET = 22; /* px – alternating left/right slide */
  var researchObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) { return; }
      var items = e.target.querySelectorAll('.research-list li');
      if (!items.length) { return; }

      /* Wait briefly so the parent column's CSS fade-in has fired */
      setTimeout(function () {
        /* Item 5: alternate slide directions – odd from left, even from right */
        items.forEach(function (li, idx) {
          var fromX = idx % 2 === 0 ? -RESEARCH_ITEM_OFFSET : RESEARCH_ITEM_OFFSET;
          animate(li, {
            opacity:    [0, 1],
            translateX: [fromX, 0],
            scale:      [0.95, 1],
            delay:      idx * 70 + 60,
            duration:   384,
            ease:       'easeOutCubic',
          });
        });
      }, 220);

      researchObserver.unobserve(e.target);
    });
  }, { threshold: 0.25 });

  document.querySelectorAll('.research-col').forEach(function (col) {
    /* Pre-hide list items – alternating initial offsets match animation */
    col.querySelectorAll('.research-list li').forEach(function (li, idx) {
      li.style.opacity   = '0';
      li.style.transform = idx % 2 === 0 ? 'translateX(-' + RESEARCH_ITEM_OFFSET + 'px)' : 'translateX(' + RESEARCH_ITEM_OFFSET + 'px)';
    });
    researchObserver.observe(col);
  });

  /* ── 4b. Section child stagger after parent becomes visible ─ */
  /* Observe .about-text; stagger its immediate content children.
     Children are naturally hidden inside the opacity:0 parent so
     we don't need to pre-hide them – just animate them in.      */
  var sectionStaggerObs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) { return; }
      var children = Array.from(e.target.children).filter(function (el) {
        return !el.matches('br');
      });
      if (!children.length) { return; }
      animate(children, {
        opacity:    [0, 1],
        translateY: [12, 0],
        scale:      [0.97, 1],
        delay:      stagger(80, { start: 120 }),
        duration:   416,
        ease:       'easeOutCubic',
      });
      sectionStaggerObs.unobserve(e.target);
    });
  }, { threshold: 0.15 });

  document.querySelectorAll('.about-text').forEach(function (el) {
    sectionStaggerObs.observe(el);
  });

  /* ── 5. Material card 3-D tilt on hover ───────────────── */
  document.querySelectorAll('.material-card').forEach(function (card) {
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

    /* Item 3: Spring-feel elastic snap back */
    card.addEventListener('mouseleave', function () {
      animate(card, {
        rotateX:    0,
        rotateY:    0,
        translateY: 0,
        scale:      1,
        duration:   560,
        ease:       spring({ stiffness: 180, damping: 16, mass: 0.9 }),
        onComplete: function () { card.style.transform = ''; },
      });
    });
  });

  /* ── 6. Floating SVG icon on card hover ──────────────── */
  [
    { sel: '.interest-card',  iconSel: '.int-icon'      },
    { sel: '.clinical-card',  iconSel: '.clinical-icon' },
    { sel: '.material-card',  iconSel: '.material-icon' },
  ].forEach(function (cfg) {
    document.querySelectorAll(cfg.sel).forEach(function (card) {
      var icon = card.querySelector(cfg.iconSel);
      if (!icon) { return; }

      var floatAnim = null;

      card.addEventListener('mouseenter', function () {
        if (floatAnim) { floatAnim.pause(); }
        floatAnim = animate(icon, {
          translateY: -6,
          alternate:  true,
          loop:       true,
          duration:   800,
          ease:       'easeInOutSine',
        });
      });

      card.addEventListener('mouseleave', function () {
        if (floatAnim) { floatAnim.pause(); floatAnim = null; }
        animate(icon, {
          translateY: 0,
          duration:   280,
          ease:       spring({ stiffness: 200, damping: 16, mass: 0.8 }),
        });
      });
    });
  });

}());
