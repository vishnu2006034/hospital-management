/* ============================================
   MedCore HMS - Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initStatsCounter();
    initScrollAnimations();
});

/* ---------- Navbar Toggle (Mobile) ---------- */
function initNavbar() {
    const toggle = document.getElementById('nav-toggle');
    const links = document.getElementById('nav-links');

    if (toggle && links) {
        toggle.addEventListener('click', () => {
            links.classList.toggle('active');
            const icon = toggle.querySelector('i');
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-times');
        });

        // Close mobile menu when a link is clicked
        links.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                links.classList.remove('active');
                const icon = toggle.querySelector('i');
                icon.classList.add('fa-bars');
                icon.classList.remove('fa-times');
            });
        });
    }

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('main-navbar');
        if (navbar) {
            navbar.style.background = window.scrollY > 50
                ? 'rgba(10, 14, 26, 0.95)'
                : 'rgba(10, 14, 26, 0.8)';
        }
    });
}

/* ---------- Animated Stats Counter ---------- */
function initStatsCounter() {
    const counters = document.querySelectorAll('.stat-number[data-count]');
    if (counters.length === 0) return;

    const animateCounter = (el) => {
        const target = parseInt(el.getAttribute('data-count'));
        const duration = 2000;
        const startTime = performance.now();

        const step = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(eased * target);

            el.textContent = current.toLocaleString() + '+';

            if (progress < 1) {
                requestAnimationFrame(step);
            }
        };

        requestAnimationFrame(step);
    };

    // Use IntersectionObserver to trigger on scroll
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.5 }
    );

    counters.forEach((counter) => observer.observe(counter));
}

/* ---------- Scroll Reveal Animations ---------- */
function initScrollAnimations() {
    const elements = document.querySelectorAll(
        '.feature-card, .dash-stat-card, .section-header'
    );

    if (elements.length === 0) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    elements.forEach((el) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(24px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });
}
