// Ayiti Sitwayen - JavaScript

// Language Toggle (persisted across pages via localStorage; Kreyòl is the default)
const DEFAULT_TITLE = document.title;

const EN_TITLES = {
    'index.html': 'Haitian Citizens - Strengthening Civic Engagement in Haiti',
    'education.html': 'Civic Education - Ayiti Sitwayen',
    'democracy.html': 'Democracy - Ayiti Sitwayen',
    'citizenship.html': 'Citizenship - Ayiti Sitwayen',
    'voting.html': 'Voting - Ayiti Sitwayen',
    'constitution.html': 'Constitution - Ayiti Sitwayen',
    'rights.html': 'Rights - Ayiti Sitwayen',
    'corruption.html': 'Corruption - Ayiti Sitwayen',
    'civil-society.html': 'Civil Society - Ayiti Sitwayen',
    'community-organizing.html': 'Community Organizing - Ayiti Sitwayen',
    'political-parties.html': 'Political Parties - Ayiti Sitwayen',
    'electoral-process.html': 'Electoral Process - Ayiti Sitwayen',
    'glossary.html': 'Political Dictionary - Ayiti Sitwayen',
    'election-history.html': 'Haiti Election History - Ayiti Sitwayen',
    'privacy.html': 'Privacy Policy - Ayiti Sitwayen',
    'terms.html': 'Terms & Conditions - Ayiti Sitwayen'
};

let currentLang = localStorage.getItem('lang') === 'en' ? 'en' : 'ht';

function pageFile() {
    const file = window.location.pathname.split('/').pop();
    return file === '' ? 'index.html' : file;
}

function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);

    // Swap all bilingual elements
    document.querySelectorAll('[data-ht][data-en]').forEach(element => {
        const htText = element.getAttribute('data-ht');
        const enText = element.getAttribute('data-en');
        if (htText && enText) {
            element.innerHTML = lang === 'ht' ? htText : enText;
        }
    });

    // Keep the document language and title in sync
    document.documentElement.lang = lang;
    document.title = lang === 'ht' ? DEFAULT_TITLE : (EN_TITLES[pageFile()] || DEFAULT_TITLE);

    // Update language switcher button
    const langSwitch = document.querySelector('.lang-switch');
    if (langSwitch) {
        langSwitch.textContent = lang === 'ht' ? 'EN' : 'HT';
    }
}

function toggleLanguage() {
    applyLanguage(currentLang === 'ht' ? 'en' : 'ht');
}

// Apply the stored language choice on load so it survives navigation
document.addEventListener('DOMContentLoaded', () => {
    if (currentLang !== 'ht') {
        applyLanguage(currentLang);
    }
});

// Smooth Scrolling for Anchor Links (guard: bare "#" is not a valid selector)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (!href || href === '#') {
            return;
        }
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Intersection Observer for Animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all mission cards and team members
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.mission-card, .team-member');

    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(el);
    });
});

// Form Submission Handler (mailto fallback until a Formspree form ID is configured)
const contactForm = document.querySelector('.contact-form');
if (contactForm && !contactForm.action.includes('formspree')) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const name = contactForm.elements['name'].value;
        const email = contactForm.elements['email'].value;
        const message = contactForm.elements['message'].value;
        const subject = encodeURIComponent('Mesaj sou ayitisitwayen.org - ' + name);
        const body = encodeURIComponent(message + '\n\n— ' + name + ' <' + email + '>');
        window.location.href = 'mailto:contact@ayitisitwayen.org?subject=' + subject + '&body=' + body;
    });
}

// Mobile Menu Toggle
function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('active');
}

// Close mobile menu after tapping a nav link
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        document.querySelector('.nav-links').classList.remove('active');
    });
});

// Add active state to current nav link
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');

    let currentSection = '';

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;

        if (window.pageYOffset >= sectionTop - 100) {
            currentSection = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
});
