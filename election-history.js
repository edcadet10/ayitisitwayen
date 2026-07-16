// Election history — timeline cards + filters (CSP-safe external script;
// replaces the former inline <script> and onclick attributes)

(function () {
    let currentFilter = 'all';

    function setExpanded(header, card) {
        header.setAttribute('aria-expanded', card.classList.contains('active') ? 'true' : 'false');
    }

    function toggleElection(header) {
        const card = header.parentElement;
        card.classList.toggle('active');
        setExpanded(header, card);
    }

    document.addEventListener('DOMContentLoaded', function () {
        // Expand/collapse — click + keyboard (headers carry role="button" tabindex="0")
        document.querySelectorAll('.election-header').forEach(function (header, i) {
            const details = header.parentElement.querySelector('.election-details');
            if (details) {
                if (!details.id) details.id = 'eleksyon-' + (i + 1);
                header.setAttribute('aria-controls', details.id);
            }
            setExpanded(header, header.parentElement);

            header.addEventListener('click', function () { toggleElection(header); });
            header.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleElection(header);
                }
            });
        });

        // Filters — toggle buttons with pressed state
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(function (btn) {
            btn.setAttribute('aria-pressed', btn.classList.contains('active') ? 'true' : 'false');
            btn.addEventListener('click', function () {
                currentFilter = btn.dataset.filter;

                filterBtns.forEach(function (b) {
                    b.classList.remove('active');
                    b.setAttribute('aria-pressed', 'false');
                });
                btn.classList.add('active');
                btn.setAttribute('aria-pressed', 'true');

                document.querySelectorAll('.election-card').forEach(function (card) {
                    const types = (card.dataset.type || '').split(' ');
                    if (currentFilter === 'all' || types.includes(currentFilter)) {
                        card.classList.remove('hidden');
                    } else {
                        card.classList.add('hidden');
                    }
                });
            });
        });
    });
})();
