// Behavioural regression tests for the bilingual, playful GitHub Pages 404 page.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('404.html', 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);

assert.equal(scripts.length, 2, 'Redirect/theme init and UI script must be present');
assert.match(html, /<meta name="robots" content="noindex,follow">/);
assert.match(html, /<main id="main">/);
assert.match(html, /href="\/files\/"/);
assert.match(html, /href="\/"/);
assert.match(html, /data-lang-content="pl"/);
assert.match(html, /data-lang-content="en"/);
assert.match(html, /:root\[data-theme="dark"\]/);
assert.match(html, /prefers-reduced-motion:reduce/);
assert.match(html, /aria-live="polite"/);
assert.doesNotMatch(html, /<script src=|<link rel="stylesheet"/);

function element(attributes = {}) {
  const callbacks = {};
  return {
    attributes,
    callbacks,
    title: '',
    textContent: '',
    setAttribute(key, value) { this.attributes[key] = String(value); },
    removeAttribute(key) { delete this.attributes[key]; },
    addEventListener(key, callback) { callbacks[key] = callback; },
    getAttribute(key) { return this.attributes[key] ?? null; },
  };
}
function visit(path, search = '', hash = '', saved = null, systemDark = false) {
  let redirect = null;
  let storage = saved;
  const root = {lang: 'pl', dataset: {}};
  const meta = {content: ''};
  const toggle = element();
  const next = element();
  const hypothesis = element();
  const hypothesisEn = element();
  const pl = element({}); pl.hreflang = 'pl';
  const en = element({}); en.hreflang = 'en';
  const map = {
    'theme-toggle': toggle,
    'new-hypothesis': next,
    'hypothesis': hypothesis,
    'hypothesis-en': hypothesisEn
  };
  const media = {
    matches: systemDark,
    callbacks: {},
    addEventListener(event, cb) { this.callbacks[event] = cb; }
  };
  const window = {
    location: {pathname: path, search, hash, replace(url) { redirect = url; }},
    matchMedia: () => media
  };
  const document = {
    documentElement: root,
    title: '404',
    querySelector(selector) {
      assert.equal(selector, 'meta[name="description"]');
      return meta;
    },
    querySelectorAll(selector) {
      assert.equal(selector, '.language-switch a');
      return [pl, en];
    },
    getElementById(id) {
      assert.ok(id in map, 'Unexpected element ' + id);
      return map[id];
    }
  };
  const localStorage = {
    getItem(key) { assert.equal(key, 'self-theme'); return storage; },
    setItem(key, value) { assert.equal(key, 'self-theme'); storage = value; }
  };
  for (const script of scripts) {
    vm.runInNewContext(script, {window, document, localStorage, URLSearchParams});
  }
  return {redirect, storage: () => storage, root, toggle, next, hypothesis, hypothesisEn,
    pl, en, media, meta, document};
}

const fallback = visit('/missing/page', '', '', null, false);
assert.equal(fallback.redirect, null, 'Normal 404s should render instead of redirecting');
assert.equal(fallback.root.lang, 'pl');
assert.equal(fallback.root.dataset.theme, 'light');
assert.equal(fallback.toggle.attributes['aria-pressed'], 'false');
assert.equal(fallback.pl.attributes['aria-current'], 'page');
assert.equal(fallback.en.attributes['aria-current'], undefined);
assert.match(fallback.hypothesis.textContent, /^$/);
fallback.next.callbacks.click();
assert.match(fallback.hypothesis.textContent, /USB-C/);
fallback.next.callbacks.click();
assert.match(fallback.hypothesis.textContent, /superpozycję/);
fallback.toggle.callbacks.click();
assert.equal(fallback.root.dataset.theme, 'dark');
assert.equal(fallback.storage(), 'dark');
assert.equal(fallback.toggle.attributes['aria-pressed'], 'true');

const english = visit('/some-unknown', '?lang=en', '', null, true);
assert.equal(english.root.lang, 'en');
assert.equal(english.root.dataset.lang, 'en');
assert.equal(english.root.dataset.theme, 'dark');
assert.equal(english.en.attributes['aria-current'], 'page');
assert.equal(english.pl.attributes['aria-current'], undefined);
assert.match(english.meta.content, /academic website/);
assert.match(english.document.title, /Beyond the field of view/);
english.next.callbacks.click();
assert.match(english.hypothesisEn.textContent, /USB-C/);
english.toggle.callbacks.click();
assert.equal(english.toggle.attributes['aria-label'], 'Switch to dark mode');
assert.equal(english.storage(), 'light');

const legacy = visit('/materials/course/lecture.pdf', '?lang=en', '#page=5');
assert.equal(legacy.redirect, '/files/course/lecture.pdf?lang=en#page=5',
  'Legacy PDFs must still redirect without losing the query or fragment');
assert.equal(visit('/materials/', '', '').redirect, null,
  'The existing /materials/ index handles the directory');
assert.equal(visit('/files/course/unknown.pdf').redirect, null);
assert.equal(visit('/something-materials/page').redirect, null);

console.log('[DONE] PLAYFUL_404_PAGE_PASS');
