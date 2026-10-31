"""Built-site acceptance checks for bilingual navigation and teaching URLs."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.lang = None
        self.links = []
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.lang = attrs.get('lang')
        if tag == 'a':
            self.links.append(attrs)


@unittest.skipUnless(importlib.util.find_spec('mkdocs'), 'Install requirements-docs.txt')
class DocsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.site = Path(cls.temp.name) / 'site'
        subprocess.run([sys.executable, 'scripts/build_site.py', '--site-dir', str(cls.site)],
                       cwd=ROOT, check=True, capture_output=True, text=True)

    def test_page_language_switch_preserves_section(self):
        for language, prefix in [('pl', ''), ('en', 'en/')]:
            for slug in ['', 'research/', 'projects/', 'publications/', 'teaching/', 'contact/']:
                with self.subTest(language=language, slug=slug):
                    page = Page(self.site / prefix / slug / 'index.html')
                    self.assertEqual(page.lang, language)
                    links = {a['hreflang']: urljoin('/self/' + prefix + slug, a['href'])
                             for a in page.links if 'md-select__link' in a.get('class', '')}
                    self.assertEqual(links, {'pl': '/self/' + slug, 'en': '/self/en/' + slug})

    def test_translated_portfolio_is_complete(self):
        projects = json.loads((ROOT / 'docs/data/projects.json').read_text())
        translations = json.loads((ROOT / 'docs/data/projects.en.json').read_text())
        self.assertEqual(len(projects), len(translations))
        progress = json.loads((ROOT / 'docs/data/in-progress.json').read_text())
        translated = json.loads((ROOT / 'docs/data/in-progress.en.json').read_text())
        self.assertEqual({entry['id'] for entry in progress}, set(translated))
        for entry in translated.values():
            self.assertTrue(entry['description'].strip())
            self.assertTrue(entry['nextStep'].strip())
        for prefix in ['', 'en/']:
            html = (self.site / prefix / 'publications/index.html').read_text()
            self.assertEqual(html.count('<article>'),
                             len(json.loads((ROOT / 'docs/data/publications.json').read_text())) + len(progress))
        english = (self.site / 'en/publications/index.html').read_text()
        self.assertIn('Research plan; validation and results are incomplete', english)
        self.assertNotIn('Następny krok', english)

    def test_public_material_files_preserved_byte_for_byte(self):
        for source in (ROOT / 'materials').rglob('*'):
            if source.is_file():
                self.assertEqual(source.read_bytes(), (self.site / source.relative_to(ROOT)).read_bytes())
        self.assertEqual((ROOT / 'index.html').read_bytes(), (self.site / 'legacy.html').read_bytes())

    def test_local_links_in_built_pages_resolve(self):
        for prefix in ['', 'en/']:
            for slug in ['', 'research/', 'projects/', 'publications/', 'teaching/', 'contact/']:
                page = Page(self.site / prefix / slug / 'index.html')
                for link in page.links:
                    href = link.get('href', '')
                    parsed = urlsplit(href)
                    if parsed.scheme or parsed.netloc or not parsed.path:
                        continue
                    url = urljoin('/self/' + prefix + slug, parsed.path)
                    self.assertTrue(url.startswith('/self/'), url)
                    target = self.site / unquote(url.removeprefix('/self/'))
                    if target.is_dir():
                        target /= 'index.html'
                    self.assertTrue(target.is_file(), url)
