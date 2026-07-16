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
    'presidents.html': "Haiti's Heads of State (1804-2026) - Ayiti Sitwayen",
    'prime-ministers.html': "Haiti's Prime Ministers (1988-2026) - Ayiti Sitwayen",
    'parliament.html': "Haiti's Parliament - Ayiti Sitwayen",
    'candidates.html': 'The 2026 Election Candidates - Ayiti Sitwayen',
    'voting-day.html': 'Election Day Guide - Ayiti Sitwayen',
    'local-government.html': 'Local Government - Ayiti Sitwayen',
    'judiciary.html': 'The Justice System - Ayiti Sitwayen',
    'diaspora.html': 'The Diaspora and the Elections - Ayiti Sitwayen',
    'research.html': 'Research - Ayiti Sitwayen',
    'research-note-1.html': 'Research Note #1: Civic Attitudes by Group - Ayiti Sitwayen',
    'research-note-2.html': 'Research Note #2: 20 Years of Civic Attitudes (2006-2023) - Ayiti Sitwayen',
    'privacy.html': 'Privacy Policy - Ayiti Sitwayen',
    'terms.html': 'Terms & Conditions - Ayiti Sitwayen'
};

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

let currentLang = localStorage.getItem('lang') === 'en' ? 'en' : 'ht';

function pageFile() {
    const file = window.location.pathname.split('/').pop();
    return file === '' ? 'index.html' : file;
}

function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);

    // Swap all bilingual elements (inputs swap their placeholder, not innerHTML)
    document.querySelectorAll('[data-ht][data-en]').forEach(element => {
        const htText = element.getAttribute('data-ht');
        const enText = element.getAttribute('data-en');
        if (htText && enText) {
            const value = lang === 'ht' ? htText : enText;
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = value;
            } else {
                element.innerHTML = value;
            }
        }
    });

    // Bilingual aria-labels (hidden text is the classic missed translation)
    document.querySelectorAll('[data-ht-aria][data-en-aria]').forEach(element => {
        element.setAttribute('aria-label', lang === 'ht'
            ? element.getAttribute('data-ht-aria')
            : element.getAttribute('data-en-aria'));
    });

    // Keep the document language and title in sync
    document.documentElement.lang = lang;
    document.title = lang === 'ht' ? DEFAULT_TITLE : (EN_TITLES[pageFile()] || DEFAULT_TITLE);

    // Update language switcher button (shows the language you can switch TO)
    const langSwitch = document.querySelector('.lang-switch');
    if (langSwitch) {
        langSwitch.textContent = lang === 'ht' ? 'EN' : 'HT';
        langSwitch.setAttribute('lang', lang === 'ht' ? 'en' : 'ht');
        langSwitch.setAttribute('aria-label', lang === 'ht' ? 'Switch to English' : 'Tounen an Kreyòl');
    }
}

function toggleLanguage() {
    applyLanguage(currentLang === 'ht' ? 'en' : 'ht');
}

// Apply the stored language choice immediately (this script sits at the end
// of <body>, so the DOM is parsed) — avoids a flash of the wrong language.
if (currentLang !== 'ht') {
    applyLanguage(currentLang);
}

// Smooth Scrolling for Anchor Links (guard: bare "#" is not a valid selector)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (!href || href === '#') {
            return;
        }
        const target = document.querySelector(href);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({
                behavior: prefersReducedMotion.matches ? 'auto' : 'smooth',
                block: 'start'
            });
        }
    });
});

// Scroll-in reveal for homepage cards — skipped entirely for reduced motion,
// with a timed fallback so content can never stay hidden.
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.mission-card, .team-member');
    if (!animatedElements.length || prefersReducedMotion.matches || !('IntersectionObserver' in window)) {
        return;
    }

    const reveal = el => {
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                reveal(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(24px)';
        el.style.transition = 'opacity 0.5s cubic-bezier(0.2, 0, 0, 1), transform 0.5s cubic-bezier(0.2, 0, 0, 1)';
        observer.observe(el);
    });

    // Fallback: never leave content invisible (e.g. observer quirks, printing)
    setTimeout(() => animatedElements.forEach(reveal), 2500);
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

// Mobile Menu Toggle (keeps aria-expanded in sync for assistive tech)
function setMenuState(open) {
    const navLinks = document.querySelector('.nav-links');
    const navToggle = document.querySelector('.nav-toggle');
    if (!navLinks) return;
    navLinks.classList.toggle('active', open);
    if (navToggle) {
        navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
}

function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    setMenuState(!(navLinks && navLinks.classList.contains('active')));
}

// Close mobile menu after tapping a nav link
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => setMenuState(false));
});

// Close mobile menu with Escape and return focus to the toggle
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const navLinks = document.querySelector('.nav-links');
        if (navLinks && navLinks.classList.contains('active')) {
            setMenuState(false);
            const navToggle = document.querySelector('.nav-toggle');
            if (navToggle) navToggle.focus();
        }
    }
});

// Add active state to current nav link (rAF-throttled; no layout thrash per event)
let scrollTickPending = false;
window.addEventListener('scroll', () => {
    if (scrollTickPending) return;
    scrollTickPending = true;
    requestAnimationFrame(() => {
        scrollTickPending = false;
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');
        if (!sections.length || !navLinks.length) return;

        let currentSection = '';
        sections.forEach(section => {
            if (window.pageYOffset >= section.offsetTop - 120) {
                currentSection = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === `#${currentSection}`);
        });
    });
}, { passive: true });

// Wire nav controls without inline handlers (CSP-safe)
document.addEventListener('DOMContentLoaded', function () {
    const navToggle = document.querySelector('.nav-toggle');
    if (navToggle) {
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.addEventListener('click', toggleMobileMenu);
    }
    const langSwitch = document.querySelector('.lang-switch');
    if (langSwitch) {
        if (!langSwitch.getAttribute('aria-label')) {
            langSwitch.setAttribute('aria-label', currentLang === 'ht' ? 'Switch to English' : 'Tounen an Kreyòl');
            langSwitch.setAttribute('lang', currentLang === 'ht' ? 'en' : 'ht');
        }
        langSwitch.addEventListener('click', toggleLanguage);
    }
});
