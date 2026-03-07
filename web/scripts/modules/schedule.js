const DAYS_ORDER = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс'];
const DAYS_FULL  = { Пн:'Понедельник',Вт:'Вторник',Ср:'Среда',Чт:'Четверг',Пт:'Пятница',Сб:'Суббота',Вс:'Воскресенье' };
const DAY_EMOJIS = { Пн:'🔵',Вт:'🟢',Ср:'🟡',Чт:'🟠',Пт:'🔴',Сб:'🟣',Вс:'⚪' };
const QUICK_EX   = ['Отдых','Подтягивания','Отжимания','Приседания','Пресс','Планка','Выпады','Бег','Растяжка'];

const active   = DB.getActiveProfile();
let schedule   = active ? DB.getSchedule(active) : JSON.parse(JSON.stringify(DB.DEFAULT_SCHEDULE));
let editingDay = null;

function renderSchedule() {
    const grid = document.getElementById('scheduleGrid');
    grid.innerHTML = '';

    const days = DAYS_ORDER.filter(d => d in schedule);
    if (!days.length) {
        grid.innerHTML = '<p style="color:var(--text-muted);font-size:14px;padding:40px;text-align:center">📭 Расписание пусто. Нажмите «Добавить день»</p>';
        return;
    }

    days.forEach(day => {
        const exercises = schedule[day];
        const isRest = !exercises.length || (exercises.length===1 && exercises[0].toLowerCase().trim()==='отдых');
        const isSun  = day==='Сб' || day==='Вс';

        const card = document.createElement('div');
        card.className = 'day-card ' + (isRest ? 'rest' : isSun ? 'sun' : 'train');

        const exHTML = isRest
            ? '<span class="rest-label">😴 Отдых</span>'
            : exercises.map(ex => `<div class="ex-item"><span class="arrow">▸</span><span>${ex}</span></div>`).join('');

        card.innerHTML = `
            <div class="day-header">${DAYS_FULL[day]}</div>
            <div class="day-exercises">${exHTML}</div>
            <div class="day-actions">
                <button class="day-edit-btn" onclick="openEditDay('${day}')">✏️ Изменить</button>
                <button class="day-del-btn"  onclick="deleteDay(event,'${day}')">🗑️</button>
            </div>
        `;
        card.addEventListener('click', e => {
            if (e.target.closest('.day-actions')) return;
            openEditDay(day);
        });
        grid.appendChild(card);
    });
}

function openEditDay(day) {
    editingDay = day;
    document.getElementById('editDayTitle').textContent = `📝 ${day} — ${DAYS_FULL[day]}`;
    document.getElementById('editDayText').value = (schedule[day] || []).join('\n');

    const qb = document.getElementById('quickBtns');
    qb.innerHTML = '';
    QUICK_EX.forEach(ex => {
        const btn = document.createElement('button');
        btn.className   = 'quick-btn';
        btn.textContent = ex;
        btn.onclick = () => {
            const ta = document.getElementById('editDayText');
            if (ex.toLowerCase()==='отдых') { ta.value = 'Отдых'; return; }
            if (ta.value.trim().toLowerCase()==='отдых') ta.value = '';
            ta.value = (ta.value.trim() ? ta.value.trim()+'\n' : '') + ex;
        };
        qb.appendChild(btn);
    });
    openModal('editDayModal');
}

function saveDayEdit() {
    if (!editingDay) return;
    const raw = document.getElementById('editDayText').value.trim();
    schedule[editingDay] = raw ? raw.split('\n').map(l=>l.trim()).filter(Boolean) : ['Отдых'];
    if (active) DB.saveSchedule(active, schedule);
    renderSchedule();
    closeModal('editDayModal');
    showToast(`✅ День ${DAYS_FULL[editingDay]} обновлён!`);
}

async function deleteDay(e, day) {
    e.stopPropagation();
    const exercises = schedule[day] || [];
    const ok = await showConfirm({
        title:       `Удалить ${DAYS_FULL[day]}?`,
        message:     'Этот день будет удалён из расписания.',
        sub:         exercises.join(' · ') || 'Отдых',
        confirmText: '🗑️ Удалить',
        danger:      true,
    });
    if (!ok) return;
    delete schedule[day];
    if (active) DB.saveSchedule(active, schedule);
    renderSchedule();
    showToast(`🗑️ День ${DAYS_FULL[day]} удалён`);
}

function openAddDayModal() {
    const available = DAYS_ORDER.filter(d => !(d in schedule));
    if (!available.length) { showToast('✅ Все дни уже добавлены!'); return; }

    const radios = document.getElementById('addDayRadios');
    radios.innerHTML = '';
    available.forEach((d, i) => {
        const label = document.createElement('label');
        label.className = 'radio-item';
        label.innerHTML = `<input type="radio" name="addDay" value="${d}" ${i===0?'checked':''}> ${d} — ${DAYS_FULL[d]}`;
        radios.appendChild(label);
    });
    document.getElementById('addDayText').value = 'Отдых';
    openModal('addDayModal');
}

function saveNewDay() {
    const sel = document.querySelector('input[name="addDay"]:checked');
    if (!sel) return;
    const day = sel.value;
    const raw = document.getElementById('addDayText').value.trim();
    schedule[day] = raw ? raw.split('\n').map(l=>l.trim()).filter(Boolean) : ['Отдых'];
    if (active) DB.saveSchedule(active, schedule);
    renderSchedule();
    closeModal('addDayModal');
    showToast(`✅ День ${DAYS_FULL[day]} добавлен!`);
}

async function resetSchedule() {
    const ok = await showConfirm({
        title:       'Сбросить расписание?',
        message:     'Текущее расписание будет заменено стандартным.',
        confirmText: '🔄 Сбросить',
        danger:      false,
    });
    if (!ok) return;
    schedule = JSON.parse(JSON.stringify(DB.DEFAULT_SCHEDULE));
    if (active) DB.saveSchedule(active, schedule);
    renderSchedule();
    showToast('✅ Расписание сброшено!');
}

renderSchedule();