import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("850x550")
        
        self.records = []          # Все записи
        self.filtered_records = [] # Отфильтрованные записи
        
        # Попытка загрузить сохранённые данные
        self.load_from_file()
        
        # Создание интерфейса
        self.create_input_frame()
        self.create_records_tree()
        self.create_filter_frame()
        self.create_button_frame()
        
        self.update_treeview()
    
    def create_input_frame(self):
        """Панель добавления новой записи"""
        input_frame = ttk.LabelFrame(self.root, text="Добавить новую запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w", padx=5)
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5)
        
        # Осадки
        ttk.Label(input_frame, text="Осадки:").grid(row=0, column=4, sticky="w", padx=5)
        self.precip_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Да", variable=self.precip_var).grid(row=0, column=5, padx=5)
        
        # Описание
        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky="w", padx=5)
        self.desc_entry = ttk.Entry(input_frame, width=60)
        self.desc_entry.grid(row=1, column=1, columnspan=5, padx=5, pady=5, sticky="we")
    
    def create_records_tree(self):
        """Таблица для отображения записей"""
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("date", "temperature", "precipitation", "description")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("precipitation", text="Осадки")
        self.tree.heading("description", text="Описание")
        
        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("precipitation", width=80)
        self.tree.column("description", width=450)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_filter_frame(self):
        """Панель фильтрации"""
        filter_frame = ttk.LabelFrame(self.root, text="Фильтр записей", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5)
        self.filter_date_entry = ttk.Entry(filter_frame, width=12)
        self.filter_date_entry.grid(row=0, column=1, padx=5)
        
        # Фильтр по температуре
        ttk.Label(filter_frame, text="Температура >").grid(row=0, column=2, padx=5)
        self.filter_temp_entry = ttk.Entry(filter_frame, width=8)
        self.filter_temp_entry.grid(row=0, column=3, padx=5)
        ttk.Label(filter_frame, text="°C").grid(row=0, column=4, padx=2)
        
        # Кнопки фильтрации
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=5, padx=10)
        ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=6, padx=5)
    
    def create_button_frame(self):
        """Нижняя панель с кнопками"""
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="➕ Добавить запись", command=self.add_record).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_to_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_from_file).pack(side="left", padx=5)
    
    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def add_record(self):
        """Добавление новой записи с проверкой ввода"""
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        precip = self.precip_var.get()
        desc = self.desc_entry.get().strip()
        
        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД (например, 2025-04-26)")
            return
        
        try:
            temperature = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return
        
        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым!")
            return
        
        record = {
            "date": date,
            "temperature": temperature,
            "precipitation": "Да" if precip else "Нет",
            "description": desc
        }
        self.records.append(record)
        self.reset_filter()  # Показываем все записи
        self.update_treeview()
        
        # Очистка полей ввода
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.temp_entry.delete(0, tk.END)
        self.precip_var.set(False)
        self.desc_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Запись успешно добавлена!")
    
    def apply_filter(self):
        """Применение фильтров"""
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()
        
        self.filtered_records = self.records.copy()
        
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты в фильтре!")
                return
            self.filtered_records = [r for r in self.filtered_records if r["date"] == filter_date]
        
        if filter_temp_str:
            try:
                temp_threshold = float(filter_temp_str)
                self.filtered_records = [r for r in self.filtered_records if r["temperature"] > temp_threshold]
            except ValueError:
                messagebox.showerror("Ошибка", "Фильтр по температуре должен быть числом!")
                return
        
        self.update_treeview(filtered=True)
        
        if not self.filtered_records:
            messagebox.showinfo("Результат", "Записей, соответствующих фильтру, не найдено.")
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.filtered_records = self.records.copy()
        self.update_treeview(filtered=True)
    
    def update_treeview(self, filtered=False):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        data = self.filtered_records if filtered else self.records
        for record in data:
            self.tree.insert("", tk.END, values=(
                record["date"],
                record["temperature"],
                record["precipitation"],
                record["description"]
            ))
    
    def save_to_file(self):
        """Сохранение в JSON файл"""
        try:
            with open("weather_data.json", "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Успех", "Данные сохранены в файл weather_data.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def load_from_file(self):
        """Загрузка из JSON файла"""
        try:
            with open("weather_data.json", "r", encoding="utf-8") as f:
                self.records = json.load(f)
            self.reset_filter()
            messagebox.showinfo("Успех", "Данные загружены из файла weather_data.json")
        except FileNotFoundError:
            messagebox.showwarning("Предупреждение", "Файл с сохранёнными данными не найден. Начинаем с пустого дневника.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
