import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "weather.json"

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("650x550")
        
        self.records = self.load_data()
        
        # --- Форма добавления ---
        frame_add = tk.LabelFrame(root, text="Добавить запись")
        frame_add.pack(padx=10, pady=10, fill="x")
        
        tk.Label(frame_add, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5)
        self.entry_date = tk.Entry(frame_add, width=12)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_add, text="Температура (°C):").grid(row=0, column=2, padx=5, pady=5)
        self.entry_temp = tk.Entry(frame_add, width=10)
        self.entry_temp.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame_add, text="Осадки:").grid(row=0, column=4, padx=5, pady=5)
        self.combo_precip = ttk.Combobox(frame_add, values=["Нет", "Да"], width=5)
        self.combo_precip.current(0)
        self.combo_precip.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Label(frame_add, text="Описание погоды:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_desc = tk.Entry(frame_add, width=30)
        self.entry_desc.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")
        
        tk.Button(frame_add, text="Добавить запись", command=self.add_record, bg="#4CAF50", fg="white").grid(row=1, column=4, columnspan=2, pady=5, sticky="we", padx=5)
        
        # --- Фильтрация ---
        frame_filter = tk.LabelFrame(root, text="Фильтр записей")
        frame_filter.pack(padx=10, pady=5, fill="x")
        
        tk.Label(frame_filter, text="Дата:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date = tk.Entry(frame_filter, width=12)
        self.filter_date.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_filter, text="Температура выше (°C):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_temp = tk.Entry(frame_filter, width=10)
        self.filter_temp.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Button(frame_filter, text="Применить", command=self.update_table).grid(row=0, column=4, padx=5)
        tk.Button(frame_filter, text="Сбросить", command=self.reset_filter).grid(row=0, column=5, padx=5)

        # --- Таблица ---
        columns = ("date", "temp", "desc", "precip")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура (°C)")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("precip", text="Осадки")
        
        self.tree.column("date", width=100)
        self.tree.column("temp", width=120)
        self.tree.column("desc", width=250)
        self.tree.column("precip", width=80)
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.update_table()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(self.records, file, ensure_ascii=False, indent=4)

    def add_record(self):
        date_str = self.entry_date.get()
        temp_str = self.entry_temp.get()
        desc = self.entry_desc.get().strip()
        precip = self.combo_precip.get()
        
        # Валидация даты
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД.")
            return
            
        # Валидация температуры
        try:
            temp = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом (например, 15.5 или -5)!")
            return
            
        # Валидация описания
        if not desc:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым!")
            return
            
        self.records.append({"date": date_str, "temp": temp, "desc": desc, "precip": precip})
        self.save_data()
        self.update_table()
        self.entry_desc.delete(0, tk.END)
        self.entry_temp.delete(0, tk.END)
        messagebox.showinfo("Успех", "Запись о погоде успешно добавлена!")

    def reset_filter(self):
        self.filter_date.delete(0, tk.END)
        self.filter_temp.delete(0, tk.END)
        self.update_table()

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        f_date = self.filter_date.get().strip()
        f_temp_str = self.filter_temp.get().strip()
        
        f_temp = None
        if f_temp_str:
            try:
                f_temp = float(f_temp_str)
            except ValueError:
                pass # Если в фильтр ввели не число, игнорируем
        
        for rec in self.records:
            match_date = True
            match_temp = True
            
            if f_date and rec["date"] != f_date:
                match_date = False
            if f_temp is not None and float(rec["temp"]) <= f_temp:
                match_temp = False
                
            if match_date and match_temp:
                self.tree.insert("", "end", values=(rec["date"], f"{rec['temp']} °C", rec["desc"], rec["precip"]))

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()
