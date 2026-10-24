/* ============================================================
   Theme Switcher – initialisation script
   Reads / writes  localStorage key  "theme"
   Sets  data-theme  attribute on  <html>
   ============================================================ */
(function () {
  'use strict';

  const STORAGE_KEY = 'theme';
  const DEFAULT     = 'cyber';

  const THEMES = [
    { id: 'cyber',    label: 'Cyber',    swatch: 'cyber'    },
    { id: 'forest',   label: 'Forest',   swatch: 'forest'   },
    { id: 'solar',    label: 'Solar',    swatch: 'solar'    },
    { id: 'amethyst', label: 'Amethyst', swatch: 'amethyst' },
  ];

  /* ── Apply theme ──────────────────────────────────────────── */
  function applyTheme(id) {
    const safe = THEMES.some(t => t.id === id) ? id : DEFAULT;
    document.documentElement.setAttribute('data-theme', safe);
    try { localStorage.setItem(STORAGE_KEY, safe); } catch (_) { /* ignore */ }

    /* Notify canvas and other listeners */
    document.dispatchEvent(new CustomEvent('themechange', { detail: { theme: safe } }));

    /* Aktualizacja stanu wizualnego i a11y opcji motywu. */
    document.querySelectorAll('.theme-option').forEach(btn => {
      const isActive = btn.dataset.themeId === safe;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });

    /* Keep the toggle button aria-label in sync */
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
      const name = THEMES.find(t => t.id === safe)?.label ?? safe;
      toggle.setAttribute('aria-label', `Motyw: ${name} – kliknij aby zmienić`);
    }
  }

  /* ── Restore saved theme immediately (before paint) ─────── */
  let saved = DEFAULT;
  try { saved = localStorage.getItem(STORAGE_KEY) || DEFAULT; } catch (_) { /* ignore */ }
  applyTheme(saved);

  /* ── Build picker UI after DOM is ready ──────────────────── */
  document.addEventListener('DOMContentLoaded', function () {

    /* Locate the nav-level wrapper we inserted in HTML */
    const picker = document.querySelector('.theme-picker');
    if (!picker) return;

    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;

    /* Build panel */
    const panel = document.createElement('div');
    panel.className = 'theme-panel';
    panel.id = 'themePanel';
    panel.setAttribute('role', 'listbox');
    panel.setAttribute('aria-label', 'Wybierz motyw');

    THEMES.forEach(t => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'theme-option';
      btn.dataset.themeId = t.id;
      btn.setAttribute('role', 'option');
      btn.setAttribute('aria-selected', t.id === saved ? 'true' : 'false');

      const swatch = document.createElement('span');
      swatch.className = `theme-swatch theme-swatch--${t.swatch}`;
      swatch.setAttribute('aria-hidden', 'true');

      btn.appendChild(swatch);
      btn.appendChild(document.createTextNode(t.label));

      btn.addEventListener('click', function () {
        applyTheme(t.id);
        closePanel();
      });

      panel.appendChild(btn);
    });

    picker.appendChild(panel);

    /* Mark currently-active option */
    applyTheme(saved);

    /* ── Toggle open / close ──────────────────────────────── */
    function openPanel() {
      panel.classList.add('open');
      toggle.setAttribute('aria-expanded', 'true');
    }

    function closePanel() {
      panel.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }

    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      panel.classList.contains('open') ? closePanel() : openPanel();
    });

    /* Close when clicking outside */
    document.addEventListener('click', function (e) {
      if (!picker.contains(e.target)) closePanel();
    });

    /* Close on Escape */
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closePanel();
    });
  });
})();
