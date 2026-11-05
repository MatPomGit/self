/* Bilingual labels for the original, wheel-based static homepage.
 * The Polish HTML remains the canonical markup and works without this file.
 */
(() => {
  'use strict';

  const language = new URLSearchParams(window.location.search).get('lang') === 'en' ? 'en' : 'pl';

  const english = {
    'dr inż. Mateusz Pomianek': 'Mateusz Pomianek, PhD, Eng.',
    'Politechnika Rzeszowska': 'Rzeszów University of Technology',
    'Informatyka afektywna i': 'Affective computing and',
    'robotyka humanoidalna': 'humanoid robotics',
    'W swojej działalności naukowej łączę informatykę z neuronauką, koncentrując się na badaniach i rozwoju inteligentnych systemów percepcji oraz interakcji człowiek–maszyna, a także na analizie ich wpływu na procesy poznawcze i zachowanie człowieka':
      'My research integrates computer science and neuroscience, focusing on intelligent perception and human–machine interaction systems and their effects on human cognition and behaviour.',
    'Adiunkt, Katedra Informatyki i Automatyki': 'Assistant Professor, Department of Computer and Control Engineering',
    'Badam i rozwijam inteligentne systemy percepcji, interakcji człowiek–maszyna oraz robotyki, łącząc informatykę z neuronauką.':
      'I research and develop intelligent systems for perception, human–machine interaction and robotics, combining computer science with neuroscience.',
    'Kontakt': 'Contact',
    'Kontakt i profile': 'Contact and profiles',
    'Adres': 'Address',
    'E-mail i telefon': 'Email and phone',
    'Profil uczelniany': 'University profile',
    'Dla': 'For',
    'studentów': 'students',
    'Dla studentów': 'For students',
    'Materiały i zajęcia': 'Materials and courses',
    'Materiały': 'Materials',
    'Materiały dydaktyczne': 'Teaching materials',
    'Zajęcia': 'Courses',
    'Konsultacje': 'Consultations',
    'Prace dyplomowe': 'Theses',
    'Projekty studenckie': 'Student projects',
    'Projekty': 'Projects',
    'Badania i rozwój': 'Research and development',
    'Wszystkie projekty': 'All projects',
    'Aktualne programy badawczo-rozwojowe': 'Current research and development programmes',
    'Wybrane projekty i konsorcja': 'Selected projects and consortia',
    'Publikacje': 'Publications',
    '/ Publikacje': '/ Publications',
    'Dorobek naukowy': 'Research outputs',
    'Wszystkie publikacje': 'All publications',
    'Czasopisma': 'Journal articles',
    'Konferencje': 'Conference papers',
    'Patenty': 'Patents',
    'Robocze': 'In progress',
    'Badania': 'Research',
    'Obszary naukowe': 'Research areas',
    'Informatyka afektywna': 'Affective computing',
    'Wizja komputerowa': 'Computer vision',
    'Śledzenie wzroku': 'Eye tracking',
    'Robotyka humanoidalna': 'Humanoid robotics',
    'Optoelektronika': 'Optoelectronics',
    'Wybierz': 'Choose a',
    'kategorię': 'category',
    'Instrukcje, prezentacje, ćwiczenia i materiały dodatkowe są dostępne na stronie uczelnianej oraz w repozytoriach przypisanych do konkretnych zajęć.':
      'Instructions, presentations, exercises and supplementary resources are available on the university website and in repositories assigned to individual courses.',
    'Sprawy dotyczące zajęć, projektów i zaliczeń najlepiej zgłaszać mailowo z krótkim opisem problemu.':
      'For questions about courses, projects or assessment, please send an email with a short description of the issue.',
    'Preferowane są tematy łączące programowanie, sztuczną inteligencję, analizę obrazu, HCI, HRI, neuroinformatykę i robotykę.':
      'Preferred thesis topics combine programming, artificial intelligence, image analysis, HCI, HRI, neuroinformatics and robotics.',
    'Liczy się działające rozwiązanie, czytelny kod, dokumentacja oraz możliwość odtworzenia wyników.':
      'Projects should include working software, readable code, documentation and reproducible results.',
    'Narzędzia dla programistów': 'Tools for programmers',
    'Terminal, Git, organizacja środowiska pracy i praktyki projektowe.':
      'Terminal, Git, development environments and project practices.',
    'Algorytmy i struktury danych': 'Algorithms and data structures',
    'Złożoność obliczeniowa, struktury danych i analiza rozwiązań.':
      'Computational complexity, data structures and analysis of solutions.',
    'Programowanie aplikacji mobilnych': 'Mobile application programming',
    'Projektowanie aplikacji, architektura, frontend i backend.':
      'Application design, architecture, frontend and backend.',
    'Analiza i przetwarzanie obrazów': 'Image analysis and processing',
    'Filtracja, segmentacja, morfologia i detekcja obiektów.':
      'Filtering, segmentation, morphology and object detection.',
    'Psychoinformatyka poznawczo afektywna': 'Cognitive and affective psychoinformatics',
    'Analiza zachowania, emocji i procesów poznawczych z użyciem metod informatycznych.':
      'Computational analysis of behaviour, emotions and cognitive processes.',
    'Robotyka afektywna': 'Affective robotics',
    'Interakcja człowiek robot, percepcja oraz kognitywne systemy robotyczne.':
      'Human–robot interaction, perception and cognitive robotic systems.',
    'Świat większy od nas': 'A world bigger than us',
    'Wiele sposobów widzenia': 'Many ways of seeing',
    'Świat, który tworzy mózg': 'The world our brains create',
    'Nad czym pracuję': 'What I work on',
    'Największą satysfakcję daje mi': 'What I enjoy most is',
    'chwila, gdy z ciekawości rodzi się pomysł, a z pomysłu coś, co pomaga nam lepiej rozumieć świat lub siebie nawzajem.':
      'the moment curiosity turns into an idea, and that idea into something that helps us understand the world or one another a little better.',
    'Wczytywanie projektów…': 'Loading projects…',
    'Wczytywanie publikacji…': 'Loading publications…',
    'Źródło:': 'Source:',
    'Wykaz projektów na stronie uczelnianej PRz': 'University project list',
    'Wszystkie': 'All',
    'Katedra Informatyki i Automatyki': 'Department of Computer and Control Engineering',
    'pokój D.103': 'Room D.103',
    'E mail': 'Email',
    'dr inż. Mateusz Pomianek · Politechnika Rzeszowska':
      'Mateusz Pomianek, PhD, Eng. · Rzeszów University of Technology',
    'Strona główna': 'Homepage',
    'Tryb ciemny': 'Dark mode',
    'Włącz tryb ciemny': 'Enable dark mode',
    'Włącz tryb jasny': 'Enable light mode',
    'Portret dr. inż. Mateusza Pomianka': 'Portrait of Mateusz Pomianek',
    'Kategorie strony': 'Website categories',
    'Informacje szczegółowe': 'Detailed information',
    'Filtruj publikacje': 'Filter publications',
    'Wersja strony 1.2.18': 'Website version 1.2.18',
    'Język strony': 'Site language',
    'Źródło': 'Source',
    'Skopiowano': 'Copied',
    'Nie można skopiować automatycznie. Sprawdź uprawnienia przeglądarki.':
      'Could not copy automatically. Check browser permissions.',
    'Nie udało się pobrać danych. Odśwież stronę, aby spróbować ponownie.':
      'Data could not be loaded. Reload the page to try again.',
    'Nieprawidłowy format danych': 'Invalid data format',
    'Brak manuskryptów': 'No manuscripts',
    'Postęp szacunkowy; czasopisma docelowe mogą ulec zmianie. Punktacja według wykazu 2024, jeśli zweryfikowana.':
      'Estimated progress; target journals may change. Ministerial points refer to the 2024 list where verified.',
    'Następny krok: ': 'Next step: ',
    'Docelowe czasopismo: ': 'Target journal: ',
    'pkt: do weryfikacji': 'points: pending verification',
    ' pkt': ' points',
    'Szacunkowy postęp: ': 'Estimated progress: ',
    'Nie udało się wczytać planowanych manuskryptów.': 'The planned manuscripts could not be loaded.',
    'Cite': 'Cite',
    'copy BibTeX': 'Copy BibTeX',
    'XR, HCI i HRI': 'XR, HCI and HRI',
    'tel. +48 17 865 14 81': 'phone +48 17 865 14 81',
  };

  const researchParagraphs = [
    'I have always been curious about the world itself: what happens right beside us and what unfolds far beyond Earth. When I think about the sheer scale of the universe, I am amazed that humans, so small in comparison, can even attempt to understand it. Astronomy keeps me humble, but it also makes me more curious.',
    'Building models of the world has always been a passion of mine. The same thing can be described in many ways; each reveals something, while simplifying or leaving something else out. I am not looking for one perfect picture of reality. I enjoy seeing what changes when we look from a different angle.',
    'I am also curious about how machines might perceive reality. Without our senses or experiences, what kind of picture of their surroundings would they build? What might they notice that we overlook, and what would remain invisible to them?',
    'And then I come back to people. Our brains do not show us the world directly; they build their own model from sensations, memories and expectations. Why can two people experience the same event so differently? How does their understanding of the world shape their choices, emotions and relationships?',
    'These questions are at the heart of my research. I bring experiments, programming and engineering together to explore how different pictures of the world take shape, and how machines might build their own. I am an Assistant Professor at Rzeszów University of Technology and earned my doctorate at the Military University of Technology.',
    'I started with optoelectronics, imaging and measurement systems. Over time, artificial intelligence became a natural next step: analysing images, combining sensor data and designing systems that can make sense of their surroundings. This led me to humanoid robots, autonomous systems, and virtual and augmented reality.',
    'But understanding how people see the world matters just as much to me. That is why I also explore neuroscience and psychology, studying attention, emotions and behaviour through eye tracking, EEG and experiments. I am especially curious about where these two perspectives meet: people and intelligent machines. What makes us trust one another? How can technology respond better to our needs?',
  ];

  // HTML &nbsp; becomes U+00A0 in text nodes. Match translations independently
  // of typographic whitespace, without changing the canonical Polish markup.
  function translate(text) {
    if (language !== 'en') return text;
    if (Object.prototype.hasOwnProperty.call(english, text)) return english[text];
    const normalized = text.replace(/\s+/gu, ' ').trim();
    return Object.prototype.hasOwnProperty.call(english, normalized) ? english[normalized] : text;
  }

  function apply() {
    document.documentElement.lang = language;
    document.querySelectorAll('.language-switch a').forEach(link => {
      const selected = link.hreflang === language;
      if (selected) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
      link.addEventListener('click', () => {
        link.href = '?lang=' + link.hreflang + window.location.hash;
      });
    });
    if (language !== 'en') return;

    const paragraphs = document.querySelectorAll('#badania .research-intro p, #badania .research-work p');
    if (paragraphs.length !== researchParagraphs.length) {
      throw new Error('Unexpected number of research paragraphs');
    }
    paragraphs.forEach((node, index) => { node.textContent = researchParagraphs[index]; });

    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.parentElement.closest('script, style')) continue;
      const original = node.nodeValue;
      const leading = original.match(/^\s*/u)[0];
      const trailing = original.match(/\s*$/u)[0];
      const content = original.slice(leading.length, original.length - trailing.length);
      const translated = translate(content);
      if (translated !== content) node.nodeValue = leading + translated + trailing;
    }
    document.querySelectorAll('[aria-label], [title], [alt]').forEach(element => {
      for (const attribute of ['aria-label', 'title', 'alt']) {
        if (element.hasAttribute(attribute)) {
          const text = element.getAttribute(attribute);
          const translated = translate(text);
          if (translated !== text) element.setAttribute(attribute, translated);
        }
      }
    });
    document.title = 'Mateusz Pomianek, PhD, Eng.';
    const description = document.querySelector('meta[name="description"]');
    if (description) description.content =
      'Academic website of Mateusz Pomianek. Research, projects, publications, teaching and contact.';
  }

  function translateProjects(originals, translations) {
    if (language !== 'en') return originals;
    if (!Array.isArray(translations)) throw new Error('Missing project translations');
    const mapped = new Map();
    for (const item of translations) {
      if (mapped.has(item.sourceTitle)) throw new Error('Duplicate project translation');
      mapped.set(item.sourceTitle, item);
    }
    if (mapped.size !== originals.length) throw new Error('Project translation count mismatch');
    return originals.map(original => {
      const translation = mapped.get(original.title);
      if (!translation || !translation.title || !translation.period || !translation.description) {
        throw new Error('Missing translation for project: ' + original.title);
      }
      return { ...original, title: translation.title, period: translation.period, description: translation.description };
    });
  }

  function translateManuscripts(originals, translations) {
    if (language !== 'en') return originals;
    if (!translations || Object.keys(translations).length !== originals.length) {
      throw new Error('Manuscript translation count mismatch');
    }
    return originals.map(original => {
      const translation = translations[original.id];
      if (!translation || !translation.description || !translation.nextStep) {
        throw new Error('Missing translation for manuscript: ' + original.id);
      }
      return { ...original, description: translation.description, nextStep: translation.nextStep };
    });
  }

  function publicationMetadata(metadata) {
    if (language !== 'en') return metadata;
    const months = {
      stycznia: 'January', lutego: 'February', marca: 'March',
      kwietnia: 'April', maja: 'May', czerwca: 'June',
      lipca: 'July', sierpnia: 'August', września: 'September',
      października: 'October', listopada: 'November', grudnia: 'December',
      'sty.': 'Jan.', 'lut.': 'Feb.', 'mar.': 'Mar.', 'kwi.': 'Apr.',
      'cze.': 'Jun.', 'lip.': 'Jul.', 'sie.': 'Aug.', 'wrz.': 'Sep.',
      'paź.': 'Oct.', 'lis.': 'Nov.', 'gru.': 'Dec.',
    };
    return metadata
      .replace(/\b(stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia|sty\.|lut\.|mar\.|kwi\.|cze\.|lip\.|sie\.|wrz\.|paź\.|lis\.|gru\.)/gu,
        month => months[month])
      .replace(/ pkt\b/gu, ' points')
      .replace(/\bt\.\s/g, 'vol. ')
      .replace(/\bnr\s/g, 'no. ')
      .replace(/\bs\.\s/g, 'pp. ');
  }

  window.SiteI18n = Object.freeze({
    language, translate, apply, translateProjects, translateManuscripts, publicationMetadata,
  });
})();
