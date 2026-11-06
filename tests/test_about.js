// Regression tests: the research biography is loaded from one bilingual file.
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('index.html', 'utf8');
const about = JSON.parse(fs.readFileSync('docs/data/about.json', 'utf8'));

const start = html.indexOf('    async function loadAbout(){');
const call = '    loadAbout();';
const end = html.indexOf(call, start);
assert.ok(start >= 0 && end > start, 'Biography loader exists in the homepage');
const loader = html.slice(start, end + call.length);

async function exercise(language, data = about, responseOk = true) {
  const elements = new Map(['research-status', 'research-intro', 'research-work', 'research-summary']
    .map(id => [id, {
      id, hidden: false, textContent: '', children: [],
      replaceChildren(...values) {
        this.children = values.flatMap(value => value.children || [value]);
      }
    }]));
  const createFragment = () => ({
    children: [],
    append(...children) { this.children.push(...children); }
  });
  const errors = [];
  const makeElement = (tag, className, value) => ({tag, className, textContent:value, children:[]});
  const translate = value => language === 'en' ? ({
    'Nad czym pracuję':'What I work on',
    'Nie udało się wczytać opisu.':'Could not load the biography.',
  })[value] || value : value;
  const context = {
    document: {
      getElementById: id => elements.get(id),
      createDocumentFragment: createFragment,
    },
    fetch: async path => {
      assert.equal(path, 'docs/data/about.json');
      return {ok:responseOk, status:503, json:async () => data};
    },
    i18n: {language},
    tr: translate,
    makeElement,
    console: {error:(...args) => errors.push(args)}
  };
  await vm.runInNewContext(loader, context);
  return {elements, errors};
}

(async () => {
  for (const language of ['pl', 'en']) {
    const {elements, errors} = await exercise(language);
    const story = about[language];
    assert.deepEqual(errors, []);
    assert.equal(elements.get('research-status').hidden, true);
    assert.deepEqual(elements.get('research-intro').children.map(x => x.textContent), story.intro);
    assert.deepEqual(elements.get('research-work').children.slice(1).map(x => x.textContent), story.work);
    assert.equal(elements.get('research-work').children[0].textContent,
      language === 'pl' ? 'Nad czym pracuję' : 'What I work on');
    assert.equal(elements.get('research-summary').textContent, story.summary);
  }
  const failed = await exercise('pl', about, false);
  assert.equal(failed.elements.get('research-status').hidden, false);
  assert.equal(failed.elements.get('research-status').textContent, 'Nie udało się wczytać opisu.');
  assert.equal(failed.errors.length, 1);
  const invalid = await exercise('en', {pl:about.pl,en:{intro:[],work:[],summary:''}});
  assert.equal(invalid.elements.get('research-status').textContent, 'Could not load the biography.');
  console.log('[DONE] ABOUT_CONTENT_LOADER_PASS');
})().catch(error => {console.error(error); process.exitCode = 1;});
