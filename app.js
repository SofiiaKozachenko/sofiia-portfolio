(() => {
  'use strict';
  const defaultProjects = [...(window.PORTFOLIO_PROJECTS || []), ...(window.EXTRA_PROJECTS || [])];
  let projects = [...defaultProjects];
  const safeStorage = {getItem(key){try{return window.localStorage.getItem(key)}catch{return null}},setItem(key,val){try{window.localStorage.setItem(key,val)}catch{}}};
  let lang = safeStorage.getItem('sk_portfolio_lang') === 'ua' ? 'ua' : 'en';
  const $ = s => document.querySelector(s);
  const escapeHtml = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const theme = {
    violet: ['#7f69c5', '#f1eeff'], peach: ['#d6bdb1', '#593d3c'],
    lime: ['#bde469', '#26350f'], brown: ['#8c634c', '#fbf3e8'], blue: ['#a5beeb', '#1c329e']
  };
  const translations = {
    en: {
      availability:'AVAILABLE FOR PROJECTS',navWork:'WORK <sup>05</sup>',navAbout:'ABOUT',navContact:'CONTACT',
      introTag:'LET ME INTRODUCE MYSELF',heroIntro:'I make',heroAccent:'ideas',heroEnd:'look impossible to ignore.',
      heroNote:'GRAPHIC DESIGN, BRANDING<br>& A LITTLE BIT OF MAGIC.',explore:'EXPLORE',
      selectedProjects:'SELECTED PROJECTS',workTitle:'Selected <i>work<span class="work-asterisk">*</span></i>',
      workSubtitle:"A collection of things I've made, imagined, shaped, and occasionally obsessed over.",
      behanceMore:'LET’S CREATE SOMETHING ↗',aboutTag:'THE HUMAN BEHIND THE PIXELS',
      aboutTitleOne:'Not just',aboutTitleTwo:'pretty',aboutTitleThree:'pictures.',
      aboutLead:"I'm Sofiia, a graphic designer who loves turning complex ideas into bold, meaningful visual worlds.",
      aboutText:"I work at the intersection of visual identity, brand storytelling, digital design and experimentation. I believe the best design does more than catch the eye — it gives an idea its own voice.",
      factOne:'CREATING VISUAL<br>IDENTITIES',factTwo:'COMPUTER SCIENCE<br>+ DESIGN',factThree:'CURIOUS, STRATEGIC<br>& A BIT BOLD',
      contactTag:"LET'S MAKE SOMETHING",contactTitleOne:'GOT A',contactTitleTwo:'wild',contactTitleThree:'IDEA?',
      contactText:"Let's make it real. A good project usually starts with a simple hello.",sayHello:'SAY HELLO',
      projectIndex:'PROJECT',caseAbout:'The idea behind it.',viewBehance:'EXPLORE FULL CASE ON BEHANCE',nextProject:'NEXT PROJECT',back:'← BACK TO PORTFOLIO',
      journeyNumber:"MY JOURNEY / 2024—2026",
      journeyTitle:"Experience<span class=\"resume-spark\">✳</span>",
      journeyIntro:"I have worked with a design studio, a retail marketing team, an advertising agency and a coffee shop. Each setting shaped how I approach visual communication.",
      experienceHeading:"WORK EXPERIENCE",
      roleAxioma:"Graphic designer and SMM designer at Axioma design studio.",
      roleTada:"Graphic designer in the marketing department of the Ta-Da! retail network.",
      roleLmg:"Graphic designer at LMG Agency (medicine and cosmetology).",
      roleCafeTitle:"Coffee shop",
      roleCafe:"SMM and graphic designer for a coffee shop.",
      expertiseHeading:"WHAT I DO",
      skillBrand:"Identity & branding",
      skillBrandText:"Logos, visual identities, color and typography systems, brand guidelines and brandbooks.",
      skillMarketing:"Marketing & print",
      skillMarketingText:"Social media design, packaging, POS materials, advertising and print-ready layouts.",
      skillUi:"Digital & UI/UX",
      skillUiText:"Website interfaces, information architecture, wireframes, low- and high-fidelity prototypes.",
      skillAi:"AI & creative tools",
      skillAiText:"AI tools in the creative process (Midjourney, DALL·E, Freepik AI, Nano Banana) and basic video editing.",
      educationHeading:"EDUCATION & TRAINING",
      eduKarazin:"V. N. Karazin Kharkiv National University",
      eduKarazinDegree:"Computer Science · Bachelor's",
      eduKnu:"Taras Shevchenko National University of Kyiv",
      eduKnuDegree:"Computer Science · Master's",
      eduProjector:"Graphic Design · 2024–2025",
      eduDesignly:"UI/UX Design · 2023"
    },
    ua: {
      availability:'ВІДКРИТА ДО ПРОЄКТІВ',navWork:'ПРОЄКТИ <sup>05</sup>',navAbout:'ПРО МЕНЕ',navContact:'КОНТАКТИ',
      introTag:'НУ ЩО, ЗНАЙОМИТИСЬ?',heroIntro:'Перетворюю',heroAccent:'ідеї',heroEnd:'на візуал, який помічають.',
      heroNote:'ГРАФІЧНИЙ ДИЗАЙН, АЙДЕНТИКА<br>І ТРІШКИ МАГІЇ.',explore:'ДИВИТИСЬ',
      selectedProjects:'ОБРАНІ ПРОЄКТИ',workTitle:'Мої <i>роботи<span class="work-asterisk">*</span></i>',
      workSubtitle:'Колекція речей, які я придумувала, створювала та іноді надто ретельно доводила до ідеалу.',
      behanceMore:'СТВОРИМО ЩОСЬ РАЗОМ ↗',aboutTag:'ЛЮДИНА ЗА ПІКСЕЛЯМИ',
      aboutTitleOne:'Не просто',aboutTitleTwo:'гарні',aboutTitleThree:'картинки.',
      aboutLead:'Я Софія, графічна дизайнерка, яка любить перетворювати складні ідеї на сміливі візуальні світи.',
      aboutText:'Працюю з айдентикою, візуальними історіями брендів, цифровим дизайном та експериментами. Вірю, що хороший дизайн не лише привертає увагу, а й дає ідеї власний голос.',
      factOne:'СТВОРЮЮ ВІЗУАЛЬНІ<br>ІДЕНТИЧНОСТІ',factTwo:'КОМПʼЮТЕРНІ НАУКИ<br>+ ДИЗАЙН',factThree:'ДОПИТЛИВА, СТРАТЕГІЧНА<br>І ТРОХИ СМІЛИВА',
      contactTag:'СТВОРИМО ЩОСЬ РАЗОМ',contactTitleOne:'МАЄШ',contactTitleTwo:'сміливу',contactTitleThree:'ІДЕЮ?',
      contactText:'Давай втілимо її в життя. Класний проєкт часто починається з простого «привіт».',sayHello:'НАПИСАТИ',
      projectIndex:'ПРОЄКТ',caseAbout:'Ідея за проєктом.',viewBehance:'ПЕРЕГЛЯНУТИ КЕЙС НА BEHANCE',nextProject:'НАСТУПНИЙ ПРОЄКТ',back:'← НАЗАД ДО ПОРТФОЛІО',
      journeyNumber:"МІЙ ШЛЯХ / 2024—2026",
      journeyTitle:"Досвід<span class=\"resume-spark\">✳</span>",
      journeyIntro:"Працювала в дизайн-студії, маркетинговій команді рітейл-мережі, рекламній агенції та кавʼярні. Різні формати роботи допомогли сформувати системний підхід до візуальної комунікації.",
      experienceHeading:"ДОСВІД РОБОТИ",
      roleAxioma:"Графічна дизайнерка та SMM у дизайн-студії Axioma.",
      roleTada:"Графічна дизайнерка маркетингового департаменту рітейл-мережі Ta-Da!.",
      roleLmg:"Графічна дизайнерка LMG Agency (напрям: медицина та косметологія).",
      roleCafeTitle:"Кавʼярня",
      roleCafe:"SMM та графічна дизайнерка кавʼярні.",
      expertiseHeading:"ЧИМ ЗАЙМАЮСЬ",
      skillBrand:"Айдентика та брендинг",
      skillBrandText:"Логотипи, візуальна ідентичність, колірні й типографічні системи, гайдбуки та брендбуки.",
      skillMarketing:"Маркетинг і друк",
      skillMarketingText:"Дизайн для соцмереж, пакування, POS-матеріали, реклама й підготовка макетів до друку.",
      skillUi:"Digital та UI/UX",
      skillUiText:"Інтерфейси сайтів, інформаційна архітектура, вайрфрейми, Low-fi та High-fi прототипи.",
      skillAi:"ШІ та креативні інструменти",
      skillAiText:"ШІ у творчому процесі (Midjourney, DALL·E, Freepik AI, Nano Banana), базовий монтаж відео.",
      educationHeading:"ОСВІТА ТА НАВЧАННЯ",
      eduKarazin:"ХНУ імені В. Н. Каразіна",
      eduKarazinDegree:"Компʼютерні науки · бакалавр",
      eduKnu:"КНУ імені Т. Г. Шевченка",
      eduKnuDegree:"Компʼютерні науки · магістр",
      eduProjector:"Графічний дизайн · 2024–2025",
      eduDesignly:"UI/UX-дизайн · 2023"
    }
  };
  const t = key => translations[lang][key] || key;

  function applyLanguage() {
    document.documentElement.lang = lang === 'ua' ? 'uk' : 'en';
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const val = translations[lang][el.dataset.i18n];
      if (val) el.innerHTML = val;
    });
    $('#languageToggle').innerHTML = lang === 'en' ? 'UA <span>↗</span>' : 'EN <span>↗</span>';
    const workNav=document.querySelector('.nav [data-i18n="navWork"]');
    if(workNav)workNav.innerHTML=(lang==='ua'?'ПРОЄКТИ':'WORK')+` <sup>${String(projects.length).padStart(2,'0')}</sup>`;
    document.querySelectorAll('.filter').forEach(button => {
      const name = button.dataset.filter;
      const labels = lang === 'ua' ? {all:'УСІ',branding:'АЙДЕНТИКА',digital:'DIGITAL',packaging:'ПАКОВАННЯ'} : {all:'ALL',branding:'BRANDING',digital:'DIGITAL',packaging:'PACKAGING'};
      button.innerHTML = labels[name] + (name === 'all' ? ` <span>(${String(projects.length).padStart(2, '0')})</span>` : '');
    });
    renderProjects();
    const active = new URLSearchParams(location.search).get('case');
    if(active) renderCase(active, false);
  }

  function coverHTML(project) {
    const colors = theme[project.palette] || theme.blue;
    const original404 = project.image ? project.image.replace('/projects/808/','/projects/404/') : '';
    const localCover = (window.BEHANCE_IMPORTS || {})[project.slug]?.cover || `assets/covers/${project.slug}.webp`;
    const thumb = `<img class="project-image" src="${escapeHtml(localCover)}" alt="${escapeHtml(project.title)} — original Behance cover" loading="lazy" decoding="async" data-remote-large="${escapeHtml(project.image || '')}" data-remote-small="${escapeHtml(original404)}" onerror="if(!this.dataset.triedLarge){this.dataset.triedLarge='1';this.src=this.dataset.remoteLarge;return}if(!this.dataset.triedSmall){this.dataset.triedSmall='1';this.src=this.dataset.remoteSmall;return}this.closest('.project-cover').classList.add('cover-failed');this.style.display='none'">`;
    return `<div class="project-cover" style="--card-color:${colors[0]};--card-ink:${colors[1]}">
      <div class="project-graphic" aria-hidden="true"><strong>${escapeHtml(project.title)}</strong></div>
      ${thumb}</div>`;
  }

  function renderProjects() {
    const grid = $('#projectGrid');
    if (!grid) return;
    grid.innerHTML = projects.map((p, i) => `<article class="project-card" data-category="${escapeHtml(p.category)}"><a href="?case=${encodeURIComponent(p.slug)}" class="project-open" data-slug="${escapeHtml(p.slug)}" aria-label="Open ${escapeHtml(p.title)} case study">
      ${coverHTML(p)}<div class="project-info"><div><h3>${escapeHtml(p.title)}</h3></div><span class="project-year">${String(i + 1).padStart(2, '0')} / ${escapeHtml(p.year)}</span></div></a></article>`).join('');
    const active = document.querySelector('.filter.active')?.dataset.filter || 'all';
    filterProjects(active);
  }
  function filterProjects(filter) {
    document.querySelectorAll('.project-card').forEach(card => card.hidden = filter !== 'all' && card.dataset.category !== filter);
    document.querySelectorAll('.filter').forEach(btn => {
      btn.classList.toggle('active',btn.dataset.filter === filter);
      btn.setAttribute('aria-pressed', String(btn.dataset.filter === filter));
    });
  }
  let returnScroll = 0;
  let activeCaseObserver=null;
  function renderCase(slug, updateHistory = true) {
    const p = projects.find(item => item.slug === slug);
    if(!p) { if(updateHistory) location.href=location.pathname; return; }
    const idx=projects.indexOf(p),next=projects[(idx+1)%projects.length];
    const localized=lang==='ua';
    const labels=localized ? {
      back:'НАЗАД ДО ПОРТФОЛІО',next:'НАСТУПНИЙ КЕЙС',source:'ОРИГІНАЛЬНИЙ КЕЙС',
      awaiting:'Презентація тимчасово недоступна',
      note:'Повна презентація завантажується автоматично під час публікації сайту. Якщо синхронізація тимчасово недоступна, попередня успішна версія лишається опублікованою.',
      sourceLink:'ОРИГІНАЛ НА BEHANCE'
    } : {
      back:'BACK TO PORTFOLIO',next:'NEXT PROJECT',source:'ORIGINAL CASE STUDY',
      awaiting:'Presentation temporarily unavailable',
      note:'The complete gallery is automatically synchronized during site publishing. If synchronization fails, the last successfully published site stays online.',
      sourceLink:'ORIGINAL ON BEHANCE'
    };
    if(updateHistory){returnScroll=window.scrollY;try{history.pushState({case:slug},'',`?case=${encodeURIComponent(slug)}`);}catch{}}
    if(activeCaseObserver){activeCaseObserver.disconnect();activeCaseObserver=null;}
    const exported=(window.BEHANCE_IMPORTS||{})[slug];
    const prepared=(window.PORTFOLIO_CASE_PAGES||{})[slug];
    const uploaded=Array.isArray(p.presentationImages)?p.presentationImages.filter(x=>x?.url):[];
    const caseTitle=escapeHtml(p.title);
    let original='';
    if(prepared?.html) {
      // Native HTML avoids one oversized iframe viewport (which eagerly loaded all media).
      // All visible case blocks retain their original Behance sequence and proportions.
      const bg=/^#[0-9a-fA-F]{3,8}$/.test(prepared.background||'') ? prepared.background : '#ffffff';
      original=`<section class="case-native-gallery" style="--native-bg:${bg}">${prepared.html}</section>`;
    } else if(prepared?.tiles?.length) {
      original=prepared.tiles.map((f,i)=>`<figure class="original-case-image"><img src="${escapeHtml(f.local)}" alt="${caseTitle} / ${i+1}" loading="${i===0?'eager':'lazy'}" decoding="async"></figure>`).join('');
    } else if(uploaded.length) {
      original=uploaded.map((f,i)=>`<figure class="original-case-image"><img src="${escapeHtml(f.url)}" alt="${escapeHtml(f.alt||p.title)}" loading="${i===0?'eager':'lazy'}" decoding="async"></figure>`).join('');
    } else {
      const cover=exported?.cover||p.image||'';
      original=`<section class="case-awaiting">
        <div><span class="mono case-awaiting-tag">✳ ${labels.source}</span>
          <h2>${labels.awaiting}</h2><p>${labels.note}</p>
          <div class="case-awaiting-actions"><a href="${escapeHtml(p.behance||'#')}" target="_blank" rel="noopener noreferrer">${labels.sourceLink} ↗</a></div>
        </div><div class="case-awaiting-visual" style="--await-bg:${(theme[p.palette]||theme.blue)[0]};--await-fg:${(theme[p.palette]||theme.blue)[1]}"><strong>${caseTitle}</strong>${cover?`<img src="${escapeHtml(cover)}" alt="${caseTitle} — original cover" loading="eager" onerror="this.remove()" />`:''}</div></section>`;
    }
    const root=$('#caseView');
    root.innerHTML=`<div class="case-page original-case-page">
      <header class="case-topbar"><a class="brand" href="${location.pathname||'./'}" data-action="back">SK<span class="brand-spark">✳</span></a><span class="case-topbar-label mono">${caseTitle} / ${labels.source}</span><div class="case-topbar-buttons"><button class="case-lang" data-action="case-language">${localized?'EN':'UA'} ↗</button><button class="case-back" data-action="back">← ${labels.back}</button></div></header>
      <main class="original-case-main">${original}</main>
      <button class="next-project" data-next="${escapeHtml(next.slug)}"><div><span class="mono">${labels.next} / ${String((idx+1)%projects.length+1).padStart(2,'0')}</span><h2>${escapeHtml(next.title)}</h2></div><span class="next-arrow">↗</span></button>
      <footer class="case-footer"><span>© SOFIIA KOZACHENKO 2026</span><button data-action="back">← ${labels.back}</button><span>DESIGNED WITH CURIOSITY ✳</span></footer>
    </div>`;
    root.hidden=false;document.body.style.overflow='hidden';root.scrollTop=0;
    document.title=`${p.title} — Sofiia Kozachenko`;
    $('#mainShell').setAttribute('aria-hidden','true');
    // Responsive images use native lazy loading. The gallery no longer has an iframe.

  }

  function closeCase(updateHistory = true) {
    const root = $('#caseView');
    if (root.hidden) return;
    if(activeCaseObserver){activeCaseObserver.disconnect();activeCaseObserver=null;}
    if (updateHistory) try{ history.pushState({}, '', location.pathname + location.hash); }catch{}
    root.hidden = true;
    root.innerHTML = '';
    document.body.style.overflow = '';
    document.title = 'Sofiia Kozachenko® — Independent Graphic Designer';
    $('#mainShell').removeAttribute('aria-hidden');
    window.scrollTo(0, returnScroll);
  }
  function syncFromURL() {
    const slug = new URLSearchParams(location.search).get('case');
    if(slug) renderCase(slug, false); else closeCase(false);
  }
  document.addEventListener('click', e => {
    const trigger = e.target.closest('.project-open');
    if(trigger) {e.preventDefault();renderCase(trigger.dataset.slug);return;}
    const caseLang = e.target.closest('[data-action="case-language"]');
    if (caseLang) {lang=lang==='en'?'ua':'en';safeStorage.setItem('sk_portfolio_lang',lang);applyLanguage();return;}
    const zoom = e.target.closest('a[data-zoom]');
    if(zoom) {
      e.preventDefault();
      const caseRoot=$('#caseView');
      if(!caseRoot || caseRoot.hidden) return;
      const overlay=document.createElement('div');
      overlay.className='portfolio-image-lightbox';
      overlay.setAttribute('role','dialog');
      overlay.setAttribute('aria-label',lang==='ua'?'Оригінал зображення':'Full-resolution image');
      overlay.innerHTML=`<button type="button" aria-label="Close image">×</button><img alt="" loading="eager" decoding="async">`;
      overlay.querySelector('img').src=zoom.getAttribute('href');
      caseRoot.append(overlay);
      overlay.querySelector('button').focus();
      return;
    }
    const lightbox=e.target.closest('.portfolio-image-lightbox');
    if(lightbox && (e.target===lightbox || e.target.closest('button'))) {
      e.preventDefault();lightbox.remove();return;
    }
    const back = e.target.closest('[data-action="back"]');
    if(back){e.preventDefault();closeCase();return;}
    const next = e.target.closest('[data-next]');
    if(next){renderCase(next.dataset.next);return;}
    const filter = e.target.closest('[data-filter]');
    if(filter) filterProjects(filter.dataset.filter);
  });
  $('#languageToggle').addEventListener('click', () => {
    lang = lang === 'en' ? 'ua' : 'en';
    safeStorage.setItem('sk_portfolio_lang',lang);
    applyLanguage();
  });
  $('#backToTop').addEventListener('click',() => window.scrollTo({top:0,behavior:'smooth'}));
  document.addEventListener('keydown',e => {if(e.key === 'Escape'){const z=document.querySelector('.portfolio-image-lightbox');if(z){z.remove();e.preventDefault();return;}closeCase();}});
  window.addEventListener('popstate',syncFromURL);
  let ticking = false;
  function onScroll(){if(ticking)return;ticking=true;requestAnimationFrame(()=>{
    const max = Math.max(1,document.documentElement.scrollHeight-innerHeight);
    $('#scrollProgress').style.width = (window.scrollY/max*100)+'%';
    ticking=false;
  });}
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(!reduceMotion && window.matchMedia('(pointer:fine)').matches) {
    const spot = $('#cursorSpot'), art = $('#heroArt');
    window.addEventListener('pointermove',e=>{
      spot.style.left=e.clientX+'px';spot.style.top=e.clientY+'px';spot.style.opacity='.7';
      if(window.scrollY < 900 && art) {
        const x=(e.clientX/innerWidth-.5)*24, y=(e.clientY/innerHeight-.5)*17;
        art.style.transform=`translate(${x}px,${y}px)`;
      }
    },{passive:true});
    document.addEventListener('pointerover',e=>{const active=e.target.closest('a,button');spot.style.width=active?'48px':'32px';spot.style.height=active?'48px':'32px';});
  }
  // Optional read-only Sanity CMS feed. Configure content/sanity-config.js after creating a Sanity project.
  async function loadPublishedSanityProjects(){
    const cfg = window.SANITY_CONFIG;
    if(!cfg?.projectId || !cfg?.dataset) return;
    const query = encodeURIComponent('*[_type == "portfolioProject" && defined(slug.current)] | order(orderRank asc, _createdAt desc){"slug": slug.current, title, subtitle, category, type, year, palette, short, shortUa, description, descriptionUa, "image": cover.asset->url, "behance": behanceUrl, "gallery": gallery[]{"url": asset->url, alt, caption}, "presentationImages": presentationImages[]{"url": asset->url, alt}, figmaFileKey, figmaFrames[]{nodeId, width, height, name}, caseStudy}');
    const url = `https://${encodeURIComponent(cfg.projectId)}.api.sanity.io/v2025-02-19/data/query/${encodeURIComponent(cfg.dataset)}?query=${query}`;
    try{const response=await fetch(url);if(!response.ok)throw new Error('CMS fetch failed');const data=await response.json();if(Array.isArray(data.result)&&data.result.length){projects=data.result;applyLanguage();syncFromURL();}}catch(err){console.warn('Using bundled portfolio projects; CMS not connected:',err.message);}
  }
  applyLanguage();syncFromURL();loadPublishedSanityProjects();
})();
