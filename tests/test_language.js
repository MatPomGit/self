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
assert.equal(en.translate('Świat większy od nas'), 'A world bigger than us');
assert.equal(en.translate('Wiele sposobów widzenia'), 'Many ways of seeing');
assert.equal(en.translate('Świat, który tworzy mózg'), 'The world our brains create');
assert.equal(en.translate('Nad czym pracuję'), 'What I work on');
assert.equal(en.translate('Najbardziej interesuje mnie'), 'What fascinates me most is');
assert.equal(en.translate('Aktualne programy badawczo-rozwojowe'), 'Current research and development programmes');
assert.equal(en.translate('Wybrane projekty i konsorcja'), 'Selected projects and consortia');
assert.equal(pl.translate('Dla studentów'), 'Dla studentów');

const lead = html.match(/<p class="lead">([^<]+)<\/p>/)[1].replace(/&nbsp;/g, '\u00a0');
const role = html.match(/<p class="role">([^<]+)<\/p>/)[1].replace(/&nbsp;/g, '\u00a0');
assert.match(en.translate(lead), /^My research integrates computer science and neuroscience/);
assert.equal(en.translate(role), 'Assistant Professor, Department of Computer and Control Engineering');
assert.equal(en.translate('Informatyka afektywna i\u00a0'), 'Affective computing and');
assert.equal(en.translate('  Wybierz  '), 'Choose a');
assert.equal(en.translate('Unknown academic label'), 'Unknown academic label');
assert.equal(pl.translate(lead), lead);
assert.equal(en.publicationMetadata('t. 25, nr 20, s. 6460 · MEiN: 100 pkt'),
  'vol. 25, no. 20, pp. 6460 · MEiN: 100 points');
assert.equal(en.publicationMetadata('20 marca 2025 · 10 stycznia 2024'), '20 March 2025 · 10 January 2024');
assert.equal(en.publicationMetadata('Microelectronic Devices, s. 28–30, paź. 2020'),
  'Microelectronic Devices, pp. 28–30, Oct. 2020');
assert.match(html, /themeToggle.setAttribute\('aria-label', action\)/);
// All Polish interface strings must have an English equivalent. Bibliographic
// titles are not in the static HTML; street names are proper nouns.
const staticPage = html.slice(html.indexOf('<body>'), html.indexOf('<script src="docs/assets/js/site-i18n.js">'))
  .replace(/<div class="research-(?:intro|work)">[\s\S]*?<\/div>/g, '');
const missingUI = [...staticPage.matchAll(/>([^<>]+)</g)]
  .map(match => match[1].replace(/&nbsp;/g, '\u00a0').trim())
  .filter(value => /[ąćęłńóśźż]/iu.test(value) && en.translate(value) === value)
  .filter(value => !['al. Powstańców Warszawy 12', '35 959 Rzeszów'].includes(value));
assert.deepEqual(missingUI, []);
assert.equal(en.translate('dr inż. Mateusz Pomianek'), 'Mateusz Pomianek, PhD, Eng.');


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

const story = html.match(/<div class="research-intro">([\s\S]*?)<\/div>/)?.[1];
assert.ok(story, 'Research story is present');
const polishParagraphs = [...story.matchAll(/<p>([\s\S]*?)<\/p>/g)];
assert.equal(polishParagraphs.length, 5, 'Short research story has five paragraphs');
const englishParagraphsSource = source.match(/const researchParagraphs = \[([\s\S]*?)\n  \];/)?.[1];
assert.ok(englishParagraphsSource, 'Research translations are present');
const englishParagraphs = vm.runInNewContext('[' + englishParagraphsSource + ']', {});
const researchWork = html.match(/<div class="research-work">([\s\S]*?)<\/div>/)?.[1];
assert.ok(researchWork, 'Research-work section follows the philosophical story');
const workParagraphs = [...researchWork.matchAll(/<p>([\s\S]*?)<\/p>/g)];
assert.equal(workParagraphs.length, 2, 'The work section has exactly two concise paragraphs');
assert.ok(html.indexOf('class="research-summary"') < html.indexOf('class="research-work"'));
assert.equal(englishParagraphs.length, polishParagraphs.length + workParagraphs.length, 'PL/EN research paragraph counts match');
assert.match(source, /#badania \.research-intro p, #badania \.research-work p/);
assert.ok(englishParagraphs.every(text => text.length > 80), 'English paragraphs have content');
assert.match(englishParagraphs[0], /universe/);
assert.match(englishParagraphs[1], /models of the world/);
assert.match(englishParagraphs[3], /brains/);
assert.match(englishParagraphs[5], /optoelectronics/);
assert.match(englishParagraphs[6], /Neuroscience and psychology/);

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
  assert.equal(localizedProjects[index].period, translation.period);
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
