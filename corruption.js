
        // Accordion functionality
        function toggleAccordion(header) {
            const content = header.nextElementSibling;
            const isActive = header.classList.contains('active');

            header.classList.toggle('active');
            content.classList.toggle('active');

            updateProgress();
        }

        // Quiz functionality
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

            const options = document.querySelectorAll(`input[name="${questionName}"]`);
            const feedback = button.parentElement.querySelector('.quiz-feedback') || button.previousElementSibling;
            const lang = document.documentElement.lang;

            // Disable all options
            options.forEach(option => {
                option.disabled = true;
                const label = option.closest('.quiz-option');
                if (option.value === correctAnswer) {
                    label.classList.add('correct');
                } else if (option.checked) {
                    label.classList.add('incorrect');
                }
            });

            // Show feedback
            feedback.classList.add('show');
            if (selectedOption.value === correctAnswer) {
                feedback.classList.add('correct');
                feedback.textContent = lang === 'ht' ? '\u2713 Kòrèk! Bon travay!' : '\u2713 Correct! Great job!';
            } else {
                feedback.classList.add('incorrect');
                feedback.textContent = lang === 'ht' ? 'Pa kòrèk. Eseye ankò.' : 'Incorrect. Try again.';
            }

            // Disable button
            button.disabled = true;
            button.style.opacity = '0.5';

            updateProgress();
        }

        // Progress tracking
        function updateProgress() {
            const totalSections = 5;
            const openedSections = document.querySelectorAll('.accordion-header.active').length;
            const answeredQuizzes = document.querySelectorAll('.quiz-option.correct').length;

            // Calculate progress: 20% per section opened + 3% per quiz answered
            const progress = Math.min(100, (openedSections * 20) + (answeredQuizzes * 3));

            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            const completionBadge = document.getElementById('completionBadge');
            const lang = document.documentElement.lang;

            progressFill.style.width = progress + '%';
            progressText.textContent = lang === 'ht' ? `Pwogrè: ${progress}%` : `Progress: ${progress}%`;

            // Show completion badge at 100%
            if (progress === 100) {
                completionBadge.classList.add('show');
            }
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            updateProgress();
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
