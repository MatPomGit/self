/* Reusable citation formatting and external-link validation for the static website. */
(() => {
  'use strict';

  function safeHttpsUrl(value) {
    if (typeof value !== 'string' || !value.trim()) return null;
    try {
      const url = new URL(value);
      return url.protocol === 'https:' && url.hostname && !url.username && !url.password
        ? url.href : null;
    } catch (_) {
      return null;
    }
  }

  function bibtexKey(entry, index) {
    const last = (entry.authors || 'author').split(',')[0].trim().split(' ')[0]
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
    return (last || 'author') + (entry.year || 'nd') + '_' + (index + 1);
  }

  function bibtexEscape(value) {
    const escapes = {
      '\\': '\\textbackslash{}', '{': '\\{', '}': '\\}',
      '&': '\\&', '%': '\\%', '$': '\\$', '#': '\\#',
      '_': '\\_', '^': '\\textasciicircum{}', '~': '\\textasciitilde{}'
    };
    return String(value ?? '').replace(/[\\{}&%$#_^~]/g, char => escapes[char]);
  }

  function bibtexAuthors(authors) {
    // BibTeX uses "and others" to represent an incomplete "et al." author list.
    const names = String(authors || '').trim().replace(/(?:,\s*)?\bet\s+al\.?$/i, ', others');
    return names.split(',').map(name => name.trim()).filter(Boolean).map(name => {
      if (name.toLowerCase() === 'others') return 'others';
      const parts = name.match(/^(.+?)\s+((?:[A-ZĄĆĘŁŃÓŚŹŻ]\.)+)$/u);
      return parts ? parts[1] + ', ' + parts[2] : name;
    }).join(' and ');
  }

  function bibtexText(entry, index) {
    const type = {journal:'article', conference:'inproceedings', patent:'misc'}[entry.type] || 'misc';
    const props = [
      ['title', entry.title],
      ['year', entry.year],
      ['author', bibtexAuthors(entry.authors)],
      ['note', entry.metadata],
      ['url', safeHttpsUrl(entry.link)]
    ].filter(([, value]) => value != null && String(value).trim());
    return '@' + type + '{' + bibtexKey(entry, index) + ',\n' +
      props.map(([key, value]) => '  ' + key + ' = {' + bibtexEscape(value) + '}').join(',\n') + '\n}';
  }

  window.SelfPublications = Object.freeze({safeHttpsUrl, bibtexEscape, bibtexAuthors, bibtexText});
})();
