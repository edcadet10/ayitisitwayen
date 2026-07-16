
        function toggleAccordion(header) {
            const content = header.nextElementSibling;
            const isActive = header.classList.contains('active');

            header.classList.toggle('active');
            content.classList.toggle('active');

            updateProgress();
        }

        function checkQuiz(option, isCorrect) {
            const options = option.parentElement.children;
            for (let opt of options) {
                opt.disabled = true;
            }

            if (isCorrect) {
                option.classList.add('correct');
            } else {
                option.classList.add('incorrect');
                for (let opt of options) {
                    if (opt.dataset.correct === 'true') {
                        opt.classList.add('correct');
                    }
                }
            }

            updateProgress();
        }

        function updateProgress() {
            const totalSections = 6;
            const totalQuizzes = 3;

            const openedSections = document.querySelectorAll('.accordion-header.active').length;
            const answeredQuizzes = document.querySelectorAll('.quiz-option.correct').length;

            const progress = Math.min(100, Math.round((openedSections / totalSections) * 70 + (answeredQuizzes / totalQuizzes) * 30));

            document.getElementById('progressFill').style.width = progress + '%';

            const lang = document.documentElement.lang;
            const progressText = lang === 'ht' ? 'Pwogrè: ' + progress + '%' : 'Progress: ' + progress + '%';
            document.getElementById('progressText').textContent = progressText;

            document.getElementById('progressText').setAttribute('data-ht', 'Pwogrè: ' + progress + '%');
            document.getElementById('progressText').setAttribute('data-en', 'Progress: ' + progress + '%');
        }

        window.addEventListener('load', updateProgress);
    


// CSP-safe event wiring + accessibility state (replaces inline on* handlers)
document.addEventListener('DOMContentLoaded', function () {
    function syncAccordions() {
        document.querySelectorAll('.accordion-header').forEach(function (h) {
            h.setAttribute('aria-expanded', h.classList.contains('active') ? 'true' : 'false');
        });
    }

    document.querySelectorAll('.accordion-header').forEach(function (h, i) {
        var panel = h.nextElementSibling;
        if (panel) {
            if (!panel.id) panel.id = 'akordeyon-' + (i + 1);
            h.setAttribute('aria-controls', panel.id);
        }
        h.addEventListener('click', function () { toggleAccordion(h); syncAccordions(); });
    });
    syncAccordions();
    window.addEventListener('load', syncAccordions);

    document.querySelectorAll('.quiz-feedback').forEach(function (f) {
        f.setAttribute('role', 'status');
    });

    // Feedback for single-tap quizzes: never color-only, announced politely
    function announceQuiz(option, isCorrect) {
        var wrap = option.closest('.quiz, .quiz-container') || option.parentElement;
        var fb = wrap.querySelector('.quiz-feedback');
        if (!fb) {
            fb = document.createElement('div');
            fb.setAttribute('role', 'status');
            option.parentElement.insertAdjacentElement('afterend', fb);
        }
        var ht = document.documentElement.lang !== 'en';
        fb.className = 'quiz-feedback show ' + (isCorrect ? 'correct' : 'incorrect');
        fb.textContent = isCorrect
            ? (ht ? '\u2713 Kòrèk! Bon travay!' : '\u2713 Correct! Great job!')
            : (ht ? '\u2717 Pa kòrèk. Bon repons lan make.' : '\u2717 Incorrect. The correct answer is highlighted.');
    }

    document.querySelectorAll('.quiz-option[data-correct]').forEach(function (o) {
        o.addEventListener('click', function () {
            if (o.disabled) return;
            checkQuiz(o, o.dataset.correct === 'true');
            announceQuiz(o, o.dataset.correct === 'true');
        });
    });
    document.querySelectorAll('.quiz-submit[data-quiz]').forEach(function (b) {
        b.addEventListener('click', function () { checkQuiz(b.dataset.quiz, b.dataset.answer, b); });
    });

    // Progress bar semantics
    var fill = document.getElementById('progressFill');
    if (fill && fill.parentElement) {
        var bar = fill.parentElement;
        bar.setAttribute('role', 'progressbar');
        bar.setAttribute('aria-valuemin', '0');
        bar.setAttribute('aria-valuemax', '100');
        bar.setAttribute('aria-valuenow', '0');
        if (document.getElementById('progressText')) {
            bar.setAttribute('aria-describedby', 'progressText');
        }
        new MutationObserver(function () {
            bar.setAttribute('aria-valuenow', String(parseInt(fill.style.width, 10) || 0));
        }).observe(fill, { attributes: true, attributeFilter: ['style'] });
    }
});
