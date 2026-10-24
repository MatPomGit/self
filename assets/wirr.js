/* Statuses are read from the same local public manifest as the library. */
(() => {
  'use strict';
  const script = document.currentScript;
  const manifest = new URL('../assets/library.json', script.src);
  const tags = [...document.querySelectorAll('[data-resource-status]')];
  if (!tags.length) return;
  fetch(manifest, { cache: 'no-cache' })
    .then(response => { if (!response.ok) throw new Error('Cannot load manifest'); return response.json(); })
    .then(data => {
      if (!data || !Array.isArray(data.entries)) return;
      const entries = new Map(data.entries.map(e => [e.type + '/' + e.id, e]));
      for (const tag of tags) {
        const entry = entries.get(tag.dataset.resourceStatus);
        if (!entry) continue;
        const status = entry.status || 'ready';
        tag.textContent = status === 'planned' ? 'Oczekuje na plik'
          : status === 'draft' ? 'Szkic' : 'Opublikowano';
        tag.className = status === 'planned' ? 'pending' : status === 'draft' ? 'draft' : 'ready';
      }
    }).catch(() => { /* Initial status remains visible on network errors. */ });
})();
