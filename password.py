import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os

# Имя файла для сохранения истории
HISTORY_FILE = "passwords_history.json"

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x600")
        
        # Список для хранения истории паролей
        self.history = []
        
        # Создание интерфейса
        self.create_settings_frame()
        self.create_generate_frame()
        self.create_history_frame()
        
        # Загрузка истории из файла
        self.load_history()
    
    def create_settings_frame(self):
        """Панель настроек пароля"""
        settings_frame = tk.LabelFrame(self.root, text="Настройки пароля", padx=10, pady=10)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # Длина пароля (ползунок)
        tk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.length_var = tk.IntVar(value=12)
        self.length_scale = tk.Scale(settings_frame, from_=4, to=30, orient="horizontal", 
                                      variable=self.length_var, length=300)
        self.length_scale.grid(row=0, column=1, padx=5, pady=5)
        
        # Метка для отображения текущей длины
        self.length_label = tk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5)
        
        # Обновляем метку при движении ползунка
        self.length_scale.configure(command=self.update_length_label)
        
        # Чекбоксы для выбора символов
        tk.Label(settings_frame, text="Использовать:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.use_digits = tk.BooleanVar(value=True)
        digits_cb = tk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits)
        digits_cb.grid(row=1, column=1, sticky="w", padx=5)
        
        self.use_letters = tk.BooleanVar(value=True)
        letters_cb = tk.Checkbutton(settings_frame, text="Буквы (a-z, A-Z)", variable=self.use_letters)
        letters_cb.grid(row=1, column=2, sticky="w", padx=5)
        
        self.use_symbols = tk.BooleanVar(value=False)
        symbols_cb = tk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*)", variable=self.use_symbols)
        symbols_cb.grid(row=1, column=3, sticky="w", padx=5)
    
    def update_length_label(self, value):
        """Обновление метки с длиной пароля"""
        self.length_label.config(text=str(int(float(value))))
    
    def create_generate_frame(self):
        """Панель для генерации и отображения пароля"""
        generate_frame = tk.LabelFrame(self.root, text="Генерация", padx=10, pady=10)
        generate_frame.pack(fill="x", padx=10, pady=5)
        
        # Кнопка генерации
        self.generate_btn = tk.Button(generate_frame, text="Сгенерировать пароль", 
                                      command=self.generate_password, bg="lightgreen", font=("Arial", 12))
        self.generate_btn.pack(pady=5)
        
        # Поле для отображения пароля
        tk.Label(generate_frame, text="Сгенерированный пароль:").pack(pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(generate_frame, textvariable=self.password_var, 
                                       font=("Courier", 14), width=40, state="readonly")
        self.password_entry.pack(pady=5)
        
        # Кнопка копирования
        self.copy_btn = tk.Button(generate_frame, text="Копировать в буфер", 
                                  command=self.copy_to_clipboard, bg="lightblue")
        self.copy_btn.pack(pady=5)
    
    def create_history_frame(self):
        """Таблица для отображения истории паролей"""
        history_frame = tk.LabelFrame(self.root, text="История паролей", padx=10, pady=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создаем таблицу с прокруткой
        columns = ("password", "length", "date")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        
        # Настройка заголовков
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("date", text="Дата и время")
        
        # Настройка ширины столбцов
        self.tree.column("password", width=250)
        self.tree.column("length", width=80)
        self.tree.column("date", width=200)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка очистки истории
        clear_btn = tk.Button(history_frame, text="Очистить историю", 
                              command=self.clear_history, bg="lightcoral")
        clear_btn.pack(pady=5)
    
    def generate_password(self):
        """Генерация пароля на основе настроек"""
        # Проверяем, что выбран хотя бы один тип символов
        if not self.use_digits.get() and not self.use_letters.get() and not self.use_symbols.get():
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return
        
        length = self.length_var.get()
        
        # Собираем доступные символы
        characters = ""
        if self.use_digits.get():
            characters += string.digits  # 0-9
        if self.use_letters.get():
            characters += string.ascii_letters  # a-z, A-Z
        if self.use_symbols.get():
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Генерируем пароль
        password = ""
        for _ in range(length):
            password += random.choice(characters)
        
        # Отображаем пароль
        self.password_var.set(password)
        
        # Добавляем в историю
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        history_item = {
            "password": password,
            "length": length,
            "date": now
        }
        
        self.history.append(history_item)
        self.update_history_table()
        self.save_history()
        
        messagebox.showinfo("Успех", "Пароль успешно сгенерирован!")
    
    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте пароль!")
    
    def update_history_table(self):
        """Обновление таблицы истории"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавляем все пароли из истории (в обратном порядке, новые сверху)
        for item in reversed(self.history):
            self.tree.insert("", "end", values=(
                item["password"],
                item["length"],
                item["date"]
            ))
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.update_history_table()
            self.save_history()
            messagebox.showinfo("Успех", "История очищена!")
    
    def save_history(self):
        """Сохранение истории в JSON файл"""
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
    
    def load_history(self):
        """Загрузка истории из JSON файла"""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                self.update_history_table()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {e}")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()