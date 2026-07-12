
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
                alert('Tanpri chwazi yon repons / Please select an answer');
                return;
            }

            const feedback = button.previousElementSibling;
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
                feedback.textContent = lang === 'ht' ? 'Kòrèk! Bon travay!' : 'Correct! Great job!';
            } else {
                feedback.className = 'quiz-feedback show incorrect';
                const lang = document.querySelector('html').lang;
                feedback.textContent = lang === 'ht' ? 'Pa kòrèk. Eseye ankò!' : 'Incorrect. Try again!';
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
    

// CSP-safe event wiring (replaces the inline on* handlers removed for a strict CSP)
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.accordion-header').forEach(function (h) {
        h.addEventListener('click', function () { toggleAccordion(h); });
    });
    document.querySelectorAll('.quiz-option[data-correct]').forEach(function (o) {
        o.addEventListener('click', function () { checkQuiz(o, o.dataset.correct === 'true'); });
    });
    document.querySelectorAll('.quiz-submit[data-quiz]').forEach(function (b) {
        b.addEventListener('click', function () { checkQuiz(b.dataset.quiz, b.dataset.answer, b); });
    });
});
