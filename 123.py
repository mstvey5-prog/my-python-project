import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import json
import re

class WorkoutTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("💪 Тренировочный журнал")
        self.root.configure(bg="#1a1a2e")

        # Цветовая палитра
        self.colors = {
            "bg_dark": "#1a1a2e",
            "bg_medium": "#16213e",
            "bg_light": "#0f3460",
            "bg_card": "#1f2940",
            "bg_input": "#2a3a5c",
            "accent": "#e94560",
            "accent_hover": "#ff6b81",
            "success": "#00b894",
            "success_hover": "#00d2a0",
            "warning": "#fdcb6e",
            "danger": "#d63031",
            "danger_hover": "#e17055",
            "text_primary": "#ffffff",
            "text_secondary": "#a0aec0",
            "text_accent": "#74b9ff",
            "text_muted": "#636e72",
            "border": "#2d3748",
            "highlight": "#6c5ce7",
            "highlight_hover": "#a29bfe",
            "rest_day": "#2d3436",
            "train_day": "#0f3460",
            "sunday": "#2d1f3d",
        }

        self.db_path = "123.db"
        self.init_database()
        self.current_profile = None
        self.profiles = self.load_profiles_list()
        self.is_locked = True
        self.no_profile_frame = None
        self.schedule = {}
        self.workouts = []
        self.profile = {}
        self.profile_entries = {}
        self.body_type_var = tk.StringVar(value="")
        self.schedule_buttons = {}
        self.grouped_view = tk.BooleanVar(value=True)

        self.setup_styles()
        self.create_profile_selector()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=(5, 10))

        self.tab_add = tk.Frame(self.notebook, bg=self.colors["bg_dark"])
        self.notebook.add(self.tab_add, text=" ➕ Добавить ")

        self.tab_view = tk.Frame(self.notebook, bg=self.colors["bg_dark"])
        self.notebook.add(self.tab_view, text=" 📋 Тренировки ")

        self.tab_schedule = tk.Frame(self.notebook, bg=self.colors["bg_dark"])
        self.notebook.add(self.tab_schedule, text=" 📅 Расписание ")

        self.tab_profile = tk.Frame(self.notebook, bg=self.colors["bg_dark"])
        self.notebook.add(self.tab_profile, text=" 👤 Профиль ")

        self.setup_add_tab()
        self.setup_view_tab()
        self.setup_schedule_tab()
        self.setup_profile_tab()

        self.refresh_profiles()
        self.lock_interface()

  
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=self.colors["bg_medium"],
                        foreground=self.colors["text_primary"],
                        fieldbackground=self.colors["bg_medium"],
                        borderwidth=0,
                        font=("Segoe UI", 10),
                        rowheight=30)
        style.configure("Treeview.Heading",
                        background=self.colors["bg_light"],
                        foreground=self.colors["text_accent"],
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0)
        style.map("Treeview",
                  background=[("selected", self.colors["highlight"])],
                  foreground=[("selected", "white")])
        style.configure("TNotebook",
                        background=self.colors["bg_dark"],
                        borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=self.colors["bg_medium"],
                        foreground=self.colors["text_secondary"],
                        padding=[15, 8],
                        font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", self.colors["bg_light"])],
                  foreground=[("selected", self.colors["text_accent"])])
        style.configure("TScrollbar",
                        background=self.colors["bg_medium"],
                        troughcolor=self.colors["bg_dark"],
                        borderwidth=0)

    def create_styled_button(self, parent, text, command, bg=None, fg=None,
                             hover_bg=None, font_size=10, width=None, height=None,
                             bold=True, padx=15, pady=8):
        bg = bg or self.colors["accent"]
        fg = fg or self.colors["text_primary"]
        hover_bg = hover_bg or self.colors["accent_hover"]
        font_style = ("Segoe UI", font_size, "bold") if bold else ("Segoe UI", font_size)
        btn = tk.Button(parent, text=text, command=command,
                        bg=bg, fg=fg, font=font_style,
                        activebackground=hover_bg, activeforeground=fg,
                        bd=0, relief=tk.FLAT, cursor="hand2",
                        padx=padx, pady=pady)
        if width:
            btn.config(width=width)
        if height:
            btn.config(height=height)
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    def create_styled_entry(self, parent, width=25, font_size=11, justify=tk.LEFT):
        entry = tk.Entry(parent,
                         bg=self.colors["bg_input"],
                         fg=self.colors["text_primary"],
                         insertbackground=self.colors["text_accent"],
                         font=("Segoe UI", font_size),
                         width=width,
                         bd=0,
                         relief=tk.FLAT,
                         justify=justify)
        entry.config(highlightbackground=self.colors["border"],
                     highlightcolor=self.colors["text_accent"],
                     highlightthickness=1)
        return entry

    def create_section_label(self, parent, text, font_size=16):
        return tk.Label(parent, text=text,
                        font=("Segoe UI", font_size, "bold"),
                        bg=self.colors["bg_dark"],
                        fg=self.colors["text_accent"])

    def create_field_label(self, parent, text, font_size=11):
        return tk.Label(parent, text=text,
                        bg=self.colors["bg_dark"],
                        fg=self.colors["text_secondary"],
                        font=("Segoe UI", font_size))

    def validate_time_format(self, time_str):
        time_str = time_str.strip()
        if not time_str:
            return False, "Время не может быть пустым!"
        pattern = r'^(\d{1,2}):(\d{2})$'
        match = re.match(pattern, time_str)
        if not match:
            return False, "Неверный формат! Используйте ЧЧ:ММ"
        hours = int(match.group(1))
        minutes = int(match.group(2))
        if hours < 0 or hours > 23:
            return False, f"Часы от 0 до 23"
        if minutes < 0 or minutes > 59:
            return False, f"Минуты от 0 до 59"
        formatted = f"{hours:02d}:{minutes:02d}"
        return True, formatted

    def get_current_time_str(self):
        return datetime.now().strftime("%H:%M")

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                name TEXT PRIMARY KEY,
                full_name TEXT,
                gender TEXT,
                height TEXT,
                weight REAL,
                age INTEGER,
                bmi REAL,
                last_used TEXT,
                workouts TEXT,
                schedule TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def create_profile_selector(self):
        self.profile_selector_frame = tk.Frame(self.root, bg=self.colors["bg_medium"], bd=0)
        self.profile_selector_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        title_frame = tk.Frame(self.profile_selector_frame, bg=self.colors["bg_light"])
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="👤 Выбор пользователя",
                 bg=self.colors["bg_light"], fg=self.colors["text_accent"],
                 font=("Segoe UI", 13, "bold")).pack(pady=8, padx=15, anchor=tk.W)

        content_frame = tk.Frame(self.profile_selector_frame, bg=self.colors["bg_medium"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        list_frame = tk.Frame(content_frame, bg=self.colors["bg_medium"])
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "last_used")
        self.profiles_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=3)
        self.profiles_tree.heading("name", text="📛 Имя профиля")
        self.profiles_tree.heading("last_used", text="🕐 Последний вход")
        self.profiles_tree.column("name", width=300)
        self.profiles_tree.column("last_used", width=200)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.profiles_tree.yview)
        self.profiles_tree.configure(yscrollcommand=scrollbar.set)
        self.profiles_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self.profile_selector_frame, bg=self.colors["bg_medium"])
        btn_frame.pack(pady=(0, 10))

        self.login_btn = self.create_styled_button(
            btn_frame, "✅ Войти", self.login_profile,
            bg=self.colors["success"], hover_bg=self.colors["success_hover"],
            width=14)
        self.login_btn.pack(side=tk.LEFT, padx=5)
        self.login_btn.config(state=tk.DISABLED)

        self.create_btn = self.create_styled_button(
            btn_frame, "➕ Создать", self.create_new_profile,
            bg=self.colors["highlight"], hover_bg=self.colors["highlight_hover"],
            width=14)
        self.create_btn.pack(side=tk.LEFT, padx=5)

        self.delete_btn = self.create_styled_button(
            btn_frame, "🗑️ Удалить", self.delete_profile,
            bg=self.colors["danger"], hover_bg=self.colors["danger_hover"],
            width=14)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn.config(state=tk.DISABLED)

        self.profiles_tree.bind("<<TreeviewSelect>>", self.on_profile_select)
        self.profiles_tree.bind("<Double-1>", self.on_profile_double_click)

    def load_profiles_list(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM profiles")
        profiles = [row[0] for row in cursor.fetchall()]
        conn.close()
        return profiles

    def refresh_profiles(self):
        for item in self.profiles_tree.get_children():
            self.profiles_tree.delete(item)
        self.profiles = self.load_profiles_list()
        for profile_name in self.profiles:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT last_used FROM profiles WHERE name = ?", (profile_name,))
            result = cursor.fetchone()
            conn.close()
            last_used = result[0] if result and result[0] else "Неизвестно"
            self.profiles_tree.insert("", tk.END, values=(profile_name, last_used))
        if self.profiles:
            self.profiles_tree.selection_set(self.profiles_tree.get_children()[0])
            self.on_profile_select()

    def on_profile_select(self, event=None):
        selected = self.profiles_tree.selection()
        if selected:
            self.login_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.login_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)

    def on_profile_double_click(self, event):
        self.login_profile()

    def login_profile(self):
        selected = self.profiles_tree.selection()
        if not selected:
            messagebox.showwarning("❌ Ошибка", "Выберите профиль!")
            return
        profile_name = self.profiles_tree.item(selected[0])['values'][0]
        self.current_profile = profile_name
        self.load_profile_data()
        self.update_last_used()
        self.unlock_interface()
        self.root.title(f"💪 Тренировочный журнал — {profile_name}")
        messagebox.showinfo("✅ Вход выполнен", f"Добро пожаловать, {profile_name}!")

    def update_last_used(self):
        if self.current_profile:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE profiles SET last_used = ? WHERE name = ?",
                (datetime.now().strftime("%d.%m.%Y %H:%M"), self.current_profile)
            )
            conn.commit()
            conn.close()

    def lock_interface(self):
        self.is_locked = True
        for i in range(4):
            self.notebook.tab(i, state="disabled")
        if not self.no_profile_frame:
            self.no_profile_frame = tk.Frame(self.root, bg=self.colors["bg_dark"])
            self.no_profile_frame.place(relx=0.5, rely=0.65, anchor="center")
            lock_card = tk.Frame(self.no_profile_frame, bg=self.colors["bg_card"],
                                 highlightbackground=self.colors["border"],
                                 highlightthickness=1)
            lock_card.pack(padx=30, pady=20)
            tk.Label(lock_card, text="🔒",
                     font=("Segoe UI", 48),
                     bg=self.colors["bg_card"], fg=self.colors["accent"]).pack(pady=(20, 5))
            tk.Label(lock_card,
                     text="Создайте или выберите профиль",
                     font=("Segoe UI", 16, "bold"),
                     bg=self.colors["bg_card"], fg=self.colors["text_primary"]).pack(pady=5)
            tk.Label(lock_card,
                     text="• Выберите профиль из списка и нажмите «Войти»\n"
                          "• Или создайте новый профиль кнопкой «Создать»",
                     font=("Segoe UI", 11),
                     bg=self.colors["bg_card"], fg=self.colors["text_secondary"],
                     justify=tk.CENTER).pack(pady=(5, 20), padx=30)

    def unlock_interface(self):
        self.is_locked = False
        for i in range(4):
            self.notebook.tab(i, state="normal")
        if self.no_profile_frame:
            self.no_profile_frame.destroy()
            self.no_profile_frame = None

    def require_profile(self):
        if self.is_locked or not self.current_profile:
            messagebox.showwarning("❌ Требуется профиль", "Сначала войдите в профиль!")
            return False
        return True

    def create_new_profile(self):
        name = simpledialog.askstring("Новый профиль", "Введите имя профиля:", parent=self.root)
        if name and name.strip():
            name = name.strip()
            if name not in self.profiles:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO profiles (name, last_used)
                    VALUES (?, ?)
                ''', (name, datetime.now().strftime("%d.%m.%Y %H:%M")))
                conn.commit()
                conn.close()
                self.profiles.append(name)
                self.current_profile = name
                self.profile = {"full_name": "", "gender": "", "height": "", "weight": "", "age": "", "bmi": ""}
                self.workouts = []
                self.schedule = {}
                self.save_profile_data()
                self.refresh_profiles()
                self.profiles_tree.selection_set(self.profiles_tree.get_children()[-1])
                self.login_profile()
                messagebox.showinfo("✅ Успех", f"Профиль «{name}» создан и активирован.")
            else:
                messagebox.showwarning("❌ Ошибка", "Профиль с таким именем уже существует.")

    def delete_profile(self):
        selected = self.profiles_tree.selection()
        if not selected:
            return
        profile_name = self.profiles_tree.item(selected[0])['values'][0]
        if profile_name == self.current_profile:
            messagebox.showwarning("❌ Ошибка", "Нельзя удалить активный профиль!")
            return
        if messagebox.askyesno("Удалить", f"Удалить профиль «{profile_name}»?\nВсе данные будут потеряны!"):
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM profiles WHERE name = ?", (profile_name,))
                conn.commit()
                conn.close()
                self.refresh_profiles()
                if self.profiles:
                    self.profiles_tree.selection_set(self.profiles_tree.get_children()[0])
                    self.on_profile_select()
                else:
                    self.current_profile = None
                    self.lock_interface()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить профиль:\n{str(e)}")

    def load_profile_data(self):
        if not self.current_profile:
            return
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT full_name, gender, height, weight, age, bmi, workouts, schedule, last_used
            FROM profiles WHERE name = ?
        ''', (self.current_profile,))
        result = cursor.fetchone()
        conn.close()

        if result:
            self.profile = {
                "full_name": result[0] or "",
                "gender": result[1] or "",
                "height": result[2] or "",
                "weight": result[3] or "",
                "age": result[4] if result[4] is not None else "",
                "bmi": float(result[5]) if result[5] is not None else None
            }
            temp_workouts = result[6]
            self.workouts = json.loads(temp_workouts) if temp_workouts else []
            temp_schedule = result[7]
            try:
                sch = json.loads(temp_schedule)
                self.schedule = sch if isinstance(sch, dict) else {}
            except (json.JSONDecodeError, TypeError):
                self.schedule = {}
        else:
            self.profile = {"full_name": "", "gender": "", "height": "", "weight": "", "age": "", "bmi": ""}
            self.workouts = []
            self.schedule = {}

        for w in self.workouts:
            if "time" not in w:
                w["time"] = "--:--"

        self.refresh_workouts()
        self.display_schedule()
        self.load_profile_to_form()

        if self.profile["bmi"] is not None:
            self.calculate_and_show_bmi(use_saved=True)

    def save_profile_data(self, empty=False):
            if not self.current_profile:
                return
            conn = self.get_db_connection()
            cursor = conn.cursor()

            weight_val = self.profile.get("weight", "")
            if isinstance(weight_val, str) and weight_val.replace('.', '', 1).replace('-', '', 1).isdigit():
                weight_val = float(weight_val)
            elif isinstance(weight_val, (int, float)):
                weight_val = float(weight_val)
            else:
                weight_val = 0.0

            age_val = self.profile.get("age", "")
            if age_val and str(age_val).isdigit():
                age_val = int(age_val)
            else:
                age_val = None

            # Самое важное исправление здесь ↓↓↓
            bmi_val = self.profile.get("bmi")
            if bmi_val is not None and bmi_val != "":
                try:
                    bmi_val = float(bmi_val)
                except (ValueError, TypeError):
                    bmi_val = None
            else:
                bmi_val = None  # если ключа нет или пусто → NULL в базе

            cursor.execute('''
                INSERT OR REPLACE INTO profiles
                (name, full_name, gender, height, weight, age, bmi, workouts, schedule, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.current_profile,
                self.profile.get("full_name", ""),
                self.profile.get("gender", ""),
                self.profile.get("height", ""),
                weight_val,
                age_val,
                bmi_val,
                json.dumps(self.workouts, ensure_ascii=False),
                json.dumps(self.schedule, ensure_ascii=False),
                datetime.now().strftime("%d.%m.%Y %H:%M")
            ))
            conn.commit()
            conn.close()
    
    def time_to_minutes(self, time_str):
        try:
            parts = time_str.strip().split(":")
            return int(parts[0]) * 60 + int(parts[1])
        except (ValueError, IndexError):
            return 9999

    def group_workouts_by_day_and_exercise(self):
        grouped = {}
        for workout in self.workouts:
            day = workout.get("date", "")
            time_val = workout.get("time", "--:--")
            exercise = workout.get("exercise", "")
            sets = workout.get("sets", 0)
            reps = workout.get("reps", 0)
            weight = workout.get("weight", 0.0)
            key = (day, exercise)
            if key not in grouped:
                grouped[key] = {
                    "date": day,
                    "exercise": exercise,
                    "sessions": [],
                    "total_sets": 0,
                    "total_reps": 0,
                    "weights": [],
                    "times": [],
                }
            grouped[key]["sessions"].append({
                "time": time_val, "sets": sets, "reps": reps, "weight": weight
            })
            grouped[key]["total_sets"] += sets
            grouped[key]["total_reps"] += reps
            grouped[key]["weights"].append(weight)
            grouped[key]["times"].append(time_val)

        for key in grouped:
            paired = list(zip(grouped[key]["times"], grouped[key]["weights"]))
            paired.sort(key=lambda p: self.time_to_minutes(p[0]))
            grouped[key]["times"] = [p[0] for p in paired]
            grouped[key]["weights"] = [p[1] for p in paired]
            grouped[key]["sessions"].sort(key=lambda s: self.time_to_minutes(s["time"]))
        return grouped

    def format_grouped_weight(self, weights):
        unique_weights = set(weights)
        if len(unique_weights) == 1:
            w = weights[0]
            return str(int(w)) if w == int(w) else str(w)
        else:
            formatted = []
            for w in weights:
                formatted.append(str(int(w)) if w == int(w) else str(w))
            return " / ".join(formatted)

    def format_grouped_times(self, times):
        seen = []
        for t in times:
            if t not in seen:
                seen.append(t)
        return " / ".join(seen)

    def setup_add_tab(self):
        outer = tk.Frame(self.tab_add, bg=self.colors["bg_dark"])
        outer.pack(expand=True, fill=tk.BOTH)

        card = tk.Frame(outer, bg=self.colors["bg_card"],
                        highlightbackground=self.colors["border"],
                        highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center")

        inner = tk.Frame(card, bg=self.colors["bg_card"])
        inner.pack(padx=30, pady=25)

        self.create_section_label(inner, "➕ Новая тренировка", 18).grid(
            row=0, column=0, columnspan=3, pady=(0, 20))

        self.create_field_label(inner, "📅 Дата:").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.date_entry = self.create_styled_entry(inner)
        self.date_entry.grid(row=1, column=1, padx=(10, 0), pady=6, sticky=tk.W, columnspan=2)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.create_field_label(inner, "🕐 Время:").grid(row=2, column=0, sticky=tk.W, pady=6)
        time_frame = tk.Frame(inner, bg=self.colors["bg_card"])
        time_frame.grid(row=2, column=1, padx=(10, 0), pady=6, sticky=tk.W, columnspan=2)
        self.time_entry = self.create_styled_entry(time_frame, width=7, font_size=13, justify=tk.CENTER)
        self.time_entry.pack(side=tk.LEFT)
        self.time_entry.insert(0, self.get_current_time_str())
        self.create_styled_button(time_frame, "⏱ Сейчас", self.insert_current_time,
                                  bg=self.colors["bg_light"], hover_bg=self.colors["highlight"],
                                  font_size=9, padx=8, pady=4).pack(side=tk.LEFT, padx=(8, 0))
        tk.Label(time_frame, text="(ЧЧ:ММ)", bg=self.colors["bg_card"],
                 fg=self.colors["text_muted"], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=8)

        self.create_field_label(inner, "🏋️ Упражнение:").grid(row=3, column=0, sticky=tk.W, pady=6)
        self.exercise_entry = self.create_styled_entry(inner)
        self.exercise_entry.grid(row=3, column=1, padx=(10, 0), pady=6, sticky=tk.W, columnspan=2)

        self.create_field_label(inner, "🔁 Подходы:").grid(row=4, column=0, sticky=tk.W, pady=6)
        self.sets_entry = self.create_styled_entry(inner, width=10)
        self.sets_entry.grid(row=4, column=1, padx=(10, 0), pady=6, sticky=tk.W)

        self.create_field_label(inner, "🔢 Повторения:").grid(row=5, column=0, sticky=tk.W, pady=6)
        self.reps_entry = self.create_styled_entry(inner, width=10)
        self.reps_entry.grid(row=5, column=1, padx=(10, 0), pady=6, sticky=tk.W)

        self.create_field_label(inner, "⚖️ Вес (кг):").grid(row=6, column=0, sticky=tk.W, pady=6)
        self.weight_entry = self.create_styled_entry(inner, width=10)
        self.weight_entry.grid(row=6, column=1, padx=(10, 0), pady=6, sticky=tk.W)

        btn = self.create_styled_button(inner, "✅ Добавить тренировку", self.add_workout,
                                        bg=self.colors["success"], hover_bg=self.colors["success_hover"],
                                        font_size=13, width=28)
        btn.grid(row=7, column=0, columnspan=3, pady=(20, 0))

    def insert_current_time(self):
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, self.get_current_time_str())

    def add_workout(self):
        if not self.require_profile():
            return
        date = self.date_entry.get()
        time_raw = self.time_entry.get()
        exercise = self.exercise_entry.get().strip()
        sets = self.sets_entry.get()
        reps = self.reps_entry.get()
        weight = self.weight_entry.get()

        if not exercise:
            messagebox.showwarning("Ошибка", "Упражнение обязательно для заполнения!")
            return

        is_valid, result = self.validate_time_format(time_raw)
        if not is_valid:
            messagebox.showwarning("❌ Неверное время", result)
            self.time_entry.focus_set()
            self.time_entry.select_range(0, tk.END)
            return
        time_formatted = result

        workout = {
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "time": time_formatted,
            "exercise": exercise,
            "sets": int(sets) if sets.isdigit() else 0,
            "reps": int(reps) if reps.isdigit() else 0,
            "weight": float(weight) if weight.replace('.', '', 1).isdigit() else 0.0
        }

        self.workouts.append(workout)
        self.save_profile_data()
        self.refresh_workouts()
        messagebox.showinfo("✅ Успех", f"Тренировка добавлена! ({time_formatted})")

        self.exercise_entry.delete(0, tk.END)
        self.sets_entry.delete(0, tk.END)
        self.reps_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, self.get_current_time_str())

    def setup_view_tab(self):
        top_frame = tk.Frame(self.tab_view, bg=self.colors["bg_dark"])
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        self.create_section_label(top_frame, "📋 Мои тренировки", 14).pack(side=tk.LEFT)

        self.view_toggle_btn = self.create_styled_button(
            top_frame, "📊 Группировка: ВКЛ", self.toggle_view_mode,
            bg=self.colors["highlight"], hover_bg=self.colors["highlight_hover"],
            font_size=9, width=22)
        self.view_toggle_btn.pack(side=tk.RIGHT)

        tree_frame = tk.Frame(self.tab_view, bg=self.colors["bg_dark"])
        tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=(0, 5))

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("date", "time", "exercise", "sets", "reps", "weight"),
            show="headings"
        )
        self.tree.heading("date", text="📅 Дата")
        self.tree.heading("time", text="🕐 Время")
        self.tree.heading("exercise", text="🏋️ Упражнение")
        self.tree.heading("sets", text="🔁 Подходы")
        self.tree.heading("reps", text="🔢 Повторения")
        self.tree.heading("weight", text="⚖️ Вес (кг)")

        # ИСПРАВЛЕНИЕ: добавлено выравнивание по центру для всех столбцов кроме "exercise"
        self.tree.column("date", width=110, anchor=tk.CENTER)
        self.tree.column("time", width=130, anchor=tk.CENTER)
        self.tree.column("exercise", width=200, anchor=tk.W)
        self.tree.column("sets", width=100, anchor=tk.CENTER)
        self.tree.column("reps", width=100, anchor=tk.CENTER)
        self.tree.column("weight", width=130, anchor=tk.CENTER)

        self.tree.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        button_frame = tk.Frame(self.tab_view, bg=self.colors["bg_dark"])
        button_frame.pack(pady=8)

        self.create_styled_button(button_frame, "🗑️ Удалить", self.delete_workout,
                                  bg=self.colors["danger"], hover_bg=self.colors["danger_hover"],
                                  font_size=10).pack(side=tk.LEFT, padx=5)
        self.create_styled_button(button_frame, "✏️ Редактировать", self.edit_workout,
                                  bg=self.colors["bg_light"], hover_bg=self.colors["highlight"],
                                  font_size=10).pack(side=tk.LEFT, padx=5)
        self.create_styled_button(button_frame, "🔄 Обновить", self.refresh_workouts,
                                  bg=self.colors["bg_light"], hover_bg=self.colors["highlight"],
                                  font_size=10).pack(side=tk.LEFT, padx=5)

        self.info_label = tk.Label(
            self.tab_view,
            text="💡 Одинаковые упражнения за день объединяются. "
                 "Подходы и повторения суммированы.",
            bg=self.colors["bg_dark"], fg=self.colors["text_muted"],
            font=("Segoe UI", 9), wraplength=800)
        self.info_label.pack(pady=(0, 8))

    def toggle_view_mode(self):
        current = self.grouped_view.get()
        self.grouped_view.set(not current)
        if self.grouped_view.get():
            self.view_toggle_btn.config(text="📊 Группировка: ВКЛ",
                                        bg=self.colors["highlight"])
            self.info_label.config(
                text="💡 Одинаковые упражнения за день объединяются. "
                     "Подходы и повторения суммированы.")
        else:
            self.view_toggle_btn.config(text="📋 Группировка: ВЫКЛ",
                                        bg=self.colors["text_muted"])
            self.info_label.config(text="📋 Все записи без группировки.")
        self.refresh_workouts()

    def refresh_workouts(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if self.grouped_view.get():
            grouped = self.group_workouts_by_day_and_exercise()
            sorted_keys = sorted(grouped.keys(), key=lambda k: k[0])
            for key in sorted_keys:
                data = grouped[key]
                times_str = self.format_grouped_times(data["times"])
                weight_str = self.format_grouped_weight(data["weights"])
                session_count = len(data["sessions"])
                if session_count > 1:
                    sets_display = f"Σ {data['total_sets']}"
                    reps_display = f"Σ {data['total_reps']}"
                else:
                    sets_display = str(data["total_sets"])
                    reps_display = str(data["total_reps"])
                self.tree.insert("", tk.END, values=(
                    data["date"], times_str, data["exercise"],
                    sets_display, reps_display, weight_str
                ))
        else:
            for w in self.workouts:
                weight_val = w.get("weight", 0)
                weight_display = str(int(weight_val)) if weight_val == int(weight_val) else str(weight_val)
                time_display = w.get("time", "--:--")
                self.tree.insert("", tk.END, values=(
                    w["date"], time_display, w["exercise"],
                    w["sets"], w["reps"], weight_display
                ))

    def delete_workout(self):
        if not self.require_profile():
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите тренировку!")
            return

        if self.grouped_view.get():
            item = self.tree.item(selected[0])
            values = item['values']
            target_date = str(values[0])
            target_exercise = str(values[2])
            matching = [i for i, w in enumerate(self.workouts)
                        if w["date"] == target_date and w["exercise"] == target_exercise]
            if not matching:
                messagebox.showwarning("Ошибка", "Записи не найдены!")
                return
            count = len(matching)
            if messagebox.askyesno("Удалить",
                                   f"Удалить все записи ({count} шт.) для\n"
                                   f"«{target_exercise}» за {target_date}?"):
                for i in sorted(matching, reverse=True):
                    del self.workouts[i]
                self.save_profile_data()
                self.refresh_workouts()
        else:
            index = self.tree.index(selected[0])
            if messagebox.askyesno("Удалить", "Удалить выбранную тренировку?"):
                del self.workouts[index]
                self.save_profile_data()
                self.refresh_workouts()

    def edit_workout(self):
        if not self.require_profile():
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите тренировку!")
            return

        if self.grouped_view.get():
            item = self.tree.item(selected[0])
            values = item['values']
            target_date = str(values[0])
            target_exercise = str(values[2])
            matching_indices = [i for i, w in enumerate(self.workouts)
                                if w["date"] == target_date and w["exercise"] == target_exercise]
            if len(matching_indices) == 1:
                self._open_edit_window(matching_indices[0])
            elif len(matching_indices) > 1:
                self._open_group_edit_selector(matching_indices, target_date, target_exercise)
            else:
                messagebox.showwarning("Ошибка", "Записи не найдены!")
        else:
            index = self.tree.index(selected[0])
            self._open_edit_window(index)

    def _open_group_edit_selector(self, indices, date, exercise):
        selector = tk.Toplevel(self.root)
        selector.title(f"Выберите запись")
        selector.configure(bg=self.colors["bg_dark"])
        selector.geometry("500x380")
        selector.transient(self.root)
        selector.grab_set()

        card = tk.Frame(selector, bg=self.colors["bg_card"])
        card.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)

        tk.Label(card,
                 text=f"📝 {exercise}\n📅 {date}",
                 bg=self.colors["bg_card"], fg=self.colors["text_accent"],
                 font=("Segoe UI", 13, "bold"),
                 justify=tk.CENTER).pack(pady=(15, 5))

        tk.Label(card, text="Выберите запись для редактирования:",
                 bg=self.colors["bg_card"], fg=self.colors["text_secondary"],
                 font=("Segoe UI", 10)).pack(pady=(0, 10))

        listbox = tk.Listbox(card, bg=self.colors["bg_input"], fg=self.colors["text_primary"],
                             font=("Segoe UI", 11), selectmode=tk.SINGLE,
                             selectbackground=self.colors["highlight"],
                             selectforeground="white", bd=0, relief=tk.FLAT,
                             highlightthickness=1,
                             highlightbackground=self.colors["border"])
        listbox.pack(expand=True, fill=tk.BOTH, padx=15, pady=5)

        for idx in indices:
            w = self.workouts[idx]
            time_str = w.get("time", "--:--")
            weight_val = w.get("weight", 0)
            weight_display = str(int(weight_val)) if weight_val == int(weight_val) else str(weight_val)
            listbox.insert(tk.END,
                           f" [{time_str}] {w['sets']} подх. × {w['reps']} — {weight_display} кг")

        def on_edit():
            sel = listbox.curselection()
            if sel:
                real_index = indices[sel[0]]
                selector.destroy()
                self._open_edit_window(real_index)
            else:
                messagebox.showwarning("Ошибка", "Выберите запись!", parent=selector)

        self.create_styled_button(card, "✏️ Редактировать", on_edit,
                                  bg=self.colors["success"], hover_bg=self.colors["success_hover"],
                                  font_size=11, width=22).pack(pady=15)

    def _open_edit_window(self, index):
        workout = self.workouts[index]
        edit_win = tk.Toplevel(self.root)
        edit_win.title("✏️ Редактировать тренировку")
        edit_win.configure(bg=self.colors["bg_dark"])
        edit_win.geometry("480x420")
        edit_win.transient(self.root)
        edit_win.grab_set()

        card = tk.Frame(edit_win, bg=self.colors["bg_card"],
                        highlightbackground=self.colors["border"], highlightthickness=1)
        card.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)

        inner = tk.Frame(card, bg=self.colors["bg_card"])
        inner.pack(padx=25, pady=20)

        tk.Label(inner, text="✏️ Редактирование", font=("Segoe UI", 15, "bold"),
                 bg=self.colors["bg_card"], fg=self.colors["text_accent"]).grid(
            row=0, column=0, columnspan=2, pady=(0, 15))

        fields_config = [
            ("📅 Дата:", workout["date"], "date"),
            ("🕐 Время:", workout.get("time", "--:--"), "time"),
            ("🏋️ Упражнение:", workout["exercise"], "exercise"),
            ("🔁 Подходы:", str(workout["sets"]), "sets"),
            ("🔢 Повторения:", str(workout["reps"]), "reps"),
            ("⚖️ Вес (кг):", str(workout["weight"]), "weight"),
        ]

        vars_dict = {}
        for i, (label_text, default_val, key) in enumerate(fields_config):
            tk.Label(inner, text=label_text, bg=self.colors["bg_card"],
                     fg=self.colors["text_secondary"], font=("Segoe UI", 11)).grid(
                row=i + 1, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar(value=default_val)
            entry = self.create_styled_entry(inner, width=20)
            entry.insert(0, default_val)
            entry.grid(row=i + 1, column=1, padx=(10, 0), pady=5)
            vars_dict[key] = (var, entry)

        def save_changes():
            time_raw = vars_dict["time"][1].get()
            is_valid, time_result = self.validate_time_format(time_raw)
            if not is_valid:
                messagebox.showwarning("❌ Неверное время", time_result, parent=edit_win)
                return

            exercise_val = vars_dict["exercise"][1].get().strip()
            if not exercise_val:
                messagebox.showwarning("Ошибка", "Упражнение обязательно!", parent=edit_win)
                return

            sets_val = vars_dict["sets"][1].get()
            reps_val = vars_dict["reps"][1].get()
            weight_val = vars_dict["weight"][1].get()

            updated = {
                "date": vars_dict["date"][1].get() or datetime.now().strftime("%Y-%m-%d"),
                "time": time_result,
                "exercise": exercise_val,
                "sets": int(sets_val) if sets_val.isdigit() else 0,
                "reps": int(reps_val) if reps_val.isdigit() else 0,
                "weight": float(weight_val) if weight_val.replace('.', '', 1).isdigit() else 0.0
            }

            self.workouts[index] = updated
            self.save_profile_data()
            self.refresh_workouts()
            edit_win.destroy()
            messagebox.showinfo("✅ Успех", "Тренировка обновлена!")

        self.create_styled_button(inner, "💾 Сохранить", save_changes,
                                  bg=self.colors["success"], hover_bg=self.colors["success_hover"],
                                  font_size=12, width=20).grid(row=8, column=0, columnspan=2, pady=(15, 0))

    def setup_schedule_tab(self):
        frame = tk.Frame(self.tab_schedule, bg=self.colors["bg_dark"])
        frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        top_frame = tk.Frame(frame, bg=self.colors["bg_dark"])
        top_frame.pack(fill=tk.X, pady=(0, 10))

        self.create_section_label(top_frame, "📅 Расписание тренировок", 16).pack(side=tk.LEFT)

        ctrl_frame = tk.Frame(top_frame, bg=self.colors["bg_dark"])
        ctrl_frame.pack(side=tk.RIGHT)

        self.create_styled_button(ctrl_frame, "➕ Добавить день", self.add_schedule_day,
                                  bg=self.colors["highlight"], hover_bg=self.colors["highlight_hover"],
                                  font_size=9).pack(side=tk.LEFT, padx=3)

        self.create_styled_button(ctrl_frame, "🔄 Сбросить", self.reset_schedule,
                                  bg=self.colors["bg_light"], hover_bg=self.colors["accent"],
                                  font_size=9).pack(side=tk.LEFT, padx=3)

        tk.Label(frame,
                 text="Нажмите на карточку дня для редактирования упражнений",
                 bg=self.colors["bg_dark"], fg=self.colors["text_muted"],
                 font=("Segoe UI", 10)).pack(pady=(0, 10))

        self.schedule_canvas = tk.Canvas(frame, bg=self.colors["bg_dark"],
                                         highlightthickness=0)
        self.schedule_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL,
                                                command=self.schedule_canvas.yview)
        self.schedule_scroll_frame = tk.Frame(self.schedule_canvas, bg=self.colors["bg_dark"])

        self.schedule_scroll_frame.bind(
            "<Configure>",
            lambda e: self.schedule_canvas.configure(scrollregion=self.schedule_canvas.bbox("all"))
        )

        self.schedule_canvas.create_window((0, 0), window=self.schedule_scroll_frame, anchor="nw")
        self.schedule_canvas.configure(yscrollcommand=self.schedule_scrollbar.set)

        self.schedule_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.schedule_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.schedule_canvas.bind_all("<MouseWheel>",
                                      lambda e: self.schedule_canvas.yview_scroll(
                                          int(-1 * (e.delta / 120)), "units"))

    def display_schedule(self):
        if not hasattr(self, 'schedule_scroll_frame'):
            return
        for widget in self.schedule_scroll_frame.winfo_children():
            widget.destroy()

        self.schedule_buttons = {}

        if not self.schedule:
            tk.Label(self.schedule_scroll_frame,
                     text="📭 Расписание пустое\nНажмите «Добавить день» чтобы начать",
                     bg=self.colors["bg_dark"], fg=self.colors["text_muted"],
                     font=("Segoe UI", 13)).pack(pady=60)
            return

        days_order = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        day_full_names = {
            "Пн": "Понедельник", "Вт": "Вторник", "Ср": "Среда",
            "Чт": "Четверг", "Пт": "Пятница", "Сб": "Суббота", "Вс": "Воскресенье"
        }
        day_emojis = {
            "Пн": "🔵", "Вт": "🟢", "Ср": "🟡", "Чт": "🟠",
            "Пт": "🔴", "Сб": "🟣", "Вс": "⚪"
        }

        grid_frame = tk.Frame(self.schedule_scroll_frame, bg=self.colors["bg_dark"])
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        col = 0
        row = 0
        for day in days_order:
            if day not in self.schedule:
                continue
            exercises = self.schedule[day]
            is_rest = (len(exercises) == 1 and exercises[0].lower() in ["отдых", "отдых "]) or len(exercises) == 0

            if is_rest:
                card_bg = self.colors["rest_day"]
                border_color = "#636e72"
                title_color = self.colors["text_muted"]
            elif day in ["Сб", "Вс"]:
                card_bg = self.colors["sunday"]
                border_color = self.colors["highlight"]
                title_color = self.colors["highlight_hover"]
            else:
                card_bg = self.colors["train_day"]
                border_color = self.colors["text_accent"]
                title_color = self.colors["text_accent"]

            card = tk.Frame(grid_frame, bg=card_bg,
                            highlightbackground=border_color,
                            highlightthickness=2,
                            cursor="hand2")
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            inner = tk.Frame(card, bg=card_bg, cursor="hand2")
            inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

            emoji = day_emojis.get(day, "⚪")
            full_name = day_full_names.get(day, day)
            header = tk.Label(inner, text=f"{emoji} {day} — {full_name}",
                              bg=card_bg, fg=title_color,
                              font=("Segoe UI", 12, "bold"),
                              cursor="hand2")
            header.pack(anchor=tk.W)

            sep = tk.Frame(inner, bg=border_color, height=1)
            sep.pack(fill=tk.X, pady=(5, 8))

            if is_rest:
                tk.Label(inner, text="😴 Отдых",
                         bg=card_bg, fg=self.colors["text_muted"],
                         font=("Segoe UI", 11, "italic"),
                         cursor="hand2").pack(anchor=tk.W)
            else:
                for ex in exercises:
                    ex_frame = tk.Frame(inner, bg=card_bg, cursor="hand2")
                    ex_frame.pack(anchor=tk.W, pady=1)
                    tk.Label(ex_frame, text="▸",
                             bg=card_bg, fg=self.colors["accent"],
                             font=("Segoe UI", 10),
                             cursor="hand2").pack(side=tk.LEFT)
                    tk.Label(ex_frame, text=f" {ex}",
                             bg=card_bg, fg=self.colors["text_primary"],
                             font=("Segoe UI", 11),
                             cursor="hand2").pack(side=tk.LEFT)

            btn_bar = tk.Frame(inner, bg=card_bg)
            btn_bar.pack(fill=tk.X, pady=(10, 0))

            edit_btn = self.create_styled_button(
                btn_bar, "✏️ Изменить",
                lambda d=day: self.edit_schedule_day(d),
                bg=self.colors["bg_light"],
                hover_bg=self.colors["highlight"],
                font_size=9, padx=10, pady=3)
            edit_btn.pack(side=tk.LEFT)

            del_btn = self.create_styled_button(
                btn_bar, "🗑️",
                lambda d=day: self.delete_schedule_day(d),
                bg=self.colors["danger"],
                hover_bg=self.colors["danger_hover"],
                font_size=9, padx=8, pady=3)
            del_btn.pack(side=tk.RIGHT)

            for widget in [card, inner, header, sep]:
                widget.bind("<Button-1>", lambda e, d=day: self.edit_schedule_day(d))

            self.schedule_buttons[day] = card

            col += 1
            if col >= 3:
                col = 0
                row += 1

        for c in range(3):
            grid_frame.grid_columnconfigure(c, weight=1)
        for r in range((len(self.schedule) + 2) // 3):
            grid_frame.grid_rowconfigure(r, weight=1)

    def edit_schedule_day(self, day):
        if not self.require_profile():
            return
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"📝 Редактирование: {day}")
        edit_win.configure(bg=self.colors["bg_dark"])
        edit_win.geometry("580x750")
        edit_win.transient(self.root)
        edit_win.grab_set()

        day_full_names = {
            "Пн": "Понедельник", "Вт": "Вторник", "Ср": "Среда",
            "Чт": "Четверг", "Пт": "Пятница", "Сб": "Суббота", "Вс": "Воскресенье"
        }

        card = tk.Frame(edit_win, bg=self.colors["bg_card"],
                        highlightbackground=self.colors["border"], highlightthickness=1)
        card.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)

        inner = tk.Frame(card, bg=self.colors["bg_card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        full_name = day_full_names.get(day, day)
        tk.Label(inner,
                 text=f"📝 {day} — {full_name}",
                 bg=self.colors["bg_card"], fg=self.colors["text_accent"],
                 font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))

        tk.Label(inner,
                 text="Список упражнений (каждое на новой строке):",
                 bg=self.colors["bg_card"], fg=self.colors["text_secondary"],
                 font=("Segoe UI", 11)).pack(pady=(0, 10))

        text_frame = tk.Frame(inner, bg=self.colors["bg_card"])
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        text_widget = tk.Text(text_frame,
                              bg=self.colors["bg_input"],
                              fg=self.colors["text_primary"],
                              insertbackground=self.colors["text_accent"],
                              font=("Segoe UI", 12),
                              bd=0, relief=tk.FLAT,
                              highlightbackground=self.colors["border"],
                              highlightcolor=self.colors["text_accent"],
                              highlightthickness=1,
                              wrap=tk.WORD,
                              spacing1=3, spacing3=3)
        text_widget.pack(fill=tk.BOTH, expand=True)

        current_exercises = self.schedule.get(day, [])
        for ex in current_exercises:
            text_widget.insert(tk.END, ex + "\n")

        quick_frame = tk.Frame(inner, bg=self.colors["bg_card"])
        quick_frame.pack(fill=tk.X, pady=(15, 0))

        tk.Label(quick_frame, text="Быстрое добавление:",
                 bg=self.colors["bg_card"], fg=self.colors["text_muted"],
                 font=("Segoe UI", 10)).pack(anchor=tk.W)

        quick_buttons_frame = tk.Frame(quick_frame, bg=self.colors["bg_card"])
        quick_buttons_frame.pack(fill=tk.X, pady=8)

        quick_exercises = [
            "Отдых", "Подтягивания", "Отжимания", "Приседания",
            "Пресс", "Планка", "Выпады", "Бег", "Растяжка"
        ]

        for i, ex_name in enumerate(quick_exercises):
            def add_quick(name=ex_name):
                content = text_widget.get("1.0", tk.END).strip()
                if name.lower() == "отдых":
                    text_widget.delete("1.0", tk.END)
                    text_widget.insert("1.0", "Отдых\n")
                else:
                    if content and content.lower() == "отдых":
                        text_widget.delete("1.0", tk.END)
                    text_widget.insert(tk.END, name + "\n")

            btn = tk.Button(quick_buttons_frame, text=ex_name,
                            command=add_quick,
                            bg=self.colors["bg_light"], fg=self.colors["text_primary"],
                            font=("Segoe UI", 10), bd=0, cursor="hand2",
                            activebackground=self.colors["highlight"],
                            padx=12, pady=6)
            btn.grid(row=i // 3, column=i % 3, padx=6, pady=6, sticky="ew")

        for c in range(3):
            quick_buttons_frame.grid_columnconfigure(c, weight=1)

        bottom_frame = tk.Frame(inner, bg=self.colors["bg_card"])
        bottom_frame.pack(fill=tk.X, pady=(30, 15))

        def save_day():
            content = text_widget.get("1.0", tk.END).strip()
            if content:
                exercises = [line.strip() for line in content.split("\n") if line.strip()]
            else:
                exercises = ["Отдых"]
            self.schedule[day] = exercises
            self.save_profile_data()
            self.display_schedule()
            edit_win.destroy()
            messagebox.showinfo("✅ Сохранено",
                                f"Расписание на {full_name} обновлено!\n\n" +
                                "\n".join(f" ▸ {e}" for e in exercises))

        def clear_text():
            text_widget.delete("1.0", tk.END)

        self.create_styled_button(bottom_frame, "💾 Сохранить", save_day,
                                  bg=self.colors["success"], hover_bg=self.colors["success_hover"],
                                  font_size=12, width=18, pady=10).pack(side=tk.LEFT, padx=20)

        self.create_styled_button(bottom_frame, "🧹 Очистить", clear_text,
                                  bg=self.colors["warning"], hover_bg="#f9ca24",
                                  fg="#2d3436", font_size=12, width=14, pady=10).pack(side=tk.LEFT, padx=15)

        self.create_styled_button(bottom_frame, "❌ Отмена", edit_win.destroy,
                                  bg=self.colors["bg_light"], hover_bg=self.colors["danger"],
                                  font_size=12, width=14, pady=10).pack(side=tk.RIGHT, padx=20)

    def add_schedule_day(self):
        if not self.require_profile():
            return

        add_win = tk.Toplevel(self.root)
        add_win.title("➕ Добавить день в расписание")
        add_win.configure(bg=self.colors["bg_dark"])
        add_win.geometry("550x750")
        add_win.minsize(500, 700)
        add_win.transient(self.root)
        add_win.grab_set()

        main_frame = tk.Frame(add_win, bg=self.colors["bg_card"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="➕ Добавить новый день", 
                 font=("Segoe UI", 16, "bold"), bg=self.colors["bg_card"], fg=self.colors["text_accent"]).pack(pady=10)

        tk.Label(main_frame, text="Выберите день недели:", 
                 bg=self.colors["bg_card"], fg=self.colors["text_secondary"]).pack(anchor="w", pady=(10,5))

        all_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        day_names = {"Пн":"Понедельник", "Вт":"Вторник", "Ср":"Среда", "Чт":"Четверг",
                     "Пт":"Пятница", "Сб":"Суббота", "Вс":"Воскресенье"}

        available = [d for d in all_days if d not in self.schedule]
        if not available:
            tk.Label(main_frame, text="Все дни уже добавлены!", fg=self.colors["success"], font=("Segoe UI", 12, "bold")).pack(pady=40)
            tk.Button(main_frame, text="Закрыть", command=add_win.destroy, bg=self.colors["bg_light"]).pack(pady=10)
            return

        selected_day = tk.StringVar(value=available[0])
        for d in available:
            tk.Radiobutton(main_frame, text=f"{d} — {day_names[d]}", variable=selected_day, value=d,
                           bg=self.colors["bg_card"], fg=self.colors["text_primary"],
                           selectcolor=self.colors["bg_input"], font=("Segoe UI", 11)).pack(anchor="w", pady=3)

        tk.Label(main_frame, text="Упражнения (по одному на строку):", 
                 bg=self.colors["bg_card"], fg=self.colors["text_secondary"]).pack(anchor="w", pady=(20,5))

        text_widget = tk.Text(main_frame, height=12, bg=self.colors["bg_input"], fg=self.colors["text_primary"],
                              font=("Segoe UI", 12), insertbackground=self.colors["text_accent"])
        text_widget.pack(fill=tk.BOTH, expand=True, pady=5)
        text_widget.insert("end", "Отдых\n")

        btn_container = tk.Frame(main_frame, bg=self.colors["bg_card"])
        btn_container.pack(fill=tk.X, pady=(20, 10))

        def save_new_day():
            day = selected_day.get()
            content = text_widget.get("1.0", "end-1c").strip()
            exercises = [line.strip() for line in content.splitlines() if line.strip()] or ["Отдых"]
            self.schedule[day] = exercises
            self.save_profile_data()
            self.display_schedule()
            add_win.destroy()
            messagebox.showinfo("Успех", f"День {day_names[day]} добавлен")

        tk.Button(btn_container, text="✅ Добавить день", command=save_new_day,
                  bg=self.colors["success"], fg="white", font=("Segoe UI", 12, "bold"),
                  activebackground=self.colors["success_hover"], relief="flat", padx=20, pady=10).pack(side="left", padx=10)

        tk.Button(btn_container, text="❌ Отмена", command=add_win.destroy,
                  bg=self.colors["danger"], fg="white", font=("Segoe UI", 12, "bold"),
                  activebackground=self.colors["danger_hover"], relief="flat", padx=20, pady=10).pack(side="right", padx=10)

    def delete_schedule_day(self, day):
        if not self.require_profile():
            return
        day_full = {
            "Пн": "Понедельник", "Вт": "Вторник", "Ср": "Среда",
            "Чт": "Четверг", "Пт": "Пятница", "Сб": "Суббота", "Вс": "Воскресенье"
        }
        full_name = day_full.get(day, day)
        if messagebox.askyesno("Удалить день",
                               f"Удалить «{full_name}» из расписания?\n"
                               f"Упражнения: {', '.join(self.schedule.get(day, []))}"):
            if day in self.schedule:
                del self.schedule[day]
            self.save_profile_data()
            self.display_schedule()

    def reset_schedule(self):
        if not self.require_profile():
            return
        
        if messagebox.askyesno("Сброс расписания", 
                              "Удалить ВСЁ текущее расписание?\n"
                              "Все дни недели будут очищены.\n"
                              "Действие нельзя отменить."):
            self.schedule = {}
            self.save_profile_data()
            self.display_schedule()
            messagebox.showinfo("Сброс выполнен", "Расписание полностью очищено.")

    def calculate_and_show_bmi(self, use_saved=False):
        if use_saved:
            bmi_rounded = self.profile["bmi"]
            gender = self.profile["gender"]
            height_cm = float(self.profile["height"]) if self.profile["height"] else 0
            weight_kg = float(self.profile["weight"]) if self.profile["weight"] else 0
            height_m = height_cm / 100
        else:
            try:
                age_str = self.profile_entries["age"].get().strip()
                gender = self.profile_entries["gender"].get()
                height_str = self.profile_entries["height"].get().strip()
                weight_str = self.profile_entries["weight"].get().strip()

                if not (age_str and height_str and weight_str):
                    raise ValueError("Заполните возраст, рост и вес")

                age = int(age_str)
                height_cm = float(height_str)
                weight_kg = float(weight_str)

                if age < 18:
                    messagebox.showwarning("⚠️ Внимание", "Для детей и подростков младше 18 лет\nиспользуйте центильные таблицы — обратитесь к врачу!")
                    self._clear_bmi_labels()
                    return

                if height_cm <= 0 or weight_kg <= 0:
                    raise ValueError("Рост и вес должны быть положительными")

                height_m = height_cm / 100
                bmi = weight_kg / (height_m ** 2)
                bmi_rounded = round(bmi, 2)

                # Сохраняем ИМТ в профиль и базу
                self.profile["bmi"] = bmi_rounded
                self.save_profile_data()

            except ValueError as e:
                messagebox.showwarning("Ошибка ввода", str(e) or "Проверьте корректность чисел в полях возраста, роста и веса")
                self._clear_bmi_labels()
                return

        # Определение статуса и рекомендаций
        if bmi_rounded < 18.5:
            status = "Недостаточный вес"
            risk = "Повышенный"
            recommendation = "Набрать вес"
            color = self.colors["warning"]
            workout_advice = ("Рекомендуется набор мышечной массы.\n"
                              "Тренировки: 3–4 раза в неделю силовые (подтягивания, приседания, отжимания, жим).\n"
                              "Увеличьте калорийность рациона на 300–500 ккал.\n"
                              "Фокус на белок: 1.6–2.2 г/кг веса тела.")
        elif 18.5 <= bmi_rounded < 25.0:
            status = "Нормальный вес"
            risk = "Отсутствует"
            recommendation = "Поддерживать"
            color = self.colors["success"]
            workout_advice = ("Отличный вес — продолжайте в том же духе!\n"
                              "Тренировки: 3–5 раз в неделю (2–3 силовые + 1–2 кардио).\n"
                              "Поддерживайте баланс: подтягивания, приседания, пресс, бег/плавание.\n"
                              "Белок 1.4–1.8 г/кг.")
        elif 25.0 <= bmi_rounded < 30.0:
            status = "Избыточная масса тела"
            risk = "Повышенный"
            recommendation = "Снизить вес"
            color = self.colors["warning"]
            workout_advice = ("Цель — снижение жировой массы.\n"
                              "Тренировки: кардио 4–5 раз в неделю (бег, велосипед, выпады) + сила 2–3 раза.\n"
                              "Дефицит калорий 300–500 ккал.\n"
                              "Фокус: приседания, подтягивания, планка, пресс.")
        elif 30.0 <= bmi_rounded < 35.0:
            status = "Ожирение I степени"
            risk = "Высокий"
            recommendation = "Обратиться к врачу + диета + спорт"
            color = self.colors["danger"]
            workout_advice = ("Начать постепенно.\n"
                              "Кардио низкой интенсивности (ходьба, лёгкий бег) 4–6 раз в неделю.\n"
                              "Силовые 2 раза (приседания, пресс, планка, отжимания от стены).\n"
                              "Обязательна консультация врача/тренера.\n"
                              "Дефицит калорий 500–700 ккал.")
        elif 35.0 <= bmi_rounded < 40.0:
            status = "Ожирение II степени"
            risk = "Очень высокий"
            recommendation = "Срочно к врачу!"
            color = self.colors["danger"]
            workout_advice = ("Срочно начать под контролем врача.\n"
                              "Ходьба 30–60 минут ежедневно.\n"
                              "Лёгкие упражнения дома: планка, скручивания, подъёмы ног.\n"
                              "Диета строгая, консультация эндокринолога обязательна.")
        else:
            status = "Ожирение III–IV степени"
            risk = "Критически высокий"
            recommendation = "Срочно к врачу!"
            color = self.colors["danger"]
            workout_advice = ("Только под наблюдением врача!\n"
                              "Начать с минимальной активности: ходьба, дыхательные упражнения.\n"
                              "Программа снижения веса разрабатывается индивидуально.\n"
                              "Не занимайтесь интенсивно без разрешения врача.")

        # Идеальный вес
        ideal_weight = 50 + 0.91 * (height_cm - 152.4)
        if gender == "Женский":
            ideal_weight *= 0.9
        ideal_weight = round(ideal_weight, 1)

        min_normal = round(18.5 * (height_m ** 2), 1)
        max_normal = round(24.9 * (height_m ** 2), 1)

        # Вывод результатов
        self.bmi_labels["bmi_value"].config(text=f"{bmi_rounded}", fg=color)
        self.bmi_labels["status"].config(text=status, fg=color)
        self.bmi_labels["risk"].config(text=risk, fg=color)
        self.bmi_labels["recommendation"].config(text=recommendation, fg=color)
        self.bmi_labels["ideal_weight"].config(text=f"{ideal_weight} кг", fg=self.colors["text_accent"])
        self.bmi_labels["normal_range"].config(text=f"{min_normal} – {max_normal} кг", fg=self.colors["text_accent"])

        # Советы по тренировкам (добавляем новый лейбл)
        tk.Label(self.bmi_result_frame, text="Советы по тренировкам и упражнениям:", 
                 bg=self.colors["bg_input"], fg=self.colors["text_secondary"],
                 font=("Segoe UI", 11)).grid(row=6, column=0, sticky="w", padx=12, pady=(10,0))

        advice_label = tk.Label(self.bmi_result_frame, text=workout_advice,
                                bg=self.colors["bg_input"], fg=self.colors["text_primary"],
                                font=("Segoe UI", 11), wraplength=450, justify="left")
        advice_label.grid(row=7, column=0, columnspan=2, sticky="w", padx=12, pady=(0,10))

    def _clear_bmi_labels(self):
        for lbl in self.bmi_labels.values():
            lbl.config(text="—", fg=self.colors["text_primary"])

    def setup_profile_tab(self):
        outer = tk.Frame(self.tab_profile, bg=self.colors["bg_dark"])
        outer.pack(expand=True, fill=tk.BOTH)

        card = tk.Frame(outer, bg=self.colors["bg_card"],
                        highlightbackground=self.colors["border"], highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center")

        inner = tk.Frame(card, bg=self.colors["bg_card"])
        inner.pack(padx=50, pady=35)

        self.create_section_label(inner, "👤 Профиль и ИМТ", 18).grid(
            row=0, column=0, columnspan=3, pady=(0, 25), sticky="ew")

        fields = [
            ("📛 ФИО:", "full_name", tk.Entry),
            ("⚧ Пол:", "gender", ttk.Combobox),
            ("🎂 Возраст:", "age", tk.Entry),
            ("📏 Рост (см):", "height", tk.Entry),
            ("⚖️ Вес (кг):", "weight", tk.Entry),
        ]

        self.profile_entries = {}
        row_idx = 1

        for label_text, key, widget_type in fields:
            tk.Label(inner, text=label_text,
                     bg=self.colors["bg_card"], fg=self.colors["text_secondary"],
                     font=("Segoe UI", 12)).grid(row=row_idx, column=0, sticky="w", padx=8, pady=10)

            if widget_type == ttk.Combobox:
                entry = ttk.Combobox(inner, values=["Мужской", "Женский", "Другой"],
                                     state="readonly", width=22, font=("Segoe UI", 11))
                entry.set(self.profile.get(key, ""))
            else:
                entry = self.create_styled_entry(inner, width=24, font_size=12)

            entry.grid(row=row_idx, column=1, padx=8, pady=10, sticky="w")
            val = self.profile.get(key, "")
            if val:
                if hasattr(entry, "insert"):
                    entry.insert(0, str(val))
                else:
                    entry.set(str(val))

            self.profile_entries[key] = entry
            row_idx += 1

        calc_btn = self.create_styled_button(
            inner, "📊 Рассчитать ИМТ", self.calculate_and_show_bmi,
            bg=self.colors["highlight"], hover_bg=self.colors["highlight_hover"],
            font_size=12, width=20
        )
        calc_btn.grid(row=row_idx, column=0, columnspan=2, pady=(20, 10))

        self.bmi_result_frame = tk.Frame(inner, bg=self.colors["bg_input"],
                                         highlightbackground=self.colors["border"], highlightthickness=1)
        self.bmi_result_frame.grid(row=row_idx+1, column=0, columnspan=2, pady=15, sticky="ew", padx=10)

        self.bmi_labels = {}
        result_labels = [
            ("Ваш ИМТ:", "bmi_value"),
            ("Статус:", "status"),
            ("Риск:", "risk"),
            ("Рекомендации:", "recommendation"),
            ("Идеальный вес ≈", "ideal_weight"),
            ("Нормальный диапазон:", "normal_range"),
        ]

        for i, (txt, key) in enumerate(result_labels):
            tk.Label(self.bmi_result_frame, text=txt,
                     bg=self.colors["bg_input"], fg=self.colors["text_secondary"],
                     font=("Segoe UI", 11)).grid(row=i, column=0, sticky="w", padx=12, pady=6)

            lbl = tk.Label(self.bmi_result_frame, text="—",
                           bg=self.colors["bg_input"], fg=self.colors["text_primary"],
                           font=("Segoe UI", 11, "bold"))
            lbl.grid(row=i, column=1, sticky="w", padx=8, pady=6)
            self.bmi_labels[key] = lbl

        btn_frame = tk.Frame(inner, bg=self.colors["bg_card"])
        btn_frame.grid(row=row_idx+2, column=0, columnspan=2, pady=(15, 0), sticky="ew")

        self.create_styled_button(btn_frame, "💾 Сохранить профиль", self.save_profile_from_form,
                                  bg=self.colors["success"], hover_bg=self.colors["success_hover"],
                                  font_size=11, width=18).pack(side=tk.LEFT, padx=10)

        self.create_styled_button(btn_frame, "🔄 Загрузить", self.load_profile_to_form,
                                  bg=self.colors["bg_light"], hover_bg=self.colors["highlight"],
                                  font_size=11, width=18).pack(side=tk.LEFT, padx=10)

    def save_profile_from_form(self):
        if not self.require_profile():
            return

        self.profile["full_name"] = self.profile_entries["full_name"].get().strip()
        self.profile["gender"] = self.profile_entries["gender"].get()
        self.profile["age"] = self.profile_entries["age"].get().strip()
        self.profile["height"] = self.profile_entries["height"].get().strip()
        self.profile["weight"] = self.profile_entries["weight"].get().strip()

        self.save_profile_data()
        messagebox.showinfo("✅ Успех", "Профиль сохранён!")

        if all(self.profile.get(k) for k in ["age", "height", "weight"]):
            self.calculate_and_show_bmi()

    def load_profile_to_form(self):
        if not self.current_profile:
            return
        for key, entry in self.profile_entries.items():
            val = self.profile.get(key, "")
            if isinstance(entry, ttk.Combobox):
                entry.set(val)
            else:
                entry.delete(0, tk.END)
                entry.insert(0, str(val))

        if all(self.profile.get(k) for k in ["age", "height", "weight"]):
            self.calculate_and_show_bmi()

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkoutTracker(root)
    root.geometry("1200x800")
    root.minsize(900, 600)
    root.mainloop()