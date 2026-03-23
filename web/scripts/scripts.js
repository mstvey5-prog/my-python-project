// ===== ТЕМА =====
function applyTheme(theme) {
    document.body.className = theme;
    localStorage.setItem('wt_theme', theme);
}

function toggleTheme() {
    applyTheme(document.body.classList.contains('dark') ? 'light' : 'dark');
}

applyTheme(localStorage.getItem('wt_theme') || 'dark');

// ===== ПРИВЕТСТВИЯ =====
const GREETINGS = [
    'Привет',
    'Hello',
    'Hola',
    'Bonjour',
    'Ciao',
    'Hallo',
    '你好',
    'こんにちは',
    '안녕',
    'Aloha',
    'Olá'
];

let greetingIdx = 0;
let cursor = null;

function makeCursor() {
    cursor = document.createElement('span');
    cursor.className = 'cursor';
    return cursor;
}

function typeGreeting() {
    const el = document.getElementById('line1');
    const text = GREETINGS[greetingIdx];

    if (cursor) cursor.remove();
    el.appendChild(makeCursor());

    let charIdx = 0;
    const typeInterval = setInterval(() => {
        el.textContent = text.slice(0, charIdx + 1);
        el.appendChild(cursor);
        charIdx++;

        if (charIdx >= text.length) {
            clearInterval(typeInterval);
            setTimeout(() => eraseGreeting(el, text.length), 2200);
        }
    }, 95);
}

function eraseGreeting(el, length) {
    let charIdx = length;
    const eraseInterval = setInterval(() => {
        const text = GREETINGS[greetingIdx];
        el.textContent = text.slice(0, charIdx - 1);
        if (cursor && el.contains(cursor)) el.appendChild(cursor);
        charIdx--;

        if (charIdx <= 0) {
            clearInterval(eraseInterval);
            if (cursor) cursor.remove();
            greetingIdx = (greetingIdx + 1) % GREETINGS.length;
            setTimeout(typeGreeting, 500);
        }
    }, 70);
}

// ===== КАРТОЧКИ =====
const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
            setTimeout(() => entry.target.classList.add('visible'), i * 100);
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.module-card').forEach(c => observer.observe(c));

// ===== СТАРТ =====
window.addEventListener('load', () => {
    setTimeout(typeGreeting, 400);
});