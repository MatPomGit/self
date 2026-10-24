/* ============================================================
   2D Grid Navigation – inter-page navigation logic
   ============================================================ */

(function () {
  'use strict';

  /*
   *  Grid layout:
   *
   *   [ publications.html ] ← [ index.html ] → [ materials.html ]
   *                                    ↓
   *                            [ projects.html ]
   *
   *  Each page carries  data-grid-pos="center|left|right|bottom"
   *  on its <body> element.
   */

  var DESTINATIONS = {
    center: { left: 'publications.html', right: 'materials.html', down: 'projects.html' },
    left:   { right: 'index.html' },
    right:  { left:  'index.html' },
    bottom: { up:    'index.html' },
  };

  function getPos() {
    return document.body.getAttribute('data-grid-pos') || 'center';
  }

  /* ── Navigate to an adjacent page ────────────────────────── */
  function navigate(dir, dests) {
    var target = dests[dir];
    if (!target) { return; }

    try {
      sessionStorage.setItem('gn-from-pos', getPos());
      sessionStorage.setItem('gn-from-dir', dir);
    } catch (_) {}

    var tx = { left: '48px', right: '-48px', up: '0', down: '0' };
    var ty = { left: '0', right: '0', up: '48px', down: '-48px' };
    document.body.style.transition = 'opacity 0.144s cubic-bezier(0.4, 0, 1, 1), transform 0.144s cubic-bezier(0.4, 0, 1, 1)';
    document.body.style.opacity    = '0';
    document.body.style.transform  =
      'translate(' + (tx[dir] || '0') + ', ' + (ty[dir] || '0') + ')';

    setTimeout(function () { window.location.href = target; }, 190);
  }

  /* ── Build mini-map ──────────────────────────────────────── */
  function buildMinimap(pos, dests) {
    /*  Row 0:  [left] [center] [right]
        Row 1:  [    ] [bottom] [     ]   */
    var cells = [
      { key: 'left',   row: 0, col: 0 },
      { key: 'center', row: 0, col: 1 },
      { key: 'right',  row: 0, col: 2 },
      { key: 'empty1', row: 1, col: 0 },
      { key: 'bottom', row: 1, col: 1 },
      { key: 'empty2', row: 1, col: 2 },
    ];

    var map = document.createElement('div');
    map.className = 'grid-minimap';
    map.setAttribute('aria-hidden', 'true');
    map.setAttribute('title', 'Nawigacja 2D');

    cells.forEach(function (c) {
      var cell = document.createElement('div');
      cell.className = 'grid-minimap-cell';

      if (c.key === pos) {
        cell.classList.add('gm-active');
      } else if (c.key.startsWith('empty')) {
        cell.classList.add('gm-inactive');
      } else {
        /* Available if any dest maps to this cell's position */
        var isAvailable = Object.values(dests).some(function (href) {
          return (
            (c.key === 'left'   && href.startsWith('publications')) ||
            (c.key === 'right'  && href.startsWith('materials'))    ||
            (c.key === 'bottom' && href.startsWith('projects'))     ||
            (c.key === 'center' && href.startsWith('index'))
          );
        });
        if (isAvailable) {
          cell.classList.add('gm-available');
        } else {
          cell.classList.add('gm-inactive');
        }
      }

      map.appendChild(cell);
    });

    return map;
  }

  /* ── Slide-in on page load ───────────────────────────────── */
  function applySlidein() {
    var fromPos, fromDir;
    try {
      fromPos = sessionStorage.getItem('gn-from-pos');
      fromDir = sessionStorage.getItem('gn-from-dir');
      sessionStorage.removeItem('gn-from-pos');
      sessionStorage.removeItem('gn-from-dir');
    } catch (_) {}

    var startTransform = null;
    if (fromDir) {
      var tx = { left: '-80px', right: '80px', up: '0', down: '0' };
      var ty = { left: '0', right: '0', up: '-80px', down: '80px' };
      startTransform =
        'translate(' + (tx[fromDir] || '0') + ', ' + (ty[fromDir] || '0') + ')';
    }

    document.body.style.opacity   = '0';
    if (startTransform) { document.body.style.transform = startTransform; }

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        document.body.style.transition = 'opacity 0.224s cubic-bezier(0.0, 0, 0.2, 1), transform 0.224s cubic-bezier(0.0, 0, 0.2, 1)';
        document.body.style.opacity    = '1';
        document.body.style.transform  = 'none';
      });
    });
  }

  /* ── Mouse-edge navigation ───────────────────────────────── */
  function addMouseEdge(dests) {
    var EDGE_PX    = 24;  /* larger edge area so navigation is easier to trigger */
    var EDGE_DELAY = 550; /* ms to hold at edge before navigating       */
    var edgeTimer  = null;

    document.addEventListener('mousemove', function (e) {
      clearTimeout(edgeTimer);

      var w = window.innerWidth;
      var h = window.innerHeight;
      var x = e.clientX;
      var y = e.clientY;

      var atDir = null;

      if      (x <= EDGE_PX       && dests.left)  { atDir = 'left';  }
      else if (x >= w - EDGE_PX   && dests.right) { atDir = 'right'; }
      else if (y >= h - EDGE_PX   && dests.down)  { atDir = 'down';  }
      else if (y <= EDGE_PX       && dests.up)    { atDir = 'up';    }

      if (atDir) {
        edgeTimer = setTimeout(function () {
          navigate(atDir, dests);
        }, EDGE_DELAY);
      }
    });

    document.addEventListener('mouseleave', function () {
      clearTimeout(edgeTimer);
    });
  }

  /* ── Keyboard arrow navigation ──────────────────────────── */
  function addKeyboard(dests) {
    var KEY_MAP = {
      ArrowLeft:  'left',
      ArrowRight: 'right',
      ArrowDown:  'down',
      ArrowUp:    'up',
    };

    document.addEventListener('keydown', function (e) {
      /* Ignore when focus is inside a text input */
      var tag = document.activeElement && document.activeElement.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') { return; }

      var dir = KEY_MAP[e.key];
      if (!dir || !dests[dir]) { return; }

      e.preventDefault();
      navigate(dir, dests);
    });
  }

  /* ── Touch-swipe navigation ──────────────────────────────── */
  function addSwipe(dests) {
    var MIN_DIST = 60; /* minimum swipe distance in px */
    var startX = null;
    var startY = null;

    document.addEventListener('touchstart', function (e) {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
    }, { passive: true });

    document.addEventListener('touchend', function (e) {
      if (startX === null || startY === null) { return; }

      var dx  = e.changedTouches[0].clientX - startX;
      var dy  = e.changedTouches[0].clientY - startY;
      var adx = Math.abs(dx);
      var ady = Math.abs(dy);

      startX = startY = null;

      if (Math.max(adx, ady) < MIN_DIST) { return; }

      /* Swipe left  → right page; swipe right → left page
         Swipe up    → down page;  swipe down  → up page   */
      var dir;
      if (adx > ady) {
        dir = dx < 0 ? 'right' : 'left';
      } else {
        dir = dy < 0 ? 'down' : 'up';
      }

      if (dests[dir]) {
        navigate(dir, dests);
      }
    }, { passive: true });
  }

  /* ── Init ────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    var pos   = getPos();
    var dests = DESTINATIONS[pos];
    if (!dests) { return; }

    /* Apply slide-in */
    applySlidein();

    /* Add mini-map */
    document.body.appendChild(buildMinimap(pos, dests));

    /* Mouse-edge, keyboard, and touch-swipe support */
    addMouseEdge(dests);
    addKeyboard(dests);
    addSwipe(dests);
  });

}());
