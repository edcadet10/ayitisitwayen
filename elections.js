/* Progressive enhancement only: every fact and source is present in HTML. */
(function () {
  'use strict';
  function init() {
    const english = document.documentElement.lang === 'en';
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
