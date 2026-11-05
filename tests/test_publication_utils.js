/* Functional regression tests for publication links, citations and async filtering. */
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('docs/assets/js/publication-utils.js', 'utf8');
const html = fs.readFileSync('index.html', 'utf8');
const window = {};
vm.runInNewContext(source, {window, URL});
const {safeHttpsUrl, bibtexEscape, bibtexAuthors, bibtexText} = window.SelfPublications;

assert.equal(safeHttpsUrl('https://example.org/article?x=1'), 'https://example.org/article?x=1');
for (const invalid of [
  null, '', '/relative/file', 'http://example.org', 'javascript:alert(1)',
  'data:text/html,a', 'https://user:secret@example.org', 'https://',
  'https://example.org@evil.invalid/path'
]) {
  assert.equal(safeHttpsUrl(invalid), null, String(invalid));
}
assert.equal(bibtexEscape('A&B_50%#' + '$' + '{^~\\}'),
  'A\\&B\\_50\\%\\#\\$\\{\\textasciicircum{}\\textasciitilde{}\\textbackslash{}\\}');
assert.equal(bibtexAuthors('Pomianek M. , Piszczek M., Stawarz P.'),
  'Pomianek, M. and Piszczek, M. and Stawarz, P.');
assert.equal(bibtexAuthors('Piszczek M. et al.'), 'Piszczek, M. and others');
const entry = {
  type: 'journal', authors: 'Piszczek M. et al.', year: 2022,
  title: 'A&B {C}', metadata: '50% improved', link: 'https://doi.org/10.example/test'
};
const bibtex = bibtexText(entry, 0);
assert.match(bibtex, /^@article\{piszczek2022_1,/);
assert.match(bibtex, /author = \{Piszczek, M\. and others\}/);
assert.match(bibtex, /title = \{A\\&B \\{C\\}\}/);
assert.match(bibtex, /note = \{50\\% improved\}/);
assert.match(bibtex, /url = \{https:\/\/doi.org\/10\.example\/test\}/);
assert.doesNotMatch(bibtexText({...entry, link: 'javascript:alert(1)'}, 0), /url = /);

// Evaluate the actual filter handlers and delayed publications callback.
const start = html.indexOf('    let publicationRecords=[];');
const stop = html.indexOf('    async function renderProgress(){', start);
const eventsStart = html.indexOf("    document.querySelectorAll('#publication-filters button').forEach", stop);
const eventsStop = html.indexOf('    const requested=location.hash.slice(1);', eventsStart);
assert.ok(start > 0 && stop > start && eventsStart > stop && eventsStop > eventsStart);
const observed = [];
const buttons = ['all', 'journal', 'progress'].map(filter => ({
  dataset: {filter},
  setAttribute() {},
  addEventListener(name, callback) {this[name] = callback;}
}));
const publications = {hidden:false};
const progress = {hidden:true};
let delayedPublicationCallback;
const context = {
  window: {SelfPublications: window.SelfPublications},
  observed,
  document: {
    querySelectorAll(selector) {
      assert.equal(selector, '#publication-filters button');
      return buttons;
    },
    getElementById(id) {
      return id === 'publications-list' ? publications : progress;
    }
  },
  loadData(path, listId, statusId, callback) {
    if (path === 'docs/data/publications.json') delayedPublicationCallback = callback;
  },
  renderProjects() {}
};
const handlers = html.slice(start, stop) +
  '\nrenderPublications = filter => observed.push(filter);\n' +
  html.slice(eventsStart, eventsStop);
vm.runInNewContext(handlers, context);
assert.equal(typeof delayedPublicationCallback, 'function');
buttons[1].click();
assert.equal(observed.at(-1), 'journal');
delayedPublicationCallback([entry]);
assert.equal(observed.at(-1), 'journal', 'late response preserves journal filter');
assert.equal(publications.hidden, false);
buttons[2].click();
const renders = observed.length;
delayedPublicationCallback([entry]);
assert.equal(observed.length, renders, 'late response does not render behind progress view');
assert.equal(publications.hidden, true);
assert.equal(progress.hidden, false);
console.log('[DONE] PUBLICATION_UTILS_PASS');
