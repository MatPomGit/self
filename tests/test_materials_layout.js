// Layout regression check without browser libraries. Visual smoke tests use Chromium.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync('materials/index.html', 'utf8');
const style = html.split('<style>')[1].split('</style>')[0];
assert.match(style, /\.materials-grid\{columns:auto 28rem;column-gap:10px/);
assert.match(style, /\.materials-group\{display:inline-block;vertical-align:top;width:100%/);
assert.match(style, /break-inside:avoid;page-break-inside:avoid/);
assert.match(style, /@media\(min-width:720px\) and \(max-width:1000px\)/);
assert.match(style, /\.materials-grid\{columns:auto 22rem\}/);
assert.match(style, /@media\(max-width:620px\)/);
assert.match(style, /\.materials-grid\{columns:1\}/);
assert.match(style, /\.materials-list\{[^}]*grid-template-columns:repeat\(auto-fit/);
assert.match(style, /overflow-wrap:break-word;white-space:normal/);
assert.doesNotMatch(style, /grid-auto-flow:dense|grid-row-end:span|grid-column:span 2/);
assert.doesNotMatch(html, /initAdaptiveMaterialsGrid|materials-grid--masonry/);
assert.match(html, /const materialRows = typeof document.createElement/);
assert.match(html, /setMaterialsView\('pdf'\)/);
console.log('[DONE] MATERIALS_BALANCED_COLUMNS_PASS');
