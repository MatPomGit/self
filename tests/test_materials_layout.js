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
const desktop = /^([45])\s+(\d+(?:\.\d+)?)rem$/.exec(grid[0].columns || '');
const medium = /^([234])\s+(\d+(?:\.\d+)?)rem$/.exec(grid[1].columns || '');
assert.ok(desktop, 'Desktop must cap automatic columns at four or five');
assert.ok(medium, 'Medium viewport must cap automatic columns');
const desktopLimit = Number(desktop[1]);
const mediumLimit = Number(medium[1]);
const desktopWidth = Number(desktop[2]);
const mediumWidth = Number(medium[2]);
assert.equal(desktopLimit, 5, 'Desktop must support up to five columns');
assert.equal(mediumLimit, 4, 'Medium viewport must support up to four columns');
assert.ok(desktopWidth >= 15 && desktopWidth <= 18, 'Desktop cards must remain compact (15-18rem)');
assert.ok(mediumWidth >= 14 && mediumWidth <= desktopWidth, 'Medium cards must remain compact');
function estimatedColumnCount(viewport, countLimit, widthRem, gapPx) {
  const innerWidth = Math.min(viewport, 1600) - 20;
  return Math.min(countLimit, Math.max(1, Math.floor((innerWidth + gapPx) / (widthRem * 16 + gapPx))));
}
assert.equal(estimatedColumnCount(1280, desktopLimit, desktopWidth, 7), 4,
  '1280px viewport should fit four cards across');
assert.equal(estimatedColumnCount(1440, desktopLimit, desktopWidth, 7), 5,
  '1440px viewport should fit five cards across');
assert.equal(estimatedColumnCount(1920, desktopLimit, desktopWidth, 7), 5,
  'The five-column limit must hold on wide screens');
assert.ok(cssLength(grid[0]['column-gap'], 'px', 'Desktop gap') <= 8);
assert.ok(cssLength(grid[0]['margin-top'], 'px', 'Grid top margin') <= 8);
assert.equal(grid[2].columns, '1', 'Mobile view must use one column');
assert.ok(style.includes('@media(min-width:720px) and (max-width:1000px)'), 'Medium viewport breakpoint missing');
assert.ok(style.includes('@media(max-width:620px)'), 'Mobile viewport breakpoint missing');

const group = one('.materials-group');
assert.equal(group.display, 'block', 'Block cards must be fragmentable across columns');
assert.equal(group.width, '100%');
assert.equal(group['break-inside'], 'auto', 'Card content must be able to continue in the next column');
assert.equal(group['page-break-inside'], 'auto');
assert.equal(group['box-decoration-break'], 'clone', 'Fragment borders and padding must be preserved');
assert.ok(cssLength(group.padding, 'px', 'Card padding') <= 8);
assert.ok((group.margin || '').startsWith('0 0 '), 'Cards must not have a top margin');
const flow = one('.materials-group--flow');
assert.equal(flow.display, 'block', 'Large cards cannot remain inline-block');
assert.equal(flow['break-inside'], 'auto', 'Long cards must split between columns');
assert.equal(one('.materials-group--flow .materials-subgroup')['break-inside'], 'auto');
const subgroup = one('.materials-subgroup');
assert.equal(subgroup['break-inside'], 'auto', 'A single long module must be fragmentable');
assert.equal(subgroup['box-decoration-break'], 'clone');
assert.equal(one('.materials-group>h4,.materials-subgroup>h5')['break-after'], 'avoid',
  'Headings should stay with the first row of their content');
const columns = one('.materials-columns');
assert.equal(columns.display, 'flex', 'Module groups must flow beside one another');
assert.equal(columns['flex-wrap'], 'wrap', 'Module groups must wrap instead of overflowing');
assert.equal(columns['align-items'], 'flex-start');
assert.ok(cssLength(columns.gap, 'px', 'Internal module gap') <= 4);
const subgroupFlow = one('.materials-columns>.materials-subgroup');
assert.equal(subgroupFlow.flex, '1 1 8rem', 'Short modules must share available width');
assert.equal(subgroupFlow['max-width'], '100%');
assert.equal(one('.materials-columns>.materials-subgroup:has(.materials-list li:nth-child(n+9):not([hidden]))')['flex-basis'], '100%',
  'Modules with at least nine visible files need a full-width row');

const list = one('.materials-list');
assert.equal(list.display, 'flex', 'Items must use their intrinsic text widths');
assert.equal(list['flex-wrap'], 'wrap', 'Items should flow onto the next line when necessary');
assert.ok(!list['grid-template-columns'], 'Fixed-width grid tracks must not reserve empty space');
assert.equal(list['align-items'], 'baseline', 'Adjacent file names should align on the text baseline');
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
assert.equal(variantName.flex, '0 1 auto', 'PDF labels must not stretch to fill empty space');
assert.equal(variantName['min-width'], '0', 'PDF labels need shrinkable flex width');
assert.equal(variantFormats['flex'], '0 0 auto', 'File formats must remain visible');
assert.ok(cssLength(links['font-size'], 'rem', 'File label size') <= 0.75);
const item = one('.materials-list li');
assert.equal(item.flex, '0 1 auto', 'List items must shrink-wrap their contents');
assert.equal(item['max-width'], '100%', 'Long names must not overflow their subgroup');
assert.equal(item['break-inside'], 'avoid', 'Individual file links must remain whole at a column boundary');
assert.ok(!style.includes('--material-min'), 'Unused fixed track widths must be removed');
assert.equal(one('.materials-list--dense')['line-height'], '1.05');
assert.ok(cssLength(one('.materials-list .material-formats')['font-size'], 'rem', 'Format suffix') <= 0.6);
assert.ok(cssLength(one('.materials-list .material-format--standalone')['font-size'], 'rem', 'Standalone format suffix') <= 0.6);

assert.ok(!/grid-auto-flow:dense|grid-row-end:span|grid-column:span 2/.test(style), 'Avoid layout-spanning gaps');
assert.ok(!/initAdaptiveMaterialsGrid|materials-grid--masonry/.test(html), 'Legacy masonry logic must remain removed');
assert.ok(html.includes('const materialRows = typeof document.createElement'));
assert.ok(html.includes("setMaterialsView('pdf')"));
console.log('[DONE] MATERIALS_LAYOUT_CONTRACT_PASS');
