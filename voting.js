
        // Accordion Toggle
        function toggleAccordion(header) {
            const content = header.nextElementSibling;
            const allHeaders = document.querySelectorAll('.accordion-header');
            const allContents = document.querySelectorAll('.accordion-content');

            // Close all other accordions
            allHeaders.forEach(h => {
                if (h !== header) {
                    h.classList.remove('active');
                }
            });
            allContents.forEach(c => {
                if (c !== content) {
                    c.classList.remove('active');
                }
            });

            // Toggle current accordion
            header.classList.toggle('active');
            content.classList.toggle('active');

            // Update progress
            updateProgress();
        }

        // Quiz Check
        function checkQuiz(questionName, correctAnswer, button) {
            const selectedOption = document.querySelector(`input[name="${questionName}"]:checked`);
            if (!selectedOption) {
                const fb = button.parentElement.querySelector('.quiz-feedback');
                if (fb) {
                    fb.className = 'quiz-feedback show incorrect';
                    fb.textContent = document.documentElement.lang !== 'en' ? 'Tanpri chwazi yon repons anvan.' : 'Please choose an answer first.';
                }
                return;
            }

            const feedback = button.parentElement.querySelector('.quiz-feedback') || button.previousElementSibling;
            const allOptions = document.querySelectorAll(`input[name="${questionName}"]`);

            // Disable all options after answer
            allOptions.forEach(opt => {
                opt.disabled = true;
                const label = opt.closest('.quiz-option');
                if (opt.value === correctAnswer) {
                    label.classList.add('correct');
                } else if (opt.checked && opt.value !== correctAnswer) {
                    label.classList.add('incorrect');
                }
            });

            // Show feedback
            if (selectedOption.value === correctAnswer) {
                feedback.className = 'quiz-feedback show correct';
                const lang = document.querySelector('html').lang;
                feedback.textContent = lang === 'ht' ? '\u2713 Kòrèk! Bon travay!' : '\u2713 Correct! Great job!';
            } else {
                feedback.className = 'quiz-feedback show incorrect';
                const lang = document.querySelector('html').lang;
                feedback.textContent = lang === 'ht' ? '\u2717 Pa kòrèk. Bon repons lan make anwo a.' : '\u2717 Incorrect. The correct answer is highlighted above.';
            }

            button.disabled = true;
            updateProgress();
        }

        // Progress Tracker
        function updateProgress() {
            const totalSections = 9;
            const openedSections = document.querySelectorAll('.accordion-header.active').length;
            const answeredQuizzes = document.querySelectorAll('.quiz-option.correct').length;

            // Calculate progress: opened sections + bonus for quizzes
            const progress = Math.min(100, (openedSections * 11) + (answeredQuizzes * 3));
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            const lang = document.querySelector('html').lang;

            progressFill.style.width = progress + '%';
            progressText.textContent = lang === 'ht' ? `Pwogrè: ${progress}%` : `Progress: ${progress}%`;

            // Show completion badge if 100%
            if (progress >= 100) {
                document.getElementById('completionBadge').classList.add('show');
            }
        }

        // Auto-open first section on load
        window.addEventListener('load', () => {
            const firstHeader = document.querySelector('.accordion-header');
            if (firstHeader) {
                toggleAccordion(firstHeader);
            }
        });
    


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
