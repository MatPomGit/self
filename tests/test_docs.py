"""Built-site acceptance checks for bilingual navigation and teaching URLs."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
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


@unittest.skipUnless(importlib.util.find_spec('zensical'), 'Install requirements-docs.txt')
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
        source_titles = [entry['title'] for entry in projects]
        translation_keys = [entry['sourceTitle'] for entry in translations]
        self.assertEqual(len(source_titles), len(set(source_titles)))
        self.assertEqual(len(translation_keys), len(set(translation_keys)))
        self.assertEqual(set(source_titles), set(translation_keys))
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


class TranslationTests(unittest.TestCase):
    def test_translations_follow_sources_when_order_changes(self):
        from scripts import site_data

        originals = [{'title': 'A'}, {'title': 'B'}]
        translated = [{'sourceTitle': 'B', 'title': 'English B',
                       'description': 'Translation B'},
                      {'sourceTitle': 'A', 'title': 'English A',
                       'description': 'Translation A'}]
        with patch.object(site_data, 'read_data',
                          side_effect=lambda name: originals if name == 'projects' else translated):
            entries = site_data.project_entries(True)
        self.assertEqual([entry['title'] for entry in entries], ['English A', 'English B'])

    def test_missing_and_duplicate_translations_fail(self):
        from scripts import site_data

        originals = [{'title': 'A'}, {'title': 'B'}]
        cases = [
            [{'sourceTitle': 'A', 'title': 'English A'}],
            [{'sourceTitle': 'A', 'title': 'A1'}, {'sourceTitle': 'A', 'title': 'A2'}],
            [{'sourceTitle': 'A', 'title': 'A1'}, {'sourceTitle': 'C', 'title': 'C1'}],
        ]
        for translations in cases:
            with self.subTest(translations=translations):
                with patch.object(site_data, 'read_data',
                                  side_effect=lambda name: originals if name == 'projects'
                                  else translations):
                    with self.assertRaises(ValueError):
                        site_data.project_entries(True)


@unittest.skipUnless(importlib.util.find_spec('tomli_w'), 'Install requirements-docs.txt')
class SitePublicationTests(unittest.TestCase):
    def make_fixture(self, root):
        source = root / 'source'
        source.mkdir()
        (source / 'index.html').write_text('new home', encoding='utf-8')
        repository = root / 'repository'
        (repository / 'materials').mkdir(parents=True)
        (repository / 'docs').mkdir()
        (repository / 'materials' / 'handout.pdf').write_bytes(b'PDF test')
        (repository / 'docs' / 'metadata.json').write_text('{}', encoding='utf-8')
        (repository / 'index.html').write_text('original', encoding='utf-8')
        target = root / 'output' / 'site'
        target.mkdir(parents=True)
        (target / '.nojekyll').touch()
        (target / 'index.html').write_text('previous home', encoding='utf-8')
        return source, repository, target

    def test_complete_site_is_published(self):
        from scripts import build_site

        with tempfile.TemporaryDirectory() as temp:
            source, repository, target = self.make_fixture(Path(temp))
            with patch.object(build_site, 'ROOT', repository):
                build_site.publish_site(source, target)
            self.assertEqual((target / 'index.html').read_text(), 'new home')
            self.assertEqual((target / 'legacy.html').read_text(), 'original')
            self.assertEqual((target / 'materials/handout.pdf').read_bytes(), b'PDF test')
            self.assertEqual((target / 'docs/metadata.json').read_text(), '{}')
            self.assertTrue((target / '.nojekyll').is_file())

    def test_asset_copy_failure_keeps_previous_site(self):
        from scripts import build_site

        with tempfile.TemporaryDirectory() as temp:
            source, repository, target = self.make_fixture(Path(temp))
            original_copytree = shutil.copytree

            def failing_copytree(src, dst, **kwargs):
                if Path(src).name == 'docs':
                    raise OSError('Simulated asset copy failure')
                return original_copytree(src, dst, **kwargs)

            with patch.object(build_site, 'ROOT', repository), \\
                    patch.object(build_site.shutil, 'copytree', side_effect=failing_copytree):
                with self.assertRaisesRegex(OSError, 'Simulated asset copy failure'):
                    build_site.publish_site(source, target)
            self.assertEqual((target / 'index.html').read_text(), 'previous home')
            self.assertTrue((target / '.nojekyll').is_file())
