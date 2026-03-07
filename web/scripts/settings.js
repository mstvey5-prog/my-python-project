// ===== DEFAULTS =====
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

function persist(key, value) {
    const s = load();
    s[key] = value;
    localStorage.setItem('wt_settings', JSON.stringify(s));
}

// ===== SVG ICONS =====
const ICONS = {
    theme: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2v20"/><path d="M12 2a10 10 0 0 0 0 20z" fill="currentColor" opacity="0.3"/></svg>`,
    accent: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L8 8.5C6.5 11 6 13 6 14.5a6 6 0 0 0 12 0c0-1.5-.5-3.5-2-6L12 2z" fill="currentColor" opacity="0.3"/><path d="M12 2L8 8.5C6.5 11 6 13 6 14.5a6 6 0 0 0 12 0c0-1.5-.5-3.5-2-6L12 2z"/></svg>`,
    glass: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="3" fill="currentColor" opacity="0.1"/><rect x="2" y="4" width="20" height="16" rx="3"/><path d="M6 8 Q9 6 11 9" opacity="0.6"/><path d="M6 11 Q7.5 10 9 11.5" opacity="0.4"/></svg>`,
    orbs: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3" fill="currentColor" opacity="0.5"/><circle cx="12" cy="12" r="6" opacity="0.3"/><circle cx="12" cy="12" r="10" opacity="0.15"/></svg>`,
    grid: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>`,
    anim: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L4.09 12.26a1 1 0 0 0 .74 1.69H11l-1 8 8.92-10.26a1 1 0 0 0-.74-1.69H13l1-8z" fill="currentColor" opacity="0.15"/><path d="M13 2L4.09 12.26a1 1 0 0 0 .74 1.69H11l-1 8 8.92-10.26a1 1 0 0 0-.74-1.69H13l1-8z"/></svg>`,
    off: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>`,
    ok: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
    reset: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.5"/></svg>`
};

// ===== TOAST =====
let toastTimer = null;

function showToast(iconKey, title, sub, duration = 2800) {
    const toast = document.getElementById('toast');
    const iconEl = document.getElementById('toastIcon');
    iconEl.innerHTML = ICONS[iconKey] || ICONS.ok;
    document.getElementById('toastTitle').textContent = title;
    document.getElementById('toastSub').textContent = sub;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), duration);
}

// ===== CONFIRM =====
function showConfirm() {
    return new Promise(resolve => {
        const overlay = document.getElementById('confirmOverlay');
        overlay.classList.add('show');
        function ok() { overlay.classList.remove('show'); cleanup(); resolve(true); }
        function cancel() { overlay.classList.remove('show'); cleanup(); resolve(false); }
        function cleanup() {
            document.getElementById('confirmOk').removeEventListener('click', ok);
            document.getElementById('confirmCancel').removeEventListener('click', cancel);
            overlay.removeEventListener('click', backdropClick);
        }
        function backdropClick(e) { if (e.target === overlay) cancel(); }
        document.getElementById('confirmOk').addEventListener('click', ok);
        document.getElementById('confirmCancel').addEventListener('click', cancel);
        overlay.addEventListener('click', backdropClick);
    });
}

// ===== ACCENT =====
function applyAccentUI(color) {
    const hex = color.replace('#', '');
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    document.documentElement.style.setProperty('--accent', color);
    document.documentElement.style.setProperty('--accent-glow', `rgba(${r},${g},${b},0.35)`);
}

// ===== NO-GLASS HELPER =====
function applyNoGlassStyles() {
    const isDark = document.body.classList.contains('dark');
    const bg = isDark ? '#1c1c1e' : '#ffffff';
    const border = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)';

    const old = document.getElementById('no-glass-override');
    if (old) old.remove();

    const styleTag = document.createElement('style');
    styleTag.id = 'no-glass-override';
    styleTag.textContent = `
        body.no-glass .navbar,
        body.no-glass .footer {
            background: ${bg} !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            border-color: ${border} !important;
        }
        body.no-glass .module-card,
        body.no-glass .app-mockup,
        body.no-glass .mockup-bar,
        body.no-glass .mockup-tabs,
        body.no-glass .mockup-card,
        body.no-glass .hero-badge,
        body.no-glass .btn-ghost,
        body.no-glass .nav-icon-btn,
        body.no-glass .theme-toggle,
        body.no-glass .settings-group,
        body.no-glass .settings-back,
        body.no-glass .accent-custom-inner,
        body.no-glass .toast,
        body.no-glass .confirm-dialog {
            background: ${bg} !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            border-color: ${border} !important;
        }
        body.no-glass * {
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
        }
    `;
    document.head.appendChild(styleTag);
}

// ===== THEME =====
function toggleTheme() {
    const isDark = document.body.classList.contains('dark');
    const next = isDark ? 'light' : 'dark';
    document.body.classList.remove('dark', 'light');
    document.body.classList.add(next);
    localStorage.setItem('wt_theme', next);
    const radio = document.querySelector(`input[name="theme"][value="${next}"]`);
    if (radio) radio.checked = true;
    persist('theme', next);
    if (document.body.classList.contains('no-glass')) applyNoGlassStyles();
}

