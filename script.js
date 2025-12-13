// Ayiti Sitwayen - JavaScript

// Language Toggle
let currentLang = 'ht'; // Default to Haitian Creole

function toggleLanguage() {
    currentLang = currentLang === 'ht' ? 'en' : 'ht';

    // Update all elements with data-ht and data-en attributes
    const elements = document.querySelectorAll('[data-ht][data-en]');

    elements.forEach(element => {
        const htText = element.getAttribute('data-ht');
        const enText = element.getAttribute('data-en');

        if (htText && enText) {
            element.innerHTML = currentLang === 'ht' ? htText : enText;
        }
    });

    // Update language switcher button
    const langSwitch = document.querySelector('.lang-switch');
    if (langSwitch) {
        langSwitch.textContent = currentLang === 'ht' ? 'EN' : 'HT';
    }
}

// Smooth Scrolling for Anchor Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
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

// Form Submission Handler (if not using Formspree)
const contactForm = document.querySelector('.contact-form');
if (contactForm && !contactForm.action.includes('formspree')) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert(currentLang === 'ht' ?
            'Mèsi! Nou pral reponn ou rapid.' :
            'Thank you! We will respond shortly.');
        contactForm.reset();
    });
}

// Mobile Menu Toggle (if needed in the future)
function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('active');
}

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
