// ===== APPLY-SETTINGS.JS =====
// Подключать на каждой странице ДО других скриптов

(function () {
    const DEFAULTS = {
        theme: 'dark',
        accent: '#ff3b30',
        glass: true,
        orbs: true,
        grid: true,
        fontSize: 100,
        animations: true
    };

    function load() {
        try {
            const s = localStorage.getItem('wt_settings');
            return s ? { ...DEFAULTS, ...JSON.parse(s) } : { ...DEFAULTS };
        } catch { return { ...DEFAULTS }; }
    }

    const s = load();

    // --- ТЕМА ---
    const theme = localStorage.getItem('wt_theme') || s.theme;
    if (theme === 'system') {
        const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.body.classList.add(dark ? 'dark' : 'light');
    } else {
        document.body.classList.add(theme);
    }

    // --- АКЦЕНТ ---
    if (s.accent && s.accent !== '#ff3b30') {
        const hex = s.accent.replace('#', '');
        const r = parseInt(hex.slice(0, 2), 16);
        const g = parseInt(hex.slice(2, 4), 16);
        const b = parseInt(hex.slice(4, 6), 16);
        document.documentElement.style.setProperty('--accent', s.accent);
        document.documentElement.style.setProperty('--accent-glow', `rgba(${r},${g},${b},0.35)`);
    }

    // --- СТЕКЛО ---
    if (!s.glass) {
        document.body.classList.add('no-glass');
    }

    // --- ШРИФТ ---
    const fontSize = parseInt(s.fontSize) || 100;
        if (fontSize !== 100) {
        document.documentElement.style.setProperty('font-size', fontSize + '%');
    }

    // --- АНИМАЦИИ ---
    if (!s.animations) {
        document.body.classList.add('no-anim');
    }

    // DOM готов — применяем орбы и сетку
    document.addEventListener('DOMContentLoaded', function () {
        if (!s.orbs) {
            const noise = document.querySelector('.noise');
            if (noise) noise.style.display = 'none';
        }
        if (!s.grid) {
            const grid = document.querySelector('.grid-bg');
            if (grid) grid.style.display = 'none';
        }
    });

    // system theme watcher
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
        const t = localStorage.getItem('wt_theme') || DEFAULTS.theme;
        if (t === 'system') {
            document.body.classList.remove('dark', 'light');
            document.body.classList.add(this.matches ? 'dark' : 'light');
        }
    });
})();