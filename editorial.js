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
    try { localStorage.setItem('lang', document.documentElement.lang === 'en' ? 'ht' : 'en'); } catch (_) {}
  });
  const filters = document.querySelector('.editorial-filters');
  const cards = [...document.querySelectorAll('[data-editorial-kind]')];
  const count = document.querySelector('[data-count-pattern]');
  if (filters && cards.length && count) {
    filters.hidden = false;
    for (const button of filters.querySelectorAll('button')) {
      button.addEventListener('click', () => {
        const selected = button.dataset.editorialFilter;
        for (const card of cards) card.hidden = selected !== 'all' && card.dataset.editorialKind !== selected;
        for (const control of filters.querySelectorAll('button')) control.setAttribute('aria-pressed', String(control === button));
        count.textContent = count.dataset.countPattern.replace('{count}', String(cards.filter(card => !card.hidden).length));
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
