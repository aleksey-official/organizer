import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime, date
import calendar
import requests
import json

class OrganizerClientGUI:
    def __init__(self, base_url='http://localhost/organizer/'):
        self.base_url = base_url
        self.session = requests.Session()
        self.logged_in = False
        self.username = None
        self.current_date = None  # выбранная дата
        self.current_month = date.today().replace(day=1)
        self.root = tk.Tk()
        self.root.title("Органайзер")
        self.root.geometry("1000x700")
        self.create_widgets()
        self.update_calendar()
        self.root.mainloop()

    def create_widgets(self):
        # Верхняя панель с информацией о пользователе и кнопками
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        self.user_label = tk.Label(top_frame, text="Не авторизован")
        self.user_label.pack(side=tk.LEFT, padx=5)

        self.login_btn = tk.Button(top_frame, text="Вход", command=self.login_dialog)
        self.login_btn.pack(side=tk.LEFT, padx=5)

        self.register_btn = tk.Button(top_frame, text="Регистрация", command=self.register_dialog)
        self.register_btn.pack(side=tk.LEFT, padx=5)

        self.logout_btn = tk.Button(top_frame, text="Выход", command=self.logout, state=tk.DISABLED)
        self.logout_btn.pack(side=tk.LEFT, padx=5)

        # Панель навигации по месяцам
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(nav_frame, text="<< Предыдущий", command=self.prev_month).pack(side=tk.LEFT, padx=5)
        self.month_label = tk.Label(nav_frame, text="", font=("Arial", 14))
        self.month_label.pack(side=tk.LEFT, expand=True)
        tk.Button(nav_frame, text="Следующий >>", command=self.next_month).pack(side=tk.LEFT, padx=5)

        # Календарь (сетка кнопок)
        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(pady=10)

        # Дни недели
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, d in enumerate(days):
            tk.Label(self.calendar_frame, text=d, width=10, relief=tk.RIDGE).grid(row=0, column=i, sticky="nsew")

        self.day_buttons = []  # список кнопок для дней (6 недель x 7 дней)
        for week in range(6):
            row_buttons = []
            for col in range(7):
                btn = tk.Button(self.calendar_frame, width=10, height=2, relief=tk.RIDGE,
                                command=lambda w=week, c=col: self.on_day_click(w, c))
                btn.grid(row=week+1, column=col, sticky="nsew")
                row_buttons.append(btn)
            self.day_buttons.append(row_buttons)

        # Панель информации о дне
        info_frame = tk.Frame(self.root)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(info_frame, text="Информация за день:", font=("Arial", 12)).pack(anchor=tk.W)

        self.info_text = tk.Text(info_frame, height=15, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Кнопки для редактирования
        edit_btn_frame = tk.Frame(info_frame)
        edit_btn_frame.pack(fill=tk.X, pady=5)

        self.edit_btn = tk.Button(edit_btn_frame, text="Редактировать", command=self.edit_info, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = tk.Button(edit_btn_frame, text="Сохранить", command=self.save_info, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = tk.Button(edit_btn_frame, text="Отмена", command=self.cancel_edit, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- API методы ----------
    def api_request(self, endpoint, method='GET', params=None, data=None, json_data=None):
        url = self.base_url.rstrip('/') + '/' + endpoint.lstrip('/')
        try:
            if method.upper() == 'GET':
                resp = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                if json_data:
                    resp = self.session.post(url, json=json_data)
                else:
                    resp = self.session.post(url, data=data)
            else:
                return None
            if resp.status_code == 200:
                return resp.json()
            else:
                self.status_var.set(f"Ошибка HTTP {resp.status_code}")
                return None
        except Exception as e:
            self.status_var.set(f"Ошибка соединения: {e}")
            return None

    def login(self, username, password):
        result = self.api_request('api/login.json.php', method='POST', json_data={'username': username, 'password': password})
        if result and result.get('success'):
            self.logged_in = True
            self.username = username
            self.update_auth_ui()
            self.status_var.set(f"Добро пожаловать, {username}!")
            return True
        else:
            error = result.get('error', 'Неизвестная ошибка') if result else 'Нет ответа от сервера'
            messagebox.showerror("Ошибка входа", error)
            return False

    def register(self, username, password):
        result = self.api_request('api/register.json.php', method='POST', json_data={'username': username, 'password': password})
        if result and result.get('success'):
            messagebox.showinfo("Регистрация", "Регистрация прошла успешно! Теперь можно войти.")
            return True
        else:
            error = result.get('error', 'Неизвестная ошибка') if result else 'Нет ответа от сервера'
            messagebox.showerror("Ошибка регистрации", error)
            return False

    def logout(self):
        self.session.get(self.base_url + 'logout.php')
        self.logged_in = False
        self.username = None
        self.update_auth_ui()
        self.status_var.set("Вы вышли из системы")
        self.clear_info()

    def get_day_info(self, date_str):
        result = self.api_request('api/get_day.php', params={'date': date_str})
        if result:
            description = result.get('description', '')
            self.current_description = description
            self.can_edit = result.get('can_edit', False) and self.logged_in
            self.show_info(description)
            return description
        else:
            self.status_var.set("Не удалось получить информацию о дне")
            return None

    def save_day_info(self, date_str, description):
        if not self.logged_in:
            messagebox.showerror("Ошибка", "Необходимо авторизоваться")
            return False
        result = self.api_request('api/save_day.php', method='POST', data={'date': date_str, 'description': description})
        if result and result.get('success'):
            self.status_var.set("Информация сохранена")
            return True
        else:
            error = result.get('error', 'Ошибка сохранения') if result else 'Нет ответа'
            messagebox.showerror("Ошибка", error)
            return False

    # ---------- Обновление UI ----------
    def update_auth_ui(self):
        if self.logged_in:
            self.user_label.config(text=f"Пользователь: {self.username}")
            self.login_btn.config(state=tk.DISABLED)
            self.register_btn.config(state=tk.DISABLED)
            self.logout_btn.config(state=tk.NORMAL)
            # Если выбран день, обновим возможность редактирования
            if self.current_date:
                self.get_day_info(self.current_date)  # повторно запросим, чтобы обновить can_edit
        else:
            self.user_label.config(text="Не авторизован")
            self.login_btn.config(state=tk.NORMAL)
            self.register_btn.config(state=tk.NORMAL)
            self.logout_btn.config(state=tk.DISABLED)
            self.edit_btn.config(state=tk.DISABLED)
            self.save_btn.config(state=tk.DISABLED)
            self.cancel_btn.config(state=tk.DISABLED)
            self.info_text.config(state=tk.DISABLED)

    def clear_info(self):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
        self.edit_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.DISABLED)

    def show_info(self, text):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text if text else "Нет информации за этот день")
        self.info_text.config(state=tk.DISABLED)
        if self.logged_in and self.can_edit:
            self.edit_btn.config(state=tk.NORMAL)
        else:
            self.edit_btn.config(state=tk.DISABLED)

    # ---------- Календарь ----------
    def update_calendar(self):
        # Очистить все кнопки
        for week in range(6):
            for col in range(7):
                self.day_buttons[week][col].config(text="", state=tk.DISABLED, bg="SystemButtonFace")

        year = self.current_month.year
        month = self.current_month.month
        self.month_label.config(text=self.current_month.strftime("%B %Y"))

        # Первый день месяца (0=пн, 6=вс) - в Python weekday() 0=пн
        first_weekday = date(year, month, 1).weekday()  # 0-6
        days_in_month = calendar.monthrange(year, month)[1]

        day = 1
        for week in range(6):
            for col in range(7):
                if week == 0 and col < first_weekday:
                    continue
                if day <= days_in_month:
                    self.day_buttons[week][col].config(text=str(day), state=tk.NORMAL, bg="white")
                    day += 1

    def on_day_click(self, week, col):
        btn_text = self.day_buttons[week][col].cget("text")
        if btn_text:
            day = int(btn_text)
            date_str = f"{self.current_month.year:04d}-{self.current_month.month:02d}-{day:02d}"
            self.current_date = date_str
            self.get_day_info(date_str)

    def prev_month(self):
        year = self.current_month.year
        month = self.current_month.month
        if month == 1:
            self.current_month = self.current_month.replace(year=year-1, month=12)
        else:
            self.current_month = self.current_month.replace(month=month-1)
        self.update_calendar()
        self.clear_info()

    def next_month(self):
        year = self.current_month.year
        month = self.current_month.month
        if month == 12:
            self.current_month = self.current_month.replace(year=year+1, month=1)
        else:
            self.current_month = self.current_month.replace(month=month+1)
        self.update_calendar()
        self.clear_info()

    # ---------- Диалоги ----------
    def login_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Вход")
        dialog.geometry("300x250")
        dialog.resizable(False, False)

        tk.Label(dialog, text="Имя пользователя:").pack(pady=5)
        username_entry = tk.Entry(dialog)
        username_entry.pack(pady=5)

        tk.Label(dialog, text="Пароль:").pack(pady=5)
        password_entry = tk.Entry(dialog, show="*")
        password_entry.pack(pady=5)

        def do_login():
            u = username_entry.get()
            p = password_entry.get()
            if u and p:
                if self.login(u, p):
                    dialog.destroy()
            else:
                messagebox.showwarning("Внимание", "Заполните все поля")

        tk.Button(dialog, text="Войти", command=do_login).pack(pady=10)

    def register_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Регистрация")
        dialog.geometry("300x250")  # увеличено
        dialog.resizable(False, False)

        tk.Label(dialog, text="Имя пользователя:").pack(pady=5)
        username_entry = tk.Entry(dialog)
        username_entry.pack(pady=5)

        tk.Label(dialog, text="Пароль:").pack(pady=5)
        password_entry = tk.Entry(dialog, show="*")
        password_entry.pack(pady=5)

        tk.Label(dialog, text="Повторите пароль:").pack(pady=5)
        confirm_entry = tk.Entry(dialog, show="*")
        confirm_entry.pack(pady=5)

        def do_register():
            try:
                u = username_entry.get()
                p = password_entry.get()
                c = confirm_entry.get()
                if u and p and c:
                    if p != c:
                        messagebox.showerror("Ошибка", "Пароли не совпадают")
                        return
                    if self.register(u, p):
                        dialog.destroy()
                else:
                    messagebox.showwarning("Внимание", "Заполните все поля")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

        tk.Button(dialog, text="Зарегистрироваться", command=do_register).pack(pady=10)

    # ---------- Редактирование ----------
    def edit_info(self):
        # Переключить текстовое поле в режим редактирования
        self.info_text.config(state=tk.NORMAL)
        self.edit_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.NORMAL)

    def save_info(self):
        new_text = self.info_text.get(1.0, tk.END).strip()
        if self.save_day_info(self.current_date, new_text):
            self.current_description = new_text
            self.info_text.config(state=tk.DISABLED)
            self.edit_btn.config(state=tk.NORMAL)
            self.save_btn.config(state=tk.DISABLED)
            self.cancel_btn.config(state=tk.DISABLED)
            self.show_info(new_text)  # обновить отображение
        else:
            # Ошибка уже показана
            pass

    def cancel_edit(self):
        # Вернуть исходный текст
        self.show_info(self.current_description if hasattr(self, 'current_description') else "")
        self.edit_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    # При необходимости изменить базовый URL
    # OrganizerClientGUI(base_url='http://localhost/путь_к_папке/')
    OrganizerClientGUI()