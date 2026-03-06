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

// ===== TOAST =====
let toastTimer = null;

function showToast(icon, title, sub, duration = 2800) {
    const toast = document.getElementById('toast');
    document.getElementById('toastIcon').textContent = icon;
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

        function ok() {
            overlay.classList.remove('show');
            cleanup();
            resolve(true);
        }
        function cancel() {
            overlay.classList.remove('show');
            cleanup();
            resolve(false);
        }
        function cleanup() {
            document.getElementById('confirmOk').removeEventListener('click', ok);
            document.getElementById('confirmCancel').removeEventListener('click', cancel);
            overlay.removeEventListener('click', backdropClick);
        }
        function backdropClick(e) {
            if (e.target === overlay) cancel();
        }

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
        showToast('🎨', 'Тема изменена', r.value === 'system' ? 'Используется системная тема' : r.value === 'dark' ? 'Тёмная тема активна' : 'Светлая тема активна');
    });
});

document.getElementById('accentPicker').addEventListener('click', e => {
    const dot = e.target.closest('.accent-dot');
    if (!dot) return;
    document.querySelectorAll('.accent-dot').forEach(d => d.classList.remove('active'));
    dot.classList.add('active');
    applyAccentUI(dot.dataset.color);
    persist('accent', dot.dataset.color);
    showToast('🎨', 'Акцент изменён', 'Новый цвет применён');
});

document.getElementById('glassToggle').addEventListener('change', e => {
    document.body.classList.toggle('no-glass', !e.target.checked);
    persist('glass', e.target.checked);
    showToast(e.target.checked ? '🪟' : '🚫', 'Стеклянный эффект', e.target.checked ? 'Включён' : 'Выключен');
});

document.getElementById('orbsToggle').addEventListener('change', e => {
    const noise = document.querySelector('.noise');
    if (noise) noise.style.display = e.target.checked ? '' : 'none';
    persist('orbs', e.target.checked);
    showToast(e.target.checked ? '✨' : '🚫', 'Орбы на фоне', e.target.checked ? 'Включены' : 'Выключены');
});

document.getElementById('gridToggle').addEventListener('change', e => {
    const grid = document.querySelector('.grid-bg');
    if (grid) grid.style.display = e.target.checked ? '' : 'none';
    persist('grid', e.target.checked);
    showToast(e.target.checked ? '▦' : '🚫', 'Сетка фона', e.target.checked ? 'Включена' : 'Выключена');
});

document.getElementById('animToggle').addEventListener('change', e => {
    document.body.classList.toggle('no-anim', !e.target.checked);
    persist('animations', e.target.checked);
    showToast(e.target.checked ? '🎭' : '🚫', 'Анимации', e.target.checked ? 'Включены' : 'Выключены');
});

document.getElementById('resetBtn').addEventListener('click', async () => {
    const confirmed = await showConfirm();
    if (!confirmed) return;
    localStorage.removeItem('wt_settings');
    localStorage.removeItem('wt_theme');
    showToast('✅', 'Настройки сброшены', 'Страница обновится через секунду');
    setTimeout(() => location.reload(), 1400);
});

initUI();