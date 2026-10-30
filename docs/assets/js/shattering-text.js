/* ============================================================
   Shattering Text Entrance Animation – initialiser
   Inspired by: https://codepen.io/ARS/pen/pjypwd

   Walks the child nodes of every matched element, wraps each
   printable character in an animated <span class="char"> with
   randomised CSS custom properties so every letter flies in
   from a unique scattered position.
   ============================================================ */

(function () {
  'use strict';

  /**
   * Splits all text nodes inside `container` into per-character
   * <span class="char"> elements and applies random shatter
   * CSS custom properties to each one.
   *
   * Preserves existing child elements (e.g. .gradient-text spans
   * and <br> tags) so the visual structure stays intact.
   *
   * @param {Element} container  - Root element to shatter
   * @param {object}  [opts]     - Optional configuration
   * @param {number}  [opts.baseDelay=50]   ms before first char
   * @param {number}  [opts.stagger=60]     ms between characters
   * @param {number}  [opts.txRange=130]    max |horizontal| offset in px
   * @param {number}  [opts.tyMin=-170]     min vertical offset in px
   * @param {number}  [opts.tyMax=-20]      max vertical offset in px
   * @param {number}  [opts.rotRange=80]    max |rotation| in deg
   * @param {number}  [opts.scaleMin=0.05]  min starting scale
   * @param {number}  [opts.scaleMax=0.25]  max starting scale
   */
  function shatterText(container, opts) {
    var cfg = Object.assign({
      baseDelay : 50,
      stagger   : 60,
      txRange   : 130,
      tyMin     : -170,
      tyMax     : -20,
      rotRange  : 80,
      scaleMin  : 0.05,
      scaleMax  : 0.25,
    }, opts);

    var charIndex = 0;

    /* Recursively processes DOM nodes */
    function processNode(node) {
      if (node.nodeType === Node.TEXT_NODE) {
        var text = node.textContent;
        var frag = document.createDocumentFragment();

        for (var i = 0; i < text.length; i++) {
          var ch   = text[i];
          var span = document.createElement('span');

          if (ch === ' ' || ch === '\u00a0') {
            /* Word gap – no animation, just spacing */
            span.className   = 'char-space';
            span.textContent = '\u00a0';
          } else {
            span.className   = 'char';
            span.textContent = ch;

            /* Random starting position */
            var tx = (Math.random() - 0.5) * cfg.txRange * 2;
            var ty = cfg.tyMin + Math.random() * (cfg.tyMax - cfg.tyMin);
            var r  = (Math.random() - 0.5) * cfg.rotRange * 2;
            var s  = cfg.scaleMin + Math.random() * (cfg.scaleMax - cfg.scaleMin);

            span.style.setProperty('--shatter-tx', tx.toFixed(1) + 'px');
            span.style.setProperty('--shatter-ty', ty.toFixed(1) + 'px');
            span.style.setProperty('--shatter-r',  r.toFixed(1)  + 'deg');
            span.style.setProperty('--shatter-s',  s.toFixed(3));
            span.style.animationDelay = (cfg.baseDelay + charIndex * cfg.stagger) + 'ms';

            charIndex++;
          }

          frag.appendChild(span);
        }

        node.parentNode.replaceChild(frag, node);

      } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName !== 'BR') {
        /* Descend into child elements (e.g. .gradient-text span).
           Array.from creates a static snapshot so DOM mutations
           during iteration (text-node replacements) are safe. */
        Array.from(node.childNodes).forEach(processNode);
      }
      /* BR nodes are left untouched – they keep the line break */
    }

    /* Snapshot childNodes (static array) so text-node replacements
       during iteration do not affect the traversal. */
    Array.from(container.childNodes).forEach(processNode);

    container.classList.add('shatter-text');
  }

  /* ── Auto-initialise on the hero name ──────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    var nameEl = document.querySelector('.hero-name');
    if (!nameEl) { return; }

    /* Remove the generic fade-in so the two animations don't clash */
    nameEl.classList.remove('fade-in');
    nameEl.style.removeProperty('transition-delay');

    shatterText(nameEl, { baseDelay: 50, stagger: 60 });
  });

}());
