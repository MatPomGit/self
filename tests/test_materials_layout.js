// Validate layout semantics, not exact CSS formatting or a whole HTML snapshot.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync('materials/index.html', 'utf8');
const style = html.split('<style>')[1]?.split('</style>')[0];
assert.ok(style, 'Materials page must include its stylesheet');

// Look up individual CSS declarations so spacing and property order can change.
function rules(selector) {
  const escaped = selector.replace(/[^a-zA-Z0-9-]/g, character => '\\' + character);
  const pattern = new RegExp('(?:^|\\n)\\s*' + escaped + '\\s*\\{([^{}]*)\\}', 'g');
  return [...style.matchAll(pattern)].map(([, body]) =>
    Object.fromEntries(body.split(';').map(part => part.trim()).filter(Boolean).map(entry => {
      const separator = entry.indexOf(':');
      assert.ok(separator > 0, 'Malformed declaration for ' + selector);
      return [entry.slice(0, separator).trim(), entry.slice(separator + 1).trim()];
    }))
  );
}
function one(selector) {
  const found = rules(selector);
  assert.equal(found.length, 1, 'Expected exactly one rule for ' + selector);
  return found[0];
}
function cssLength(value, unit, label) {
  // CSS allows zero without units; it is equivalent to 0px or 0rem.
  if (value === '0') return 0;
  const match = new RegExp('^((?:\\d+(?:\\.\\d*)?|\\.\\d+))' + unit + '$').exec(value || '');
  assert.ok(match, label + ': expected ' + unit + ', received ' + value);
  return Number(match[1]);
}

const grid = rules('.materials-grid');
assert.equal(grid.length, 3, 'Desktop, medium-width and mobile grid rules required');
const desktop = /^auto\s+(\d+(?:\.\d+)?)rem$/.exec(grid[0].columns || '');
const medium = /^auto\s+(\d+(?:\.\d+)?)rem$/.exec(grid[1].columns || '');
assert.ok(desktop, 'Desktop cards must use automatic rem-width columns');
assert.ok(medium, 'Medium-width cards must use automatic rem-width columns');
const desktopWidth = Number(desktop[1]);
const mediumWidth = Number(medium[1]);
assert.ok(desktopWidth >= 18 && desktopWidth <= 24, 'Desktop cards should stay compact (18-24rem)');
assert.ok(mediumWidth >= 16 && mediumWidth <= desktopWidth, 'Medium viewport cards should stay compact');
assert.ok(cssLength(grid[0]['column-gap'], 'px', 'Desktop gap') <= 8);
assert.ok(cssLength(grid[0]['margin-top'], 'px', 'Grid top margin') <= 8);
assert.equal(grid[2].columns, '1', 'Mobile view must use one column');
assert.ok(style.includes('@media(min-width:720px) and (max-width:1000px)'), 'Medium viewport breakpoint missing');
assert.ok(style.includes('@media(max-width:620px)'), 'Mobile viewport breakpoint missing');

const group = one('.materials-group');
assert.equal(group.display, 'inline-block');
assert.equal(group['vertical-align'], 'top');
assert.equal(group.width, '100%');
assert.equal(group['break-inside'], 'avoid');
assert.ok(cssLength(group.padding, 'px', 'Card padding') <= 8);
assert.ok((group.margin || '').startsWith('0 0 '), 'Cards must not have a top margin');
assert.equal(one('.materials-group--flow')['break-inside'], 'avoid');
assert.equal(one('.materials-columns').display, 'block');

const list = one('.materials-list');
assert.equal(list.display, 'grid');
// Fixed maximum track width prevents filenames stretching across a wide card.
// Fallback variable values must match for both min and max expressions.
const tracks = (list['grid-template-columns'] || '').replace(/\s+/g, '');
const fixedTracks = /^repeat\(auto-fill,minmax\(min\(100%,var\(--material-min,([0-9.]+rem)\)\),var\(--material-min,\1\)\)\)$/;
assert.ok(fixedTracks.test(tracks), 'File grid must use fixed-width auto-fill tracks, not auto-fit/1fr');
assert.ok(cssLength(list['column-gap'], 'px', 'Link column gap') <= 6);
assert.ok(cssLength(list['row-gap'], 'px', 'Link row gap') <= 2);

const links = rules('.materials-list a')[0];
assert.ok(links, 'Main link CSS rule missing');
assert.equal(links['white-space'], 'nowrap', 'Labels must stay on one line');
assert.equal(links['overflow'], 'hidden', 'Overflowing labels must be clipped');
assert.equal(links['text-overflow'], 'ellipsis', 'Truncated names must have an ellipsis');
assert.equal(links['min-width'], '0', 'Labels must be allowed to shrink');
assert.equal(links['max-width'], '100%', 'Labels may not exceed their grid cell');
const variantRow = one('.materials-list li.materials-row--variants');
const variantName = one('.materials-list li.materials-row--variants>a');
const variantFormats = one('.materials-list li.materials-row--variants .material-formats');
assert.equal(variantRow.display, 'flex', 'PDF and variants must share a row');
assert.equal(variantName['text-overflow'], 'ellipsis', 'PDF labels must truncate without hiding formats');
assert.equal(variantName['min-width'], '0', 'PDF labels need shrinkable flex width');
assert.equal(variantFormats['flex'], '0 0 auto', 'File formats must remain visible');
assert.ok(cssLength(links['font-size'], 'rem', 'File label size') <= 0.75);
assert.equal(one(':root[data-materials-view="all"] .materials-list--dense')['--material-min'], '7.5rem');
assert.ok(cssLength(one('.materials-list--dense')['--material-min'], 'rem', 'Dense track width') <= 6);
assert.ok(cssLength(one('.materials-list .material-formats')['font-size'], 'rem', 'Format suffix') <= 0.6);
assert.ok(cssLength(one('.materials-list .material-format--standalone')['font-size'], 'rem', 'Standalone format suffix') <= 0.6);

assert.ok(!/grid-auto-flow:dense|grid-row-end:span|grid-column:span 2/.test(style), 'Avoid layout-spanning gaps');
assert.ok(!/initAdaptiveMaterialsGrid|materials-grid--masonry/.test(html), 'Legacy masonry logic must remain removed');
assert.ok(html.includes('const materialRows = typeof document.createElement'));
assert.ok(html.includes("setMaterialsView('pdf')"));
console.log('[DONE] MATERIALS_LAYOUT_CONTRACT_PASS');
