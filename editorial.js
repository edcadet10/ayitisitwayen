(function () {
  'use strict';
  const toggle = document.querySelector('.nav-toggle');
  const navigation = document.querySelector('.nav-links');
  const setMenu = open => {
    toggle?.setAttribute('aria-expanded', String(open));
    navigation?.classList.toggle('active', open);
  };
  toggle?.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && toggle?.getAttribute('aria-expanded') === 'true') {
      setMenu(false);
      toggle.focus();
    }
  });
  document.querySelector('.lang-switch')?.addEventListener('click', event => {
    if (location.hash) event.currentTarget.hash = location.hash;
    const lang = document.documentElement.lang === 'en' ? 'ht' : 'en';
    document.cookie = 'ayiti_lang=' + lang + '; Max-Age=31536000; Path=/; SameSite=Lax; Secure';
    try { localStorage.setItem('lang', lang); } catch (_) {}
  });
  const tools = document.querySelector('.editorial-tools');
  const filters = document.querySelector('.editorial-filters');
  const cards = [...document.querySelectorAll('[data-editorial-kind]')];
  const count = document.querySelector('[data-count-pattern]');
  if (tools && filters && cards.length && count) {
    tools.hidden = false;
    const search = document.getElementById('editorial-search');
    const candidate = document.getElementById('editorial-candidate');
    const empty = document.querySelector('.editorial-empty');
    const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
    let selected = 'all';
    const apply = () => {
      const words = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
      for (const card of cards) {
        const text = normalize(card.dataset.editorialSearch);
        card.hidden = (selected !== 'all' && card.dataset.editorialKind !== selected)
          || (candidate.value && !card.dataset.editorialCandidates.split(' ').includes(candidate.value))
          || !words.every(word => text.includes(word));
      }
      const visible = cards.filter(card => !card.hidden).length;
      count.textContent = count.dataset.countPattern.replace('{count}', String(visible));
      if (empty) empty.hidden = visible !== 0;
    };
    search.addEventListener('input', apply);
    candidate.addEventListener('change', apply);
    for (const button of filters.querySelectorAll('button')) {
      button.addEventListener('click', () => {
        selected = button.dataset.editorialFilter;
        for (const control of filters.querySelectorAll('button')) control.setAttribute('aria-pressed', String(control === button));
        apply();
      });
    }
  }
  const form = document.getElementById('editorial-contact-form');
  form?.addEventListener('submit', event => {
    event.preventDefault();
    const values = new FormData(form);
    const name = String(values.get('name') || '');
    const email = String(values.get('email') || '');
    const message = String(values.get('message') || '');
    const subject = (document.documentElement.lang === 'ht' ? 'Mesaj sou' : 'Message about') + ' Ayiti Sitwayen — ' + name;
    location.href = 'mailto:contact@ayitisitwayen.org?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(message + '\n\n— ' + name + ' <' + email + '>');
  });
})();
