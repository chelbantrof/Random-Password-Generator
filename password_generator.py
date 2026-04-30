import random
import string
import json
import os
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

# ------------------ Настройки ------------------
HISTORY_FILE = "password_history.json"
MIN_LEN = 4
MAX_LEN = 50

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator — Чебан Трофим")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        # Переменные
        self.pass_len = IntVar(value=12)
        self.use_digits = BooleanVar(value=True)
        self.use_letters = BooleanVar(value=True)
        self.use_special = BooleanVar(value=True)
        self.history = self.load_history()

        # GUI компоненты
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # Рамка настроек
        frame_settings = LabelFrame(self.root, text="Настройки пароля", padx=10, pady=10)
        frame_settings.pack(fill="x", padx=10, pady=5)

        # Ползунок длины
        Label(frame_settings, text="Длина пароля:").grid(row=0, column=0, sticky="w")
        self.len_slider = Scale(frame_settings, from_=MIN_LEN, to=MAX_LEN, orient=HORIZONTAL,
                                variable=self.pass_len, length=300)
        self.len_slider.grid(row=0, column=1, padx=10)
        self.len_label = Label(frame_settings, text=f"{self.pass_len.get()}")
        self.len_label.grid(row=0, column=2)
        self.len_slider.configure(command=lambda x: self.len_label.configure(text=str(int(float(x)))))

        # Чекбоксы
        Checkbutton(frame_settings, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w")
        Checkbutton(frame_settings, text="Буквы (A-Z a-z)", variable=self.use_letters).grid(row=1, column=1, sticky="w")
        Checkbutton(frame_settings, text="Спецсимволы (!@#$%^&*)", variable=self.use_special).grid(row=1, column=2, sticky="w")

        # Кнопка генерации
        self.gen_btn = Button(self.root, text="Сгенерировать пароль", bg="lightblue", font=("Arial", 12),
                              command=self.generate_and_save)
        self.gen_btn.pack(pady=10)

        # Поле вывода пароля + кнопка копирования
        frame_output = Frame(self.root)
        frame_output.pack(fill="x", padx=10, pady=5)
        self.password_var = StringVar()
        self.pass_entry = Entry(frame_output, textvariable=self.password_var, font=("Courier", 12), state="readonly")
        self.pass_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.copy_btn = Button(frame_output, text="Копировать", command=self.copy_to_clipboard)
        self.copy_btn.pack(side="right")

        # История
        Label(self.root, text="История сгенерированных паролей:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        frame_table = Frame(self.root)
        frame_table.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "length", "password")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings")
        self.tree.heading("date", text="Дата и время")
        self.tree.heading("length", text="Длина")
        self.tree.heading("password", text="Пароль")
        self.tree.column("date", width=160)
        self.tree.column("length", width=60)
        self.tree.column("password", width=300)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления историей
        btn_frame = Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        Button(btn_frame, text="Очистить историю", command=self.clear_history, bg="salmon").pack(side="left", padx=5)
        Button(btn_frame, text="Сохранить историю вручную", command=self.save_history_to_file).pack(side="left", padx=5)

    def generate_password(self):
        length = self.pass_len.get()
        if length < MIN_LEN or length > MAX_LEN:
            messagebox.showerror("Ошибка", f"Длина должна быть от {MIN_LEN} до {MAX_LEN}")
            return None

        chars = ""
        if self.use_digits.get():
            chars += string.digits
        if self.use_letters.get():
            chars += string.ascii_letters
        if self.use_special.get():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not chars:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return None

        password = ''.join(random.choice(chars) for _ in range(length))
        return password

    def generate_and_save(self):
        pwd = self.generate_password()
        if pwd:
            self.password_var.set(pwd)
            # Добавить в историю
            record = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "length": self.pass_len.get(),
                "password": pwd
            }
            self.history.append(record)
            self.save_history_to_file()
            self.update_history_table()

    def copy_to_clipboard(self):
        pwd = self.password_var.get()
        if pwd:
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Скопировано", "Пароль скопирован в буфер обмена")
        else:
            messagebox.showwarning("Нет пароля", "Сначала сгенерируйте пароль")

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history_to_file(self):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)

    def update_history_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for record in self.history[-50:]:  # Показываем последние 50 записей
            self.tree.insert("", END, values=(record["date"], record["length"], record["password"]))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю паролей?"):
            self.history = []
            self.save_history_to_file()
            self.update_history_table()
            self.password_var.set("")

if __name__ == "__main__":
    root = Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()