import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер расходов")
        self.root.geometry("650x550")
        
        self.expenses = self.load_data()
        
        # --- Форма добавления ---
        frame_add = tk.LabelFrame(root, text="Добавить расход")
        frame_add.pack(padx=10, pady=10, fill="x")
        
        tk.Label(frame_add, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_amount = tk.Entry(frame_add, width=15)
        self.entry_amount.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_add, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.combo_category = ttk.Combobox(frame_add, values=["Еда", "Транспорт", "Развлечения", "Счета", "Другое"], width=15)
        self.combo_category.grid(row=0, column=3, padx=5, pady=5)
        self.combo_category.current(0)
        
        tk.Label(frame_add, text="Дата (ГГГГ-ММ-ДД):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_date = tk.Entry(frame_add, width=15)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(frame_add, text="Добавить", command=self.add_expense, bg="#4CAF50", fg="white").grid(row=1, column=2, columnspan=2, pady=5, sticky="we", padx=5)
        
        # --- Фильтрация и подсчет (ОБНОВЛЕНО) ---
        frame_filter = tk.LabelFrame(root, text="Фильтр и аналитика")
        frame_filter.pack(padx=10, pady=5, fill="x")
        
        tk.Label(frame_filter, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category = ttk.Combobox(frame_filter, values=["Все", "Еда", "Транспорт", "Развлечения", "Счета", "Другое"], width=15)
        self.filter_category.current(0)
        self.filter_category.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(frame_filter, text="Применить фильтр", command=self.update_table).grid(row=0, column=2, columnspan=2, padx=10, sticky="we")

        tk.Label(frame_filter, text="Дата с:").grid(row=1, column=0, padx=5, pady=5)
        self.filter_date_start = tk.Entry(frame_filter, width=15)
        self.filter_date_start.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_filter, text="Дата по:").grid(row=1, column=2, padx=5, pady=5)
        self.filter_date_end = tk.Entry(frame_filter, width=15)
        self.filter_date_end.grid(row=1, column=3, padx=5, pady=5)
        
        self.label_total = tk.Label(frame_filter, text="Итого за период: 0.00 руб.", font=("Arial", 11, "bold"))
        self.label_total.grid(row=2, column=0, columnspan=4, pady=5)

        # --- Таблица ---
        columns = ("amount", "category", "date")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.heading("amount", text="Сумма (руб.)")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
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
            json.dump(self.expenses, file, ensure_ascii=False, indent=4)

    def add_expense(self):
        amount_str = self.entry_amount.get()
        category = self.combo_category.get()
        date_str = self.entry_date.get()
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом (например, 150.50)!")
            return
            
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД (например, 2026-04-29).")
            return
            
        self.expenses.append({"amount": amount, "category": category, "date": date_str})
        self.save_data()
        self.update_table()
        self.entry_amount.delete(0, tk.END)
        messagebox.showinfo("Успех", "Запись успешно добавлена!")

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        filter_cat = self.filter_category.get()
        start_date_str = self.filter_date_start.get().strip()
        end_date_str = self.filter_date_end.get().strip()
        
        start_date = None
        end_date = None
        
        if start_date_str:
            try: start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError: pass 
            
        if end_date_str:
            try: end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            except ValueError: pass

        total = 0.0
        
        for exp in self.expenses:
            cat_match = (filter_cat == "Все" or exp["category"] == filter_cat)
            date_match = True
            
            try:
                exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")
                if start_date and exp_date < start_date:
                    date_match = False
                if end_date and exp_date > end_date:
                    date_match = False
            except ValueError:
                pass 

            if cat_match and date_match:
                self.tree.insert("", "end", values=(f"{exp['amount']:.2f}", exp["category"], exp["date"]))
                total += float(exp["amount"])
                
        self.label_total.config(text=f"Итого за период: {total:.2f} руб.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
