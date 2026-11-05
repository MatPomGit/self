// Test obliczania wysokości i szerokości kart bez zależności npm.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const html = fs.readFileSync('materials/index.html', 'utf8');
const begin = html.indexOf('  function initAdaptiveMaterialsGrid() {');
const end = html.indexOf('  requestMaterialsLayout = initAdaptiveMaterialsGrid();', begin);
assert.ok(begin > 0 && end > begin, 'funkcja responsywnej siatki musi istnieć');
const layoutScript = html.slice(begin, end);

function card(count, chars, height) {
  const classes = new Set();
  const properties = {};
  const rows = Array.from({length: count}, () => ({
    textContent: 'x'.repeat(chars), hidden: false
  }));
  return {
    hidden: false, rows, height, classes, properties,
    classList: {
      toggle(name, enabled) {
        if (enabled) classes.add(name);
        else classes.delete(name);
      }
    },
    querySelectorAll(selector) {
      assert.equal(selector, '.materials-list li:not([hidden])');
      return rows.filter(row => !row.hidden);
    },
    getBoundingClientRect() { return {height: this.height}; },
    style: {
      getPropertyValue(name) { return properties[name] || ''; },
      setProperty(name, value) { properties[name] = value; }
    }
  };
}

function runLayout(available) {
  const short = card(5, 9, 96);
  const long = card(20, 18, 240);
  const cards = [short, long];
  const frames = [];
  const observers = [];
  const classes = new Set();
  const grid = {
    classList: {add: cls => classes.add(cls)},
    querySelectorAll: selector => {
      assert.equal(selector, '.materials-group');
      return cards;
    }
  };
  const context = {
    document: {
      querySelector: selector => {
        assert.equal(selector, '.materials-grid');
        return grid;
      }
    },
    window: {
      requestAnimationFrame: callback => frames.push(callback),
      getComputedStyle: () => ({gridAutoRows: '8px', rowGap: '8px'}),
      addEventListener: (name, callback) => {
        assert.equal(name, 'load');
        assert.equal(typeof callback, 'function');
      }
    },
    ResizeObserver: available ? class {
      constructor(callback) { this.callback = callback; observers.push(this); }
      observe(node) { assert.ok(node === grid || cards.includes(node)); }
    } : undefined
  };
  vm.runInNewContext(layoutScript + '\nresult = initAdaptiveMaterialsGrid();', context);
  return {short, long, frames, observers, classes, result: context.result};
}

// Dynamiczny tryb musi mierzyć naturalną wysokość i promować długie karty.
const active = runLayout(true);
assert.equal(typeof active.result, 'function');
assert.ok(active.classes.has('materials-grid--masonry'));
assert.equal(active.observers.length, 1);
assert.equal(active.frames.length, 1);
active.frames.shift()();
assert.equal(active.short.classes.has('materials-group--adaptive-wide'), false);
assert.equal(active.long.classes.has('materials-group--adaptive-wide'), true);
assert.equal(active.short.properties['--material-row-span'], '7');
assert.equal(active.long.properties['--material-row-span'], '16');

// Zmiana widoczności materiałów wymusza ponowne obliczenie.
active.long.rows.slice(2).forEach(row => { row.hidden = true; });
active.long.height = 80;
active.result();
active.frames.shift()();
assert.equal(active.long.classes.has('materials-group--adaptive-wide'), false);
assert.equal(active.long.properties['--material-row-span'], '6');

// Obserwator umożliwia reflow po zmianie rozmiaru okna.
active.short.height = 160;
active.observers[0].callback();
active.frames.shift()();
assert.equal(active.short.properties['--material-row-span'], '11');

// Brak ResizeObserver: bezpieczny powrót do natywnych kolumn CSS.
const fallback = runLayout(false);
assert.equal(fallback.result, null);
assert.equal(fallback.classes.has('materials-grid--masonry'), false);
assert.equal(fallback.frames.length, 0);
console.log('[DONE] MATERIALS_ADAPTIVE_LAYOUT_PASS');
