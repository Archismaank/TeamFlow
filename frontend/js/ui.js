export function initUIEnhancements() {
    initThemeSwitcher();
    initOffcanvasSidebar();
    initBackToTop();
    initScrollReveal();
}

export function hidePreloader() {
    const preloader = document.getElementById('page-preloader');
    if (preloader && !preloader.classList.contains('fade-out')) {
        preloader.classList.add('fade-out');
        setTimeout(() => preloader.remove(), 400);
    }
}

function initThemeSwitcher() {
    const savedTheme = localStorage.getItem('teamflow_theme') || 'light';
    applyTheme(savedTheme);

    document.querySelectorAll('.theme-toggle-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            applyTheme(next);
            localStorage.setItem('teamflow_theme', next);
        });
    });
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.querySelectorAll('.theme-icon').forEach((icon) => {
        icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    });
}

function initOffcanvasSidebar() {
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    const openBtn = document.getElementById('btn-open-sidebar');
    const closeBtn = document.getElementById('btn-close-sidebar');

    const openMenu = () => {
        sidebar.classList.add('open');
        backdrop.classList.remove('hidden');
    };

    const closeMenu = () => {
        sidebar.classList.remove('open');
        backdrop.classList.add('hidden');
    };

    if (openBtn) openBtn.addEventListener('click', openMenu);
    if (closeBtn) closeBtn.addEventListener('click', closeMenu);
    if (backdrop) backdrop.addEventListener('click', closeMenu);

    // Auto-close mobile sidebar when selecting a project
    document.getElementById('project-list')?.addEventListener('click', (e) => {
        if (e.target.closest('.nav-item') && window.innerWidth <= 900) {
            closeMenu();
        }
    });
}

function initBackToTop() {
    const btn = document.getElementById('btn-back-to-top');
    if (!btn) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 250) {
            btn.classList.remove('hidden');
        } else {
            btn.classList.add('hidden');
        }
    });

    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

export function initScrollReveal() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                }
            });
        },
        { threshold: 0.08 }
    );

    document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
}

export function animateCounter(element, targetValue, suffix = '', duration = 450) {
    if (!element) return;
    const startValue = parseFloat(element.dataset.counter || '0') || 0;
    const endValue = Number(targetValue) || 0;
    element.dataset.counter = endValue;

    const isFloat = !Number.isInteger(endValue);
    const startTime = performance.now();

    function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = startValue + (endValue - startValue) * eased;

        element.textContent = `${isFloat ? current.toFixed(1) : Math.round(current)}${suffix}`;

        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            element.textContent = `${endValue}${suffix}`;
        }
    }

    requestAnimationFrame(step);
}