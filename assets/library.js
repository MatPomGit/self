/* Static library for GitHub Pages. No dependencies, analytics or remote APIs. */
(() => {
  'use strict';
  const script = document.currentScript;
  const root = new URL('../', script.src);
  const manifestUrl = new URL('assets/library.json', root);
  const main = document.querySelector('[data-library]');
  if (!main) return;
  const kindLabel = { f: 'Plik', p: 'PDF', h: 'HTML' };
  const idPattern = /^\d{2,}$/;
  const perPage = 24;

  function valid(entry) {
    return entry && ['f','p','h'].includes(entry.type) &&
      typeof entry.id === 'string' && idPattern.test(entry.id) &&
      typeof entry.title === 'string' && entry.title.trim() &&
      typeof entry.source === 'string' && !!resolveSource(entry.source);
  }
  function resolveSource(source) {
    if (typeof source !== 'string' || !source) return null;
    if (/^https:\/\//i.test(source)) {
      try {
        const url = new URL(source);
        return (url.username || url.password) ? null : url;
      } catch { return null; }
    }
    if (!/^[\w./-]+$/.test(source) ||
        source.startsWith('/') ||
        source.split('/').some(x => x === '..' || x === '.' || x === '') ||
        source.includes('\\')) return null;
    const url = new URL(source, root);
    return url.href.startsWith(root.href) ? url : null;
  }
  function route(entry) {
    return new URL(entry.type + '/' + entry.id + '/', root).href;
  }
  function element(tag, cls, text) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function link(text, href, downloadName) {
    const a = element('a', 'action', text);
    a.href = href;
    if (downloadName) a.download = downloadName;
    if (!href.startsWith(root.href)) {
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
    }
    return a;
  }
  function metadata(entry) {
    const line = element('div', 'kicker');
    line.append(element('span','tag',kindLabel[entry.type]), element('span','muted',entry.category || 'Inne'), element('span','muted',entry.type+'/'+entry.id));
    return line;
  }
  function card(entry) {
    const article = element('article','item');
    article.append(metadata(entry),element('h2','',entry.title),element('p','muted',entry.description || ''));
    const actions = element('div','actions');
    actions.append(link('Zobacz',route(entry)));
    const src = resolveSource(entry.source);
    if (src) actions.append(link(src.href.startsWith(root.href) ? 'Pobierz plik' : 'Otwórz źródło', src.href, src.href.startsWith(root.href) ? entry.source.split('/').pop() : undefined));
    article.append(actions);
    return article;
  }
  function renderCatalog(items) {
    const search = document.getElementById('library-search');
    const type = document.getElementById('library-type');
    const category = document.getElementById('library-category');
    const count = document.getElementById('library-count');
    const results = document.getElementById('library-results');
    const previous = document.getElementById('library-prev');
    const next = document.getElementById('library-next');
    const current = document.getElementById('library-page');
    let page = 1;
    const categories = [...new Set(items.map(e => e.category || 'Inne'))].sort((a,b)=>a.localeCompare(b,'pl'));
    categories.forEach(c => {
      const opt = document.createElement('option');
      opt.value=c; opt.textContent=c; category.append(opt);
    });
    function refresh() {
      const query=search.value.trim().toLocaleLowerCase('pl');
      const filtered=items.filter(e =>
        (!type.value || type.value === e.type) &&
        (!category.value || category.value === (e.category || 'Inne')) &&
        (!query || [e.title,e.description||'',e.category||'',e.type+'/'+e.id].join(' ').toLocaleLowerCase('pl').includes(query)));
      const pages=Math.max(1,Math.ceil(filtered.length/perPage));
      page=Math.min(page,pages);
      const begin=(page-1)*perPage;
      results.replaceChildren();
      if (!filtered.length) results.append(element('p','empty','Brak zasobów spełniających kryteria.'));
      filtered.slice(begin,begin+perPage).forEach(e=>results.append(card(e)));
      count.textContent = 'Znaleziono: '+filtered.length+' z '+items.length;
      current.textContent = 'Strona '+page+' z '+pages;
      previous.disabled=page<=1; next.disabled=page>=pages;
    }
    [search,type,category].forEach(n=>n.addEventListener(n===search?'input':'change',()=>{page=1;refresh()}));
    previous.addEventListener('click',()=>{if(page>1){page--;refresh()}});
    next.addEventListener('click',()=>{page++;refresh()});
    refresh();
  }
  function renderReader(items) {
    const type=main.dataset.type, id=main.dataset.id;
    const entry=items.find(e=>e.type===type && e.id===id);
    const title=document.getElementById('resource-title');
    const desc=document.getElementById('resource-description');
    const meta=document.getElementById('resource-meta');
    const actions=document.getElementById('resource-actions');
    const preview=document.getElementById('resource-preview');
    if (!entry) {
      document.title='Nie znaleziono zasobu | Biblioteka';
      title.textContent='Nie znaleziono zasobu';
      desc.textContent='Ten identyfikator nie występuje w katalogu. Sprawdź adres lub przejdź do biblioteki.';
      return;
    }
    document.title=entry.title+' | Biblioteka';
    title.textContent=entry.title;
    desc.textContent=entry.description || '';
    meta.append(metadata(entry));
    const src=resolveSource(entry.source);
    if (!src) return;
    const sameSite=src.href.startsWith(root.href);
    actions.append(link('Otwórz oryginał',src.href));
    if (sameSite) actions.append(link('Pobierz plik',src.href,entry.source.split('/').pop()));
    else actions.append(element('span','status','Zasób zewnętrzny. Pobieranie zależy od serwisu źródłowego.'));
    if (entry.type === 'p' || entry.type === 'h') {
      const frame=element('iframe','viewer');
      frame.src=src.href;
      frame.title='Podgląd: '+entry.title;
      frame.loading='lazy';
      frame.referrerPolicy='no-referrer';
      if (entry.type === 'h') frame.setAttribute('sandbox','allow-scripts');
      preview.append(frame);
      if (!sameSite) preview.append(element('p','status','Jeżeli serwis źródłowy blokuje osadzanie, użyj przycisku „Otwórz oryginał”.'));
    } else {
      preview.append(element('p','status','Ten format udostępniono do pobrania, bez podglądu osadzonego w przeglądarce.'));
    }
  }
  fetch(manifestUrl, {cache:'no-cache'})
    .then(response=>{if(!response.ok) throw new Error('HTTP '+response.status);return response.json()})
    .then(data=>{
      if (!data || !Array.isArray(data.entries)) throw new Error('Niepoprawny katalog');
      const keys = new Set();
      const entries = data.entries.filter(e=>{
        if (!valid(e) || keys.has(e.type+'/'+e.id)) return false;
        keys.add(e.type+'/'+e.id);
        return true;
      });
      if (main.dataset.library === 'catalog') renderCatalog(entries);
      if (main.dataset.library === 'reader') renderReader(entries);
    })
    .catch(()=>{
      const target=document.getElementById(main.dataset.library==='catalog'?'library-results':'resource-description');
      if (target) target.textContent='Nie udało się odczytać katalogu. Spróbuj ponownie lub otwórz plik źródłowy.';
    });
})();
