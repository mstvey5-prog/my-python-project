// ===== ТЕМА =====
const themeToggle = document.getElementById('themeToggle');
const themeIcon   = document.getElementById('themeIcon');

function applyTheme(t) {
    document.body.className = t;
    themeIcon.textContent = t === 'dark' ? '☀️' : '🌙';
    localStorage.setItem('wt_theme', t);
}
themeToggle.addEventListener('click', () => {
    applyTheme(document.body.classList.contains('dark') ? 'light' : 'dark');
});
applyTheme(localStorage.getItem('wt_theme') || 'dark');

// ===== МОДАЛКИ =====
function openModal(id)  { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }
document.querySelectorAll('.modal-overlay').forEach(o => {
    o.addEventListener('click', e => { if (e.target === o) o.classList.remove('open'); });
});

// ===== ТОСТ =====
let toastTimer;
function showToast(msg, ok = true) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = 'toast show' + (ok ? '' : ' error');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove('show'), 2800);
}

// ===== СТИЛИЗОВАННЫЙ ДИАЛОГ ПОДТВЕРЖДЕНИЯ =====
function showConfirm({ title, message, sub = '', confirmText = 'Удалить', cancelText = 'Отмена', danger = true }) {
    return new Promise(resolve => {

        // убираем старый если есть
        document.getElementById('wt-confirm-overlay')?.remove();

        const overlay = document.createElement('div');
        overlay.id = 'wt-confirm-overlay';
        overlay.className = 'modal-overlay open';
        overlay.innerHTML = `
            <div class="confirm-dialog">
                <div class="confirm-icon">${danger ? '⚠️' : 'ℹ️'}</div>
                <h3 class="confirm-title">${title}</h3>
                <p class="confirm-message">${message}</p>
                ${sub ? `<p class="confirm-sub">${sub}</p>` : ''}
                <div class="confirm-actions">
                    <button class="confirm-cancel">${cancelText}</button>
                    <button class="confirm-ok ${danger ? 'confirm-danger' : 'confirm-primary'}">${confirmText}</button>
                </div>
            </div>
        `;

        overlay.querySelector('.confirm-cancel').addEventListener('click', () => {
            overlay.classList.remove('open');
            setTimeout(() => overlay.remove(), 200);
            resolve(false);
        });
        overlay.querySelector('.confirm-ok').addEventListener('click', () => {
            overlay.classList.remove('open');
            setTimeout(() => overlay.remove(), 200);
            resolve(true);
        });
        overlay.addEventListener('click', e => {
            if (e.target === overlay) {
                overlay.classList.remove('open');
                setTimeout(() => overlay.remove(), 200);
                resolve(false);
            }
        });

        document.body.appendChild(overlay);
    });
}