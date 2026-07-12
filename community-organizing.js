
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
                opt.style.pointerEvents = 'none';
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
            const progressText = lang === 'ht' ? 'Pwogresyon: ' + progress + '%' : 'Progress: ' + progress + '%';
            document.getElementById('progressText').textContent = progressText;

            document.getElementById('progressText').setAttribute('data-ht', 'Pwogresyon: ' + progress + '%');
            document.getElementById('progressText').setAttribute('data-en', 'Progress: ' + progress + '%');
        }

        window.addEventListener('load', updateProgress);
    

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
