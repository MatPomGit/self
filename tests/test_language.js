/* Regression checks for the original wheel page and the language switch. */
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const read = relative => fs.readFileSync(path.join(root, relative), 'utf8');
const html = read('index.html');
const source = read('docs/assets/js/site-i18n.js');

function loadLanguage(query) {
  const window = { location: { search: query } };
  vm.runInNewContext(source, { window, URLSearchParams });
  return window.SiteI18n;
}

const en = loadLanguage('?lang=en');
const pl = loadLanguage('?lang=pl');

assert.equal(en.language, 'en');
assert.equal(pl.language, 'pl');
assert.equal(en.translate('Wybierz'), 'Choose a');
assert.equal(en.translate('kategorię'), 'category');
assert.equal(en.translate('Dla studentów'), 'For students');
assert.equal(pl.translate('Dla studentów'), 'Dla studentów');

assert.match(html, /<svg class="wheel" id="wheel"/);
assert.equal((html.match(/<g class="grp">/g) || []).length, 5);
assert.match(html, /<nav class="language-switch" aria-label="Język strony">/);
assert.match(html, /href="\?lang=pl" hreflang="pl" lang="pl" aria-current="page"/);
assert.match(html, /href="\?lang=en" hreflang="en" lang="en"/);
assert.match(html, /<script src="docs\/assets\/js\/site-i18n.js"><\/script>/);
assert.match(html, /<img class="portrait" src="docs\/images\/self.png"/);
assert.match(html, /href="materials\/"/);
assert.match(html, /loadData\('docs\/data\/projects.json'/);
assert.match(html, /loadData\('docs\/data\/publications.json'/);
assert.match(html, /fetch\('docs\/data\/in-progress.json'\)/);
assert.doesNotMatch(html, /zensical|mkdocs-material/i);

for (const match of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) {
  new vm.Script(match[1]);
}

const projects = JSON.parse(read('docs/data/projects.json'));
const projectTranslations = JSON.parse(read('docs/data/projects.en.json'));
assert.equal(projects.length, projectTranslations.length);
assert.equal(new Set(projects.map(x => x.title)).size, projects.length);
assert.equal(new Set(projectTranslations.map(x => x.sourceTitle)).size, projects.length);

const reordered = [...projectTranslations].reverse();
const localizedProjects = en.translateProjects(projects, reordered);
assert.equal(localizedProjects.length, projects.length);
for (let index = 0; index < projects.length; index++) {
  const sourceProject = projects[index];
  const translation = projectTranslations.find(x => x.sourceTitle === sourceProject.title);
  assert.ok(translation, sourceProject.title);
  assert.equal(localizedProjects[index].title, translation.title);
  assert.equal(localizedProjects[index].description, translation.description);
}
assert.throws(() => en.translateProjects(projects, projectTranslations.slice(1)), /mismatch|Missing/);
assert.throws(() => en.translateProjects(projects, [projectTranslations[0], ...projectTranslations.slice(0, -1)]), /Duplicate/);

const progress = JSON.parse(read('docs/data/in-progress.json'));
const manuscriptTranslations = JSON.parse(read('docs/data/in-progress.en.json'));
assert.equal(progress.length, Object.keys(manuscriptTranslations).length);
assert.equal(new Set(progress.map(x => x.id)).size, progress.length);
for (const paper of en.translateManuscripts(progress, manuscriptTranslations)) {
  assert.equal(paper.description, manuscriptTranslations[paper.id].description);
  assert.equal(paper.nextStep, manuscriptTranslations[paper.id].nextStep);
  assert.ok(paper.description.trim() && paper.nextStep.trim());
}
const missing = { ...manuscriptTranslations };
delete missing[progress[0].id];
assert.throws(() => en.translateManuscripts(progress, missing), /mismatch|Missing/);

console.log('[DONE] Bilingual wheel, translations, project identity and manuscript data: PASS');
