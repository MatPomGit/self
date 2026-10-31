"""Build MkDocs and retain public URLs of existing teaching materials."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-dir', type=Path, default=ROOT / 'site')
    args = parser.parse_args()
    target = args.site_dir.resolve()
    # MkDocs cleans its destination. Keep source trees out of that operation.
    if (target == ROOT or target in ROOT.parents or
            (target.is_relative_to(ROOT) and target != ROOT / 'site')):
        parser.error('Use site/ or a directory outside the repository.')
    subprocess.run([sys.executable, '-m', 'mkdocs', 'build', '--strict',
                    '--site-dir', str(target)], cwd=ROOT, check=True)
    for name in ('materials', 'docs'):
        shutil.copytree(ROOT / name, target / name, dirs_exist_ok=True)
    shutil.copy2(ROOT / 'index.html', target / 'legacy.html')
    (target / '.nojekyll').touch()
    print('[DONE] Polish and English site built; teaching URLs preserved.')


if __name__ == '__main__':
    main()
