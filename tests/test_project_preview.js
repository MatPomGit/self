/* Behavioral regression tests for project detail dialogs (no browser dependencies). */
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

class Element {
  constructor(tag) {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.listeners = new Map();
    this.attributes = new Map();
    this.className = '';
    this.textContent = '';
    this.hidden = false;
    this.open = false;
    this.isConnected = true;
  }
  append(...children) {
    for (const child of children) {
      child.parent = this;
      this.children.push(child);
    }
  }
  replaceChildren(...children) {
    this.children = [];
    this.append(...children);
  }
  setAttribute(name, value) { this.attributes.set(name, String(value)); }
  getAttribute(name) { return this.attributes.get(name) ?? null; }
  addEventListener(type, callback) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type).push(callback);
  }
  dispatch(type, event = {}) {
    for (const callback of this.listeners.get(type) || []) callback(event);
  }
  closest(selector) {
    if (selector !== 'a,button') throw new Error('Unexpected selector: ' + selector);
    for (let node = this; node; node = node.parent) {
      if (node.tagName === 'A' || node.tagName === 'BUTTON') return node;
    }
    return null;
  }
  showModal() { this.open = true; }
  close() { this.open = false; this.dispatch('close'); }
  focus() { this.focused = true; }
  remove() {
    if (this.parent) this.parent.children = this.parent.children.filter(node => node !== this);
  }
}

const document = {body: new Element('body'), createElement: tag => new Element(tag)};
const window = {};
const read = path => fs.readFileSync(path, 'utf8');
vm.runInNewContext(read('docs/assets/js/publication-utils.js'), {window, URL});
vm.runInNewContext(read('docs/assets/js/project-preview.js'), {window, document});
const dialog = document.body.children[0];
assert.equal(dialog.tagName, 'DIALOG');

const descendants = (root, predicate) => [
  ...(predicate(root) ? [root] : []),
  ...root.children.flatMap(child => descendants(child, predicate))
];
const byTag = tag => descendants(dialog, node => node.tagName === tag);
const byClass = name => descendants(dialog, node => node.className === name);

const card = new Element('article');
const project = {
  title: 'Projekt testowy',
  period: '2026',
  phase: 'current',
  description: 'Opis projektu',
  details: {
    logo: 'https://invalid.example/logo.svg',
    pl: {methods: ['EEG'], outcomes: ['Wynik'], focus: 'Interfejs'},
    en: {methods: ['BCI'], outcomes: ['Result'], focus: 'Interface'},
    links: [
      {label: 'Publikacja', url: 'https://example.org/paper'},
      {label: 'HTTP', url: 'http://example.org'},
      {label: 'Skrypt', url: 'javascript:alert(1)'},
      {label: 'Dane logowania', url: 'https://user:secret@example.org'},
      {label: '', url: 'https://example.org/empty'},
      {label: 'Niepoprawne', url: '/local/path'}
    ]
  }
};

window.ProjectPreview.attach(card, project, 'en');
assert.equal(card.tabIndex, 0);
assert.equal(card.getAttribute('role'), 'button');
assert.equal(card.getAttribute('aria-haspopup'), 'dialog');
assert.equal(card.getAttribute('aria-label'), 'Project details: Projekt testowy');

const nestedLink = new Element('a');
card.append(nestedLink);
card.dispatch('click', {target:nestedLink});
assert.equal(dialog.open, false, 'Clicking a nested anchor does not open the dialog');

let prevented = false;
card.dispatch('keydown', {key:'Enter', target:card, preventDefault(){prevented = true;}});
assert.equal(prevented, true);
assert.equal(dialog.open, true);
assert.equal(dialog.getAttribute('aria-label'), 'Project details: Projekt testowy');
assert.equal(byTag('A').length, 1, 'Only safe project links are rendered');
assert.equal(byTag('A')[0].href, 'https://example.org/paper');
assert.equal(byTag('A')[0].rel, 'noopener noreferrer');
assert.equal(byTag('IMG').length, 0, 'Remote logo is rejected');
assert.equal(byClass('project-detail-section').length, 6);
const close = byClass('project-detail-close')[0];
assert.equal(close.getAttribute('aria-label'), 'Close');
assert.equal(close.focused, true);
close.dispatch('click');
assert.equal(dialog.open, false);
assert.equal(card.focused, true, 'Focus returns to the triggering project card');

const secondCard = new Element('article');
window.ProjectPreview.attach(secondCard, {...project, details:{links:[]}}, 'unknown');
secondCard.dispatch('click', {target:secondCard});
assert.equal(dialog.open, true);
assert.equal(dialog.getAttribute('aria-label'), 'Szczegóły projektu: Projekt testowy');
assert.equal(byTag('A').length, 0, 'No empty external links section');
byClass('project-detail-close')[0].dispatch('click');
assert.equal(secondCard.focused, true);
console.log('[DONE] PROJECT_PREVIEW_PASS');
