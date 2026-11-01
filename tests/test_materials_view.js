// Test zachowania przełącznika na minimalnym modelu DOM, bez zależności npm.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('materials/index.html', 'utf8');
const scripts = [...html.matchAll(/<script>([\\s\\S]*?)<\\/script>/g)];
assert.equal(scripts.length, 2);
const script = scripts[1][1];

class Node {
  constructor(items = [], subgroups = []) {
    this.items = items;
    this.subgroups = subgroups;
    this.hidden = false;
  }
  querySelectorAll(selector) {
    assert.equal(selector, '.materials-subgroup');
    return this.subgroups;
  }
  querySelector(selector) {
    assert.equal(selector, '.materials-list li:not([hidden])');
    return this.items.find(item => !item.hidden) ||
      this.subgroups.flatMap(group => group.items).find(item => !item.hidden) || null;
  }
}
function link(path) {
  const item = { hidden: false };
  return { item, getAttribute: () => path, closest: selector => {
    assert.equal(selector, 'li');
    return item;
  }};
}
function button() {
  return {
    attrs: {}, events: {}, textContent: '', title: '',
    setAttribute(name, value) { this.attrs[name] = value; },
    addEventListener(event, handler) { this.events[event] = handler; }
  };
}
const pdfOld = link('course/lecture_v1.0.0.pdf');
const pdfNew = link('course/lecture_v1.2.0.pdf');
const pdfSimple = link('course/lab_01.PDF');
const htmlFile = link('course/lab_01.html');
const pptxFile = link('course/lecture.pptx');
const externalPage = link('subject/');
const pdfGroup = new Node([pdfOld.item, pdfNew.item, pdfSimple.item, htmlFile.item, pptxFile.item]);
const pageGroup = new Node([externalPage.item]);
const subgroupPdf = new Node([pdfOld.item, pdfNew.item, pdfSimple.item]);
const subgroupOther = new Node([htmlFile.item, pptxFile.item]);
pdfGroup.subgroups = [subgroupPdf, subgroupOther];
const viewToggle = button();
const themeToggle = button();
const root = {dataset:{theme:'light'},classList:{add(){},remove(){}}};
const groups = [pdfGroup, pageGroup];
const links = [pdfOld, pdfNew, pdfSimple, htmlFile, pptxFile, externalPage];
let now = 0;
vm.runInNewContext(script, {
  document: {
    documentElement: root,
    getElementById: id => id === 'materials-view-toggle' ? viewToggle : themeToggle,
    querySelectorAll: selector => {
      if (selector === '.materials-list a[href]') return links;
      if (selector === '.materials-group') return groups;
      throw Error(selector);
    }
  },
  window: {matchMedia: () => ({addEventListener(){}})},
  Date: {now: () => now},
  localStorage: {getItem: () => null},
  setTimeout: () => 1,
  clearTimeout() {}
});
function clickAt(time) { now = time; viewToggle.events.click(); }
assert.equal(root.dataset.materialsView, 'pdf');
assert.equal(viewToggle.attrs['aria-pressed'], 'false');
assert.equal(viewToggle.textContent, 'PDF');
assert.equal(pdfOld.item.hidden, true, 'starszy PDF ukryty');
assert.equal(pdfNew.item.hidden, false, 'najnowszy PDF widoczny');
assert.equal(pdfSimple.item.hidden, false, 'rozszerzenie wielkimi literami');
assert.equal(htmlFile.item.hidden, true);
assert.equal(pptxFile.item.hidden, true);
assert.equal(subgroupOther.hidden, true);
assert.equal(pageGroup.hidden, true);

clickAt(100); clickAt(300);
assert.equal(root.dataset.materialsView, 'pdf', 'dwa kliknięcia nie wystarczą');
clickAt(500);
assert.equal(root.dataset.materialsView, 'all');
assert.equal(viewToggle.attrs['aria-pressed'], 'true');
assert.equal(viewToggle.textContent, 'Wszystkie');
assert.equal(pdfOld.item.hidden, false);
assert.equal(htmlFile.item.hidden, false);
assert.equal(subgroupOther.hidden, false);
assert.equal(pageGroup.hidden, false);

clickAt(800); clickAt(2801);
assert.equal(root.dataset.materialsView, 'all', 'odstęp ponad 1,8 s resetuje licznik');
clickAt(2900);
assert.equal(root.dataset.materialsView, 'all');
clickAt(3100);
assert.equal(root.dataset.materialsView, 'pdf');
assert.equal(viewToggle.attrs['aria-pressed'], 'false');
assert.equal(pageGroup.hidden, true);
assert.match(html, /@media\\(max-width:620px\\).*materials-view-toggle\\{position:static/);
assert.match(html, /\\[hidden\\]\\{display:none!important\\}/);
console.log('[DONE] MATERIALS_VIEW_PASS');
