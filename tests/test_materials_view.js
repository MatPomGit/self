// Test zachowania przełącznika na minimalnym modelu DOM, bez zależności npm.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('materials/index.html', 'utf8');
assert.equal(html.split('<script>').length - 1, 2);
const script = html.split('<script>')[2].split('</script>')[0];

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
assert.equal(viewToggle.textContent, '');
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
assert.equal(viewToggle.textContent, '');
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
assert.ok(html.includes('.materials-view-toggle{position:static;transform:none;'));
assert.ok(html.includes('[hidden]{display:none!important}'));
assert.ok(html.includes('min-width:80px;height:34px;padding:0;border:0;background:transparent;cursor:pointer'));
assert.ok(html.includes('aria-pressed="false" title="Kliknij trzy razy, aby wyświetlić wszystkie pliki"></button>'));
assert.ok(!html.includes('.materials-view-toggle:hover{background:var(--hover)}'));
assert.match(viewToggle.attrs['aria-label'], /Kliknij trzy razy/);
console.log('[DONE] MATERIALS_VIEW_PASS');


// Sprawdź DOM po scaleniu identycznie nazwanych dokumentów w różnych podgrupach.
// Minimalna implementacja potrzebnych operacji DOM, bez zewnętrznych pakietów.
class Element {
  constructor(tag, className = '') {
    this.tagName = tag.toUpperCase();
    this.className = className;
    this.parentNode = null;
    this.children = [];
    this.attributes = {};
    this.dataset = {};
    this.textContent = '';
    this.hidden = false;
  }
  get classList() {
    return {
      contains: name => this.className.split(/\s+/).includes(name),
      add: name => {
        if (!this.className.split(/\s+/).includes(name)) {
          this.className = [this.className, name].filter(Boolean).join(' ');
        }
      }
    };
  }
  getAttribute(name) { return this.attributes[name] ?? null; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  removeAttribute(name) { delete this.attributes[name]; }
  appendChild(child) {
    if (child.parentNode) {
      const siblings = child.parentNode.children;
      siblings.splice(siblings.indexOf(child), 1);
    }
    this.children.push(child);
    child.parentNode = this;
    return child;
  }
  remove() {
    if (!this.parentNode) return;
    const siblings = this.parentNode.children;
    siblings.splice(siblings.indexOf(this), 1);
    this.parentNode = null;
  }
  descendants() {
    return this.children.flatMap(child => [child, ...child.descendants()]);
  }
  querySelectorAll(selector) {
    const insideList = item => {
      let current = item.parentNode;
      while (current) {
        if (current.classList.contains('materials-list')) return true;
        current = current.parentNode;
      }
      return false;
    };
    return this.descendants().filter(item => {
      switch (selector) {
        case '.materials-list a[href]':
          return item.tagName === 'A' && !!item.getAttribute('href') && insideList(item);
        case '.materials-list li':
          return item.tagName === 'LI' && insideList(item);
        case '.materials-list li:not([hidden])':
          return item.tagName === 'LI' && !item.hidden && insideList(item);
        case 'a[href]':
          return item.tagName === 'A' && !!item.getAttribute('href');
        case '.materials-list': return item.classList.contains('materials-list');
        case '.materials-group': return item.classList.contains('materials-group');
        case '.materials-subgroup': return item.classList.contains('materials-subgroup');
        case '.materials-columns': return item.classList.contains('materials-columns');
        case '.material-formats': return item.classList.contains('material-formats');
        default: throw Error('Nieobsługiwany selektor: ' + selector);
      }
    });
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}
function attach(parent, tag, className = '') {
  return parent.appendChild(new Element(tag, className));
}
function row(list, filename, caption, kind = '') {
  const li = attach(list, 'li');
  const a = attach(li, 'a', kind ? 'material-link--' + kind : '');
  a.setAttribute('href', filename);
  if (!/\.html?$/i.test(filename)) a.setAttribute('download', '');
  a.textContent = caption;
  return {li, a};
}
const tree = new Element('div');
const course = attach(tree, 'section', 'materials-group');
const columns = attach(course, 'div', 'materials-columns');
function subgroup() {
  const block = attach(columns, 'div', 'materials-subgroup');
  return {block, list: attach(block, 'ul', 'materials-list')};
}
const labs = subgroup(); // Laboratoria przed wykładami w kodzie źródłowym.
const pdfLab = row(labs.list, 'course/lab_02.pdf', 'lab_02 · PDF', 'lab');
const sources = subgroup();
const editor = row(sources.list, 'course/lab_02.docx', 'lab_02 · DOCX', 'lab');
const orphan = row(sources.list, 'course/standalone.tex', 'standalone · TEX');
const lectures = subgroup();
const pdfLecture = row(lectures.list, 'course/w01.pdf', 'w_01 · PDF', 'lecture');
const pptxLecture = row(sources.list, 'course/w01.pptx', 'w_01 · PPTX', 'lecture');
const htmlLecture = row(sources.list, 'course/w01.html', 'w_01 · HTML', 'lecture');
const orphanHtml = row(sources.list, 'course/standalone.html', 'standalone · HTML', 'lab');
pdfLecture.a.setAttribute('data-material-title', 'Wprowadzenie do badań XR');
const pairedOnly = subgroup();
const pairedSource = row(pairedOnly.list, 'course/lab_02.qmd', 'lab_02 · QMD', 'lab');

const fullToggle = button();
const fullTheme = button();
const displayRoot = {dataset:{theme:'light'},classList:{add(){},remove(){}}};
let tick = 0;
vm.runInNewContext(script, {
  document: {
    documentElement: displayRoot,
    createElement: tag => new Element(tag),
    getElementById: id => id === 'materials-view-toggle' ? fullToggle : fullTheme,
    querySelectorAll: selector => tree.querySelectorAll(selector)
  },
  window: {matchMedia: () => ({addEventListener(){}})},
  Date: {now: () => tick},
  localStorage: {getItem: () => null},
  setTimeout: () => 1,
  clearTimeout() {}
});
const labFormats = pdfLab.li.querySelector('.material-formats');
const lectureFormats = pdfLecture.li.querySelector('.material-formats');
assert.equal(pdfLab.a.textContent, 'lab_02', 'tryb podstawowy bez rozszerzenia');
assert.equal(pdfLab.a.getAttribute('download'), null, 'nazwa pliku otwiera PDF zamiast pobierać');
assert.match(pdfLab.a.getAttribute('aria-label'), /^Otwórz PDF:/);
assert.equal(orphanHtml.a.getAttribute('download'), null);
assert.equal(labFormats.children.length, 3);
assert.deepEqual(labFormats.children.map(x => x.textContent), ['PDF', 'DOCX', 'QMD']);
assert.deepEqual(labFormats.children.map(x => x.getAttribute('href')), [
  'course/lab_02.pdf', 'course/lab_02.docx', 'course/lab_02.qmd'
]);
assert.equal(labFormats.children[1].getAttribute('download'), '');
assert.ok(labFormats.children[1].classList.contains('material-format--editable'));
assert.equal(lectureFormats.children[1], pptxLecture.a);
assert.deepEqual(lectureFormats.children.map(x => x.textContent), ['PDF', 'PPTX', 'HTML']);
assert.equal(lectureFormats.children[2], htmlLecture.a, 'HTML jako osobny wariant tego samego dokumentu');
assert.equal(htmlLecture.a.getAttribute('download'), null, 'HTML otwiera stronę');
assert.match(htmlLecture.a.getAttribute('aria-label'), /^Otwórz HTML:/);
assert.equal(pairedSource.li.parentNode, null, 'źródłowe QMD w wierszu PDF');
assert.equal(pdfLecture.a.getAttribute('title'), 'Wprowadzenie do badań XR');
assert.match(lectureFormats.children[1].title, /Wprowadzenie do badań XR/);
assert.equal(editor.li.parentNode, null, 'bez zduplikowanej pozycji DOCX');
assert.equal(pptxLecture.li.parentNode, null, 'bez zduplikowanej pozycji PPTX');
assert.equal(htmlLecture.li.parentNode, null, 'bez zduplikowanej pozycji HTML');
assert.equal(columns.children[0], lectures.block, 'wykłady przed laboratoriami');
assert.equal(columns.children[1], labs.block);
assert.equal(displayRoot.dataset.materialsView, 'pdf');
assert.equal(pdfLab.li.hidden, false);
assert.equal(orphan.li.hidden, true);
assert.equal(orphanHtml.li.hidden, true);
assert.equal(sources.block.hidden, true);
assert.equal(pairedOnly.block.hidden, true);
tick = 100; fullToggle.events.click();
tick = 200; fullToggle.events.click();
tick = 300; fullToggle.events.click();
assert.equal(displayRoot.dataset.materialsView, 'all');
assert.equal(orphan.li.hidden, false, 'samodzielny TEX tylko w pełnym widoku');
assert.equal(orphanHtml.li.hidden, false, 'samodzielny HTML tylko w pełnym widoku');
assert.ok(orphan.a.classList.contains('material-link--editable'));
assert.equal(orphan.a.textContent, 'standalone');
assert.equal(orphan.a.children.length, 1);
assert.equal(orphan.a.children[0].textContent, ' · TEX');
assert.equal(orphanHtml.a.textContent, 'standalone');
assert.equal(orphanHtml.a.children[0].textContent, ' · HTML');
assert.ok(orphanHtml.a.children[0].classList.contains('material-format--standalone'));
assert.ok(orphan.a.children[0].classList.contains('material-format--standalone'));
assert.equal(sources.block.hidden, false);
assert.equal(pairedOnly.block.hidden, true, 'pusta podgrupa ukryta także w trybie pełnym');
assert.equal(labs.block.hidden, false);
assert.equal(lectures.block.hidden, false);
assert.match(html, /--lecture-edit:#254c6c/);
assert.match(html, /--lecture-edit:#87a8ca/);
assert.match(html, /--lab-edit:#27563b/);
assert.match(html, /--lab-edit:#85b098/);
assert.match(html, /a\.material-link--editable:visited\{color:var\(--edit\);text-decoration:underline/);
assert.match(html, /data-materials-view="all"/);
assert.match(html, /materials-group--flow\{display:inline-block;break-inside:avoid/);
assert.match(html, /\.materials-list a\{display:block;[^\n]*font-size:\.7rem/);
assert.match(html, /const BROWSER_EXTENSIONS = new Set\(\['html', 'htm'\]\)/);
console.log('[DONE] MATERIALS_FORMAT_PAIRS_PASS');
