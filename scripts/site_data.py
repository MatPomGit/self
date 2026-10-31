"""Render shared portfolio data in both MkDocs languages."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs' / 'data'


def read_data(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def publications(english):
    labels = ({'journal': 'Journal articles', 'conference': 'Conference papers',
               'patent': 'Patents'} if english else
              {'journal': 'Czasopisma', 'conference': 'Konferencje', 'patent': 'Patenty'})
    sections = []
    for kind, label in labels.items():
        sections.append(f'## {label}\n')
        for entry in read_data('publications'):
            if entry['type'] != kind:
                continue
            metadata = entry['metadata']
            if english:
                for pl, en in [('marca', 'March'), ('stycznia', 'January'),
                               (' pkt', ' points'), ('t. ', 'vol. '),
                               ('nr ', 'no. '), ('s. ', 'pp. ')]:
                    metadata = metadata.replace(pl, en)
            title = escape(entry['title'])
            if entry['link']:
                title = f'<a href="{escape(entry["link"], quote=True)}">{title}</a>'
            sections.append(f'<article><h3>{title}</h3><p>{escape(entry["authors"])}</p>'
                            f'<p>{escape(str(entry["year"]))} · {escape(metadata)}</p></article>\n')
    sections.append('## Work in progress\n' if english else '## Prace w toku\n')
    statuses = {
        'Plan badań; walidacja i wyniki wymagają uzupełnienia':
            'Research plan; validation and results are incomplete',
        'HOLD: etap opcjonalny': 'HOLD: optional stage',
        'Manuskrypt i protokół; brak pełnej walidacji':
            'Manuscript and protocol; full validation is incomplete',
    }
    translations = read_data('in-progress.en') if english else {}
    for item in read_data('in-progress'):
        translated = translations[item['id']] if english else item
        status = statuses[item['status']] if english else item['status']
        journal = 'Target journal' if english else 'Czasopismo docelowe'
        confirmed = ('confirmed' if english else 'potwierdzone') if item['journalConfirmed'] else (
            'proposed' if english else 'proponowane')
        next_label = 'Next step' if english else 'Następny krok'
        points_label = 'Ministerial points' if english else 'Punkty ministerialne'
        points = item['ministerialPoints']
        points = str(points) if points is not None else ('unconfirmed' if english else 'niepotwierdzone')
        basis = ('2024 list (provisional verification; a list update is planned for 2027)'
                 if english else item['pointsBasis'])
        sections.append(
            f'<article><h3>{escape(item["title"])}</h3>'
            f'<p><a href="{escape(item["projectUrl"], quote=True)}">{escape(item["project"])}</a>'
            f' · {item["progress"]}% · {escape(status)}</p>'
            f'<p>{escape(translated["description"])}</p>'
            f'<p>{journal}: <a href="{escape(item["journalUrl"], quote=True)}">'
            f'{escape(item["journal"])}</a> ({confirmed})</p>'
            f'<p>{points_label}: {escape(points)} · {escape(basis)}</p>'
            f'<p>{next_label}: {escape(translated["nextStep"])}</p></article>\n'
        )
    return '\n'.join(sections)


def on_page_markdown(markdown, page, config, files):
    english = config.theme['language'] == 'en'
    if '<!-- projects -->' in markdown:
        entries = read_data('projects.en' if english else 'projects')
        content = '\n'.join(
            f'<article><h2>{escape(x["title"])}</h2><p>{escape(x["description"])}</p></article>\n'
            for x in entries
        )
        label = 'Source: university project list' if english else 'Źródło: wykaz projektów PRz'
        content += f'\n[{label}](https://mpomianek.v.prz.edu.pl/praca-naukowa/uczestnictwo-w-organizacjach-i-projektach)\n'
        return markdown.replace('<!-- projects -->', content)
    if '<!-- publications -->' in markdown:
        return markdown.replace('<!-- publications -->', publications(english))
    return markdown
