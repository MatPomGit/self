"""Build both Zensical languages and retain existing teaching URLs."""
import argparse
import copy
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import tomli_w

from site_data import render_page

ROOT = Path(__file__).resolve().parents[1]
ENGLISH_NAV = {
    'Strona główna': 'Home', 'Badania': 'Research', 'Projekty': 'Projects',
    'Publikacje': 'Publications', 'Dla studentów': 'Teaching', 'Kontakt': 'Contact',
}


def build_language(base, language, stage):
    """Prepare complete sources before invoking Zensical's public build command."""
    source = ROOT / 'website' / language
    documents = stage / language
    shutil.copytree(source, documents)
    shutil.copytree(ROOT / 'website/stylesheets', documents / 'stylesheets')
    for page in documents.rglob('*.md'):
        page.write_text(render_page(page.read_text(encoding='utf-8'), language),
                        encoding='utf-8')
    config = copy.deepcopy(base)
    project = config['project']
    project['docs_dir'] = language
    project['site_dir'] = 'site' if language == 'pl' else 'site/en'
    project['theme']['custom_dir'] = 'overrides'
    project['theme']['language'] = language
    if language == 'en':
        project['site_url'] += 'en/'
        project['site_description'] = 'Research, projects, publications and teaching'
        project['nav'] = [{ENGLISH_NAV[name]: path} for entry in project['nav']
                          for name, path in entry.items()]
        for palette, label in zip(project['theme']['palette'], ['Dark mode', 'Light mode']):
            palette['toggle']['name'] = label
    config_file = stage / f'{language}.toml'
    config_file.write_text(tomli_w.dumps(config), encoding='utf-8')
    print(f'[BUILD] Zensical: {language}', flush=True)
    subprocess.run([sys.executable, '-m', 'zensical', 'build', '--strict',
                    '--config-file', str(config_file)], cwd=stage, check=True)


def publish_site(output, target):
    """Complete a candidate site before replacing the previous result.

    Both directories reside on the same filesystem. A failed build or asset
    copy leaves the existing site intact; a failed final rename is rolled back.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.self-publish-', dir=target.parent) as temp:
        work = Path(temp)
        candidate = work / 'site'
        shutil.copytree(output, candidate)
        for name in ('materials', 'docs'):
            shutil.copytree(ROOT / name, candidate / name, dirs_exist_ok=True)
        shutil.copy2(ROOT / 'index.html', candidate / 'legacy.html')
        (candidate / '.nojekyll').touch()

        previous = work / 'previous-site'
        had_previous = target.exists()
        if had_previous:
            target.rename(previous)
        try:
            candidate.rename(target)
        except OSError:
            if had_previous:
                previous.rename(target)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-dir', type=Path, default=ROOT / 'site')
    args = parser.parse_args()
    target = args.site_dir.absolute()
    if (target.is_symlink() or target.name != 'site' or
            target == ROOT or target in ROOT.parents or
            (target.is_relative_to(ROOT) and target != ROOT / 'site')):
        parser.error('Choose site/ or an external directory named site.')
    if target.exists() and (not target.is_dir() or
                            not (target / '.nojekyll').is_file()):
        parser.error('Refusing to overwrite an unrecognised output directory.')
    base = tomllib.loads((ROOT / 'zensical.toml').read_text(encoding='utf-8'))
    polish = {p.relative_to(ROOT / 'website/pl') for p in (ROOT / 'website/pl').rglob('*.md')}
    english = {p.relative_to(ROOT / 'website/en') for p in (ROOT / 'website/en').rglob('*.md')}
    if polish != english:
        parser.error('Every page must exist in both Polish and English.')
    with tempfile.TemporaryDirectory(prefix='self-zensical-') as temp:
        stage = Path(temp)
        output = stage / 'site'
        shutil.copytree(ROOT / 'website/overrides', stage / 'overrides')
        for language in ('pl', 'en'):
            build_language(base, language, stage)
        publish_site(output, target)
    print('[DONE] Polish and English Zensical site built; teaching URLs preserved.')


if __name__ == '__main__':
    main()
