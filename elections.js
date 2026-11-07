/* Progressive enhancement only: every fact and source is present in HTML. */
(function () {
  'use strict';
  function init() {
    const english = document.documentElement.lang === 'en';
    const directory = document.querySelector('[data-directory]');
    if (directory) {
      const search = directory.querySelector('[data-directory-search]');
      const department = directory.querySelector('[data-directory-department]');
      const commune = directory.querySelector('[data-directory-commune]');
      const normalise = function (value) { return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); };
      const rows = Array.from(directory.querySelectorAll('[data-directory-row]')).map(function (element) {
        return {element: element, text: normalise(element.textContent), department: element.dataset.department, commune: element.dataset.commune};
      });
      const allCommunes = commune ? commune.options[0].text : '';
      if (department) Array.from(new Set(rows.map(function (row) { return row.department; }))).sort().forEach(function (value) { department.add(new Option(value, value)); });
      function updateCommunes() {
        if (!commune) return;
        commune.replaceChildren(new Option(allCommunes, ''));
        Array.from(new Set(rows.filter(function (row) { return !department.value || row.department === department.value; }).map(function (row) { return row.commune; }))).sort().forEach(function (value) { commune.add(new Option(value, value)); });
      }
      function filterDirectory() {
        const query = normalise(search.value.trim());
        let count = 0;
        rows.forEach(function (row) {
          const show = row.text.includes(query) && (!department || !department.value || row.department === department.value) && (!commune || !commune.value || row.commune === commune.value);
          row.element.hidden = !show;
          if (show) count += 1;
        });
        directory.querySelector('[data-directory-status]').textContent = count + ' ' + directory.dataset.resultNoun;
      }
      updateCommunes();
      search.addEventListener('input', filterDirectory);
      if (department) department.addEventListener('change', function () { updateCommunes(); filterDirectory(); });
      if (commune) commune.addEventListener('change', filterDirectory);
      directory.querySelector('.election-directory-filters').hidden = false;
      filterDirectory();
    }
    document.querySelectorAll('[data-reviewed-date]').forEach(function (block) {
      const reviewed = Date.parse(block.dataset.reviewedDate + 'T00:00:00-05:00');
      const age = (Date.now() - reviewed) / 86400000;
      const warning = block.querySelector('.election-stale');
      if (warning && age > Number(block.dataset.staleDays)) warning.hidden = false;
    });
    const select = document.getElementById('election-audience');
    if (select) {
      const cards = Array.from(document.querySelectorAll('.election-resource[data-audience]'));
      const status = document.getElementById('election-filter-status');
      function filter() {
        let count = 0;
        cards.forEach(function (card) {
          const show = select.value === 'all' || card.dataset.audience === 'all' || card.dataset.audience === select.value;
          card.hidden = !show;
          if (show) count += 1;
        });
        status.textContent = english ? count + ' resources shown.' : count + ' resous parèt.';
      }
      select.closest('.election-filter').hidden = false;
      select.addEventListener('change', filter);
      filter();
    }
    document.querySelectorAll('.election-print').forEach(function (button) {
      button.hidden = false;
      button.addEventListener('click', function () { window.print(); });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