// ===== INIT UI =====
function initUI() {
    const s = load();
    const theme = localStorage.getItem('wt_theme') || s.theme;
    const radio = document.querySelector(`input[name="theme"][value="${theme}"]`);
    if (radio) radio.checked = true;

    document.querySelectorAll('.accent-dot').forEach(d => {
        d.classList.toggle('active', d.dataset.color === s.accent);
    });

    document.getElementById('glassToggle').checked = s.glass;
    document.getElementById('orbsToggle').checked = s.orbs;
    document.getElementById('gridToggle').checked = s.grid;
    document.getElementById('animToggle').checked = s.animations;
    document.getElementById('fontSizeVal').textContent = s.fontSize + '%';
}

// ===== EVENTS =====
document.querySelectorAll('input[name="theme"]').forEach(r => {
    r.addEventListener('change', () => {
        document.body.classList.remove('dark', 'light');
        if (r.value === 'system') {
            const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.body.classList.add(dark ? 'dark' : 'light');
        } else {
            document.body.classList.add(r.value);
        }
        localStorage.setItem('wt_theme', r.value);
        persist('theme', r.value);
        if (document.body.classList.contains('no-glass')) applyNoGlassStyles();
        const label = r.value === 'system' ? 'Системная тема' : r.value === 'dark' ? 'Тёмная тема' : 'Светлая тема';
        showToast('theme', 'Тема изменена', label);
    });
});

document.getElementById('accentPicker').addEventListener('click', e => {
    const dot = e.target.closest('.accent-dot');
    if (!dot || dot.dataset.color === 'custom') return;
    document.querySelectorAll('.accent-dot').forEach(d => d.classList.remove('active'));
    dot.classList.add('active');
    applyAccentUI(dot.dataset.color);
    persist('accent', dot.dataset.color);
    const preview = document.getElementById('accentCustomPreview');
    if (preview) preview.style.background = dot.dataset.color;
    showToast('accent', 'Акцент изменён', 'Новый цвет применён');
});

document.getElementById('glassToggle').addEventListener('change', e => {
    document.body.classList.toggle('no-glass', !e.target.checked);
    if (!e.target.checked) {
        document.querySelectorAll('*').forEach(el => {
            try { el.style.backdropFilter = 'none'; el.style.webkitBackdropFilter = 'none'; } catch(_) {}
        });
    } else {
        document.querySelectorAll('*').forEach(el => {
            el.style.backdropFilter = '';
            el.style.webkitBackdropFilter = '';
        });
    }
    persist('glass', e.target.checked);
    showToast(e.target.checked ? 'glass' : 'off', 'Стеклянный эффект', e.target.checked ? 'Включён' : 'Выключен');
});

document.getElementById('orbsToggle').addEventListener('change', e => {
    const noise = document.querySelector('.noise');
    if (noise) noise.style.display = e.target.checked ? '' : 'none';
    if (!e.target.checked) {
        document.body.style.setProperty('--orb-3', 'transparent');
    } else {
        document.body.style.removeProperty('--orb-3');
    }
    persist('orbs', e.target.checked);
    showToast(e.target.checked ? 'orbs' : 'off', 'Орбы на фоне', e.target.checked ? 'Включены' : 'Выключены');
});

document.getElementById('gridToggle').addEventListener('change', e => {
    const grid = document.querySelector('.grid-bg');
    if (grid) grid.style.display = e.target.checked ? '' : 'none';
    persist('grid', e.target.checked);
    showToast(e.target.checked ? 'grid' : 'off', 'Сетка фона', e.target.checked ? 'Включена' : 'Выключена');
});

document.getElementById('animToggle').addEventListener('change', e => {
    document.body.classList.toggle('no-anim', !e.target.checked);
    persist('animations', e.target.checked);
    showToast(e.target.checked ? 'anim' : 'off', 'Анимации', e.target.checked ? 'Включены' : 'Выключены');
});

document.getElementById('resetBtn').addEventListener('click', async () => {
    const confirmed = await showConfirm();
    if (!confirmed) return;
    localStorage.removeItem('wt_settings');
    localStorage.removeItem('wt_theme');
    showToast('reset', 'Настройки сброшены', 'Страница обновится через секунду');
    setTimeout(() => location.reload(), 1400);
});

// ===== ACCENT EXPAND =====
const accentExpandBtn = document.getElementById('accentExpandBtn');
const accentCustomPanel = document.getElementById('accentCustomPanel');

if (accentExpandBtn && accentCustomPanel) {
    accentExpandBtn.addEventListener('click', () => {
        const isOpen = accentCustomPanel.classList.toggle('open');
        accentExpandBtn.classList.toggle('open', isOpen);
        const preview = document.getElementById('accentCustomPreview');
        if (preview) {
            const currentAccent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
            preview.style.background = currentAccent;
        }
    });
}

initUI();