// ===== ПРОФИЛЬ =====
let selected = null;
let active   = DB.getActiveProfile();

function renderProfiles() {
    const list    = document.getElementById('profilesList');
    const profiles = DB.getProfiles();
    const names   = Object.keys(profiles);
    list.innerHTML = '';

    if (!names.length) {
        list.innerHTML = '<p style="font-size:13px;color:var(--text-muted);text-align:center;padding:16px 0">Профилей пока нет</p>';
        return;
    }

    names.forEach(name => {
        const p    = profiles[name];
        const item = document.createElement('div');
        item.className = 'profile-item' + (name === selected ? ' selected' : '');
        item.innerHTML = `
            <div class="p-avatar">${name.slice(0,2).toUpperCase()}</div>
            <div class="p-info">
                <span class="p-name">${name}</span>
                <span class="p-date">${p.last_used || 'Новый'}</span>
            </div>
            ${name === active ? '<span class="p-active-badge">●</span>' : ''}
        `;
        item.addEventListener('click', () => { selected = name; renderProfiles(); });
        item.addEventListener('dblclick', () => { selected = name; loginProfile(); });
        list.appendChild(item);
    });
}

function loginProfile() {
    if (!selected) { showToast('Выберите профиль!', false); return; }
    active = selected;
    DB.setActiveProfile(active);
    document.getElementById('activeProfileName').textContent = active;
    document.getElementById('statusLock').classList.add('hidden');
    document.getElementById('statusActive').classList.remove('hidden');
    document.getElementById('lockOverlay').style.display = 'none';
    loadProfileForm();
    renderProfiles();
    showToast(`✅ Добро пожаловать, ${active}!`);
}

function loadProfileForm() {
    if (!active) return;
    const p = DB.getProfile(active);
    if (!p) return;
    document.getElementById('fullName').value = p.full_name || '';
    document.getElementById('height').value   = p.height   || '';
    document.getElementById('weight').value   = p.weight   || '';
    document.querySelectorAll('.gender-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.val === p.gender);
    });
    updateBodyType();
}

function saveProfile() {
    if (!active) { showToast('Сначала войдите в профиль!', false); return; }
    const gBtn = document.querySelector('.gender-btn.active');
    DB.updateProfile(active, {
        full_name: document.getElementById('fullName').value.trim(),
        gender:    gBtn ? gBtn.dataset.val : '',
        height:    parseFloat(document.getElementById('height').value) || 0,
        weight:    parseFloat(document.getElementById('weight').value) || 0,
    });
    renderProfiles();
    showToast('💾 Профиль сохранён!');
}

function selectGender(btn) {
    document.querySelectorAll('.gender-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
}

function updateBodyType() {
    const w    = parseFloat(document.getElementById('weight').value);
    const h    = parseFloat(document.getElementById('height').value);
    const val  = document.getElementById('bodyTypeVal');
    const fill = document.getElementById('bodyTypeFill');
    const bmiSection = document.getElementById('bmiSection');

    if (isNaN(w) || w <= 0) {
        val.textContent = '—'; fill.style.width = '0%';
        bmiSection.style.display = 'none'; return;
    }

    let label, pct;
    if (w <= 65)      { label = '🏃 Худощавое'; pct = 25; }
    else if (w <= 85) { label = '💪 Среднее';   pct = 60; }
    else              { label = '🐻 Крупное';   pct = 90; }
    val.textContent  = label;
    fill.style.width = pct + '%';

    if (h > 0) {
        const bmi = w / ((h / 100) ** 2);
        document.getElementById('bmiValue').textContent = bmi.toFixed(1);
        bmiSection.style.display = 'block';

        let bmiLabel;
        if      (bmi < 16)   bmiLabel = 'Выраженный дефицит массы';
        else if (bmi < 18.5) bmiLabel = 'Недостаточная масса тела';
        else if (bmi < 25)   bmiLabel = '✅ Норма';
        else if (bmi < 30)   bmiLabel = 'Избыточная масса тела';
        else if (bmi < 35)   bmiLabel = 'Ожирение I степени';
        else                 bmiLabel = 'Ожирение II+ степени';

        document.getElementById('bmiLabel').textContent = bmiLabel;
        const pctBmi = Math.min(Math.max((bmi - 16) / 24 * 100, 0), 100);
        document.getElementById('bmiPointer').style.left = pctBmi + '%';
    }
}

function openCreateModal() {
    document.getElementById('newProfileName').value = '';
    openModal('createModal');
    setTimeout(() => document.getElementById('newProfileName').focus(), 100);
}

function createProfile() {
    const name = document.getElementById('newProfileName').value.trim();
    if (!name) { showToast('Введите имя профиля!', false); return; }

    const result = DB.createProfile(name);
    if (!result.ok) {
        showToast(result.error, false);
        // подсвечиваем инпут
        const input = document.getElementById('newProfileName');
        input.style.borderColor = 'var(--danger)';
        setTimeout(() => input.style.borderColor = '', 1500);
        return;
    }

    selected = name;
    renderProfiles();
    closeModal('createModal');
    showToast(`✅ Профиль «${name}» создан!`);
}

async function deleteProfile() {
    if (!selected) { showToast('Выберите профиль!', false); return; }
    if (selected === active) { showToast('Нельзя удалить активный профиль!', false); return; }

    const ok = await showConfirm({
        title:       'Удалить профиль?',
        message:     `Все данные профиля будут безвозвратно удалены.`,
        sub:         `👤 ${selected}`,
        confirmText: '🗑️ Удалить',
        danger:      true,
    });
    if (!ok) return;

    DB.deleteProfile(selected);
    selected = null;
    renderProfiles();
    showToast('🗑️ Профиль удалён');
}

// ИНИЦИАЛИЗАЦИЯ
renderProfiles();
if (active && DB.profileExists(active)) {
    document.getElementById('activeProfileName').textContent = active;
    document.getElementById('statusLock').classList.add('hidden');
    document.getElementById('statusActive').classList.remove('hidden');
    document.getElementById('lockOverlay').style.display = 'none';
    loadProfileForm();
}