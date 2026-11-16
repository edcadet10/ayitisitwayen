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
    if (document.querySelector('[data-comparison-tool]')) event.currentTarget.search = location.search;
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
  const comparisonTool = document.querySelector('[data-comparison-tool]');
  if (comparisonTool) {
    const first = document.getElementById('compare-first');
    const second = document.getElementById('compare-second');
    const status = comparisonTool.querySelector('[data-comparison-status]');
    const rows = [...document.querySelectorAll('[data-comparison-pair]')];
    const pairs = new Map(rows.map(row => [row.dataset.comparisonPair.split(' ').sort().join(' '), row.querySelector('a').getAttribute('href')]));
    const params = new URLSearchParams(location.search);
    for (const [key, control] of [['first', first], ['second', second]]) {
      const value = params.get(key) || '';
      if ([...control.options].some(option => option.value === value)) control.value = value;
    }
    let destination;
    const apply = () => {
      destination = undefined;
      const selected = [first.value, second.value].filter(Boolean);
      for (const row of rows) row.hidden = !selected.every(id => row.dataset.comparisonPair.split(' ').includes(id));
      for (const row of document.querySelectorAll('[data-comparison-person]')) row.hidden = selected.length > 0 && !selected.includes(row.dataset.comparisonPerson);
      if (selected.length < 2) status.textContent = '';
      else if (first.value === second.value) status.textContent = comparisonTool.dataset.same;
      else {
        destination = pairs.get(selected.sort().join(' '));
        status.textContent = destination ? comparisonTool.dataset.ready : comparisonTool.dataset.pending;
      }
      const query = new URLSearchParams();
      if (first.value) query.set('first', first.value);
      if (second.value) query.set('second', second.value);
      history.replaceState(null, '', location.pathname + (query.size ? '?' + query : '') + location.hash);
    };
    first.addEventListener('change', apply);
    second.addEventListener('change', apply);
    comparisonTool.addEventListener('submit', event => {
      event.preventDefault();
      apply();
      if (destination) location.assign(destination);
      else status.textContent = selectedPrompt();
    });
    const selectedPrompt = () => !first.value || !second.value ? comparisonTool.dataset.choose : status.textContent;
    comparisonTool.hidden = false;
    apply();
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
