/* Bilingual labels for the original, wheel-based static homepage.
 * The Polish HTML remains the canonical markup and works without this file.
 */
(() => {
  'use strict';

  const language = new URLSearchParams(window.location.search).get('lang') === 'en' ? 'en' : 'pl';

  const english = {
    'dr inż. Mateusz Pomianek': 'Mateusz Pomianek, PhD Eng.',
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
    'Profil naukowy': 'Academic profile',
    'Kompetencje inżynierskie i systemy autonomiczne': 'Engineering and autonomous systems',
    'Robotyka afektywna i neuroinformatyka': 'Affective robotics and neuroinformatics',
    'Cel badań:': 'Research goal:',
    'budowa systemów, które nie tylko odbierają sygnały, ale też inteligentnie je interpretują i odpowiadają w sposób dostosowany do kontekstu.':
      'develop systems that perceive signals, intelligently interpret them and respond appropriately to their context.',
    'Wczytywanie projektów…': 'Loading projects…',
    'Wczytywanie publikacji…': 'Loading publications…',
    'Źródło:': 'Source:',
    'Wykaz projektów na stronie uczelnianej PRz': 'University project list',
    'Wszystkie': 'All',
    'Katedra Informatyki i Automatyki': 'Department of Computer and Control Engineering',
    'pokój D.103': 'Room D.103',
    'E mail': 'Email',
    'dr inż. Mateusz Pomianek · Politechnika Rzeszowska':
      'Mateusz Pomianek, PhD Eng. · Rzeszów University of Technology',
    'Strona główna': 'Homepage',
    'Tryb ciemny': 'Dark mode',
    'Włącz tryb ciemny': 'Enable dark mode',
    'Włącz tryb jasny': 'Enable light mode',
    'Portret dr. inż. Mateusza Pomianka': 'Portrait of Mateusz Pomianek',
    'Kategorie strony': 'Website categories',
    'Informacje szczegółowe': 'Detailed information',
    'Filtruj publikacje': 'Filter publications',
    'Wersja strony 1.2.11': 'Website version 1.2.11',
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
    'I am a researcher and engineer specialising in multispectral image processing and systems based on natural human–machine interaction. My work connects optoelectronics, digital technologies and cognitive psychology. I model and integrate human perceptual and affective signals to help machines interpret the user’s state.',
    'I work as an Assistant Professor at the Department of Computer and Control Engineering, Rzeszów University of Technology. My research disciplines include automation, electronics, electrical engineering and space technologies, as well as computer science. I received my doctorate in engineering and technical sciences at the Institute of Optoelectronics, Military University of Technology. I follow the European Charter for Researchers, with an emphasis on ethics, integrity and transparency.',
    'I develop multisensor systems that use computer vision, machine learning and data fusion to infer human and environmental states. I design and integrate systems for acquiring physiological parameters, including motion, gaze direction and facial expressions. This work uses 3D scanning, photogrammetry and spatial modelling.',
    'I also develop immersive augmented and virtual reality environments for natural multimodal human–machine interfaces. My experience in security technologies includes optoelectronic guidance systems, battlefield simulators and trainers, and real-time AR systems that support situational awareness. I combine perception with real-time control to develop robotic architectures for precise and safe human collaboration.',
    'Affective robotics and brain–computer interface signal analysis are central to my work. I study and integrate eye-tracking data, emotional expressions and EEG activity. These signals support adaptive perceptual and cognitive architectures for humanoid robots and embodied AI.',
    'I use these representations to personalise robot interactions and develop specialised diagnostic and clinical applications that support medical and rehabilitation processes. I build digital twins of autonomous systems and use reinforcement learning to improve their operation under complex real-world conditions and changing user needs.',
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

    const paragraphs = document.querySelectorAll('#badania .research-intro p');
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
    document.title = 'Mateusz Pomianek, PhD Eng.';
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
      if (!translation || !translation.title || !translation.description) {
        throw new Error('Missing translation for project: ' + original.title);
      }
      return { ...original, title: translation.title, description: translation.description };
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
