
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
                alert('Tanpri chwazi yon repons / Please select an answer');
                return;
            }

            const options = document.querySelectorAll(`input[name="${questionName}"]`);
            const feedback = button.previousElementSibling;
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
                feedback.textContent = lang === 'ht' ? 'Kòrèk! Bon travay!' : 'Correct! Great job!';
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
            const totalSections = 10;
            const openedSections = document.querySelectorAll('.accordion-header.active').length;
            const answeredQuizzes = document.querySelectorAll('.quiz-option.correct').length;

            // Calculate progress: 10% per section opened + 3% per quiz answered
            const progress = Math.min(100, (openedSections * 10) + (answeredQuizzes * 3));

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
