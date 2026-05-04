import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("950x700")
        self.root.resizable(True, True)
        
        # Файл данных
        self.data_file = "movies.json"
        self.movies = []
        
        # Жанры фильмов
        self.genres = [
            "Боевик", "Комедия", "Драма", "Фантастика", 
            "Ужасы", "Триллер", "Мелодрама", "Детектив", 
            "Приключения", "Аниме", "Документальный", "Криминал", 
            "Вестерн", "Мюзикл", "Семейный", "Спортивный", "Другое"
        ]
        
        # Загрузка данных
        self.load_data()
        
        # Настройка интерфейса
        self.setup_gui()
        
        # Обновление таблицы
        self.refresh_table()
        
    def setup_gui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # ========== Фрейм для добавления фильма ==========
        input_frame = ttk.LabelFrame(main_frame, text="Добавление нового фильма", padding="15")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Название
        ttk.Label(input_frame, text="Название:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_entry = ttk.Entry(input_frame, width=30, font=("Arial", 10))
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        
        # Жанр
        ttk.Label(input_frame, text="Жанр:", font=("Arial", 10, "bold")).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        self.genre_combo = ttk.Combobox(input_frame, values=self.genres, width=15, font=("Arial", 10))
        self.genre_combo.grid(row=0, column=4, padx=5, pady=5)
        self.genre_combo.set(self.genres[0])
        
        # Год выпуска
        ttk.Label(input_frame, text="Год выпуска:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.year_entry = ttk.Entry(input_frame, width=10, font=("Arial", 10))
        self.year_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Рейтинг
        ttk.Label(input_frame, text="Рейтинг (0-10):", font=("Arial", 10, "bold")).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.rating_entry = ttk.Entry(input_frame, width=10, font=("Arial", 10))
        self.rating_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_button = ttk.Button(input_frame, text="🎬 Добавить фильм", command=self.add_movie)
        self.add_button.grid(row=1, column=4, padx=10, pady=5)
        
        # ========== Фрейм для фильтрации ==========
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация фильмов", padding="15")
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Фильтр по жанру
        ttk.Label(filter_frame, text="Фильтр по жанру:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.filter_genre = ttk.Combobox(filter_frame, values=["Все"] + self.genres, width=15)
        self.filter_genre.grid(row=0, column=1, padx=5)
        self.filter_genre.set("Все")
        self.filter_genre.bind('<<ComboboxSelected>>', lambda e: self.refresh_table())
        
        # Фильтр по году
        ttk.Label(filter_frame, text="Фильтр по году:", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.filter_year = ttk.Entry(filter_frame, width=10)
        self.filter_year.grid(row=0, column=3, padx=5)
        self.filter_year.bind('<KeyRelease>', lambda e: self.refresh_table())
        
        ttk.Label(filter_frame, text="(например: 1994)", foreground="gray").grid(row=0, column=4, sticky=tk.W)
        
        # Кнопка сброса фильтров
        self.clear_filters_btn = ttk.Button(filter_frame, text="🗑️ Сбросить фильтры", command=self.clear_filters)
        self.clear_filters_btn.grid(row=0, column=5, padx=10)
        
        # ========== Таблица с фильмами ==========
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Создание таблицы Treeview
        columns = ("id", "title", "genre", "year", "rating")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Заголовки
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Название фильма")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год выпуска")
        self.tree.heading("rating", text="Рейтинг")
        
        # Настройка колонок
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("title", width=300, anchor="w")
        self.tree.column("genre", width=120, anchor="center")
        self.tree.column("year", width=100, anchor="center")
        self.tree.column("rating", width=100, anchor="center")
        
        # Полоса прокрутки
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Размещение таблицы и скроллбаров
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # ========== Кнопки управления ==========
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, pady=10)
        
        self.edit_btn = ttk.Button(buttons_frame, text="✏️ Редактировать", command=self.edit_movie)
        self.edit_btn.grid(row=0, column=0, padx=5)
        
        self.delete_btn = ttk.Button(buttons_frame, text="🗑️ Удалить выбранный", command=self.delete_movie)
        self.delete_btn.grid(row=0, column=1, padx=5)
        
        self.save_btn = ttk.Button(buttons_frame, text="💾 Сохранить в JSON", command=self.save_data)
        self.save_btn.grid(row=0, column=2, padx=5)
        
        self.load_btn = ttk.Button(buttons_frame, text="📂 Загрузить из JSON", command=self.load_data)
        self.load_btn.grid(row=0, column=3, padx=5)
        
        # ========== Статистика ==========
        stats_frame = ttk.LabelFrame(main_frame, text="Статистика кинотеки", padding="10")
        stats_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 10))
        self.stats_label.grid(row=0, column=0, sticky=tk.W)
        
        self.update_statistics()
    
    def validate_year(self, year_string):
        """Проверка года (должен быть числом)"""
        try:
            year = int(year_string)
            current_year = datetime.now().year
            # Реалистичный диапазон: 1888 (первые фильмы) - текущий год + 5
            return 1888 <= year <= current_year + 5
        except ValueError:
            return False
    
    def validate_rating(self, rating_string):
        """Проверка рейтинга (от 0 до 10)"""
        try:
            rating = float(rating_string)
            return 0 <= rating <= 10
        except ValueError:
            return False
    
    def add_movie(self):
        """Добавление нового фильма"""
        title = self.title_entry.get().strip()
        genre = self.genre_combo.get()
        year = self.year_entry.get().strip()
        rating = self.rating_entry.get().strip()
        
        # Валидация названия
        if not title:
            messagebox.showerror("Ошибка валидации", "Пожалуйста, введите название фильма")
            return
        
        # Валидация года
        if not year:
            messagebox.showerror("Ошибка валидации", "Пожалуйста, введите год выпуска")
            return
        
        if not self.validate_year(year):
            messagebox.showerror("Ошибка валидации", 
                               f"Неверный год!\nГод должен быть числом от 1888 до {datetime.now().year + 5}\nПримеры: 1994, 2020, 2024")
            return
        
        # Валидация рейтинга
        if not rating:
            messagebox.showerror("Ошибка валидации", "Пожалуйста, введите рейтинг фильма")
            return
        
        if not self.validate_rating(rating):
            messagebox.showerror("Ошибка валидации", 
                               "Неверный рейтинг!\nРейтинг должен быть числом от 0 до 10\nПримеры: 8.5, 9, 7.2")
            return
        
        # Создание записи
        new_id = max([m['id'] for m in self.movies]) + 1 if self.movies else 1
        movie = {
            "id": new_id,
            "title": title,
            "genre": genre,
            "year": int(year),
            "rating": float(rating)
        }
        
        self.movies.append(movie)
        self.save_data()
        self.refresh_table()
        
        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)
        self.genre_combo.set(self.genres[0])
        
        # Установка фокуса на поле названия
        self.title_entry.focus()
        
        # Отображение рейтинга звездочками
        stars = "⭐" * int(float(rating)) + "☆" * (10 - int(float(rating)))
        
        messagebox.showinfo("Успех", f"✅ Фильм успешно добавлен!\n\n"
                           f"Название: {title}\n"
                           f"Жанр: {genre}\n"
                           f"Год: {year}\n"
                           f"Рейтинг: {rating}/10\n"
                           f"{stars}")
    
    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите фильм для удаления")
            return
        
        # Подтверждение удаления
        item = self.tree.item(selected[0])
        movie_info = (f"Название: {item['values'][1]}\n"
                     f"Жанр: {item['values'][2]}\n"
                     f"Год: {item['values'][3]}\n"
                     f"Рейтинг: {item['values'][4]}/10")
        
        if messagebox.askyesno("Подтверждение удаления", 
                              f"Вы уверены, что хотите удалить этот фильм?\n\n{movie_info}"):
            movie_id = item['values'][0]
            
            # Удаление из списка
            self.movies = [m for m in self.movies if m['id'] != movie_id]
            
            # Перенумерация ID
            for idx, movie in enumerate(self.movies, 1):
                movie['id'] = idx
            
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "✅ Фильм успешно удален из кинотеки!")
    
    def edit_movie(self):
        """Редактирование выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите фильм для редактирования")
            return
        
        item = self.tree.item(selected[0])
        movie_id = item['values'][0]
        movie = next((m for m in self.movies if m['id'] == movie_id), None)
        
        if movie:
            # Создание окна редактирования
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Редактирование фильма")
            edit_window.geometry("500x400")
            edit_window.resizable(False, False)
            
            # Центрирование окна
            edit_window.transient(self.root)
            edit_window.grab_set()
            
            # Заголовок
            ttk.Label(edit_window, text="Редактирование фильма", font=("Arial", 14, "bold")).pack(pady=10)
            
            # Поля ввода
            frame = ttk.Frame(edit_window, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Название
            ttk.Label(frame, text="Название:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=10)
            title_entry = ttk.Entry(frame, width=35, font=("Arial", 10))
            title_entry.insert(0, movie['title'])
            title_entry.grid(row=0, column=1, pady=10, padx=10)
            
            # Жанр
            ttk.Label(frame, text="Жанр:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=10)
            genre_combo = ttk.Combobox(frame, values=self.genres, width=32)
            genre_combo.set(movie['genre'])
            genre_combo.grid(row=1, column=1, pady=10, padx=10)
            
            # Год
            ttk.Label(frame, text="Год выпуска:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=10)
            year_entry = ttk.Entry(frame, width=35, font=("Arial", 10))
            year_entry.insert(0, str(movie['year']))
            year_entry.grid(row=2, column=1, pady=10, padx=10)
            
            # Рейтинг
            ttk.Label(frame, text="Рейтинг (0-10):", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=10)
            rating_entry = ttk.Entry(frame, width=35, font=("Arial", 10))
            rating_entry.insert(0, str(movie['rating']))
            rating_entry.grid(row=3, column=1, pady=10, padx=10)
            
            def save_edit():
                new_title = title_entry.get().strip()
                new_genre = genre_combo.get()
                new_year = year_entry.get().strip()
                new_rating = rating_entry.get().strip()
                
                # Валидация
                if not new_title:
                    messagebox.showerror("Ошибка валидации", "Введите название фильма")
                    return
                
                if not self.validate_year(new_year):
                    messagebox.showerror("Ошибка валидации", 
                                       f"Неверный год! Год должен быть от 1888 до {datetime.now().year + 5}")
                    return
                
                if not self.validate_rating(new_rating):
                    messagebox.showerror("Ошибка валидации", "Рейтинг должен быть от 0 до 10")
                    return
                
                # Обновление данных
                movie['title'] = new_title
                movie['genre'] = new_genre
                movie['year'] = int(new_year)
                movie['rating'] = float(new_rating)
                
                self.save_data()
                self.refresh_table()
                edit_window.destroy()
                messagebox.showinfo("Успех", "✅ Фильм успешно обновлен!")
            
            # Кнопки
            button_frame = ttk.Frame(edit_window)
            button_frame.pack(pady=20)
            
            ttk.Button(button_frame, text="💾 Сохранить", command=save_edit).pack(side=tk.LEFT, padx=10)
            ttk.Button(button_frame, text="❌ Отмена", command=edit_window.destroy).pack(side=tk.LEFT, padx=10)
    
    def refresh_table(self):
        """Обновление таблицы с учетом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Применение фильтров
        filtered_movies = self.movies.copy()
        
        # Фильтр по жанру
        selected_genre = self.filter_genre.get()
        if selected_genre != "Все":
            filtered_movies = [m for m in filtered_movies if m['genre'] == selected_genre]
        
        # Фильтр по году
        filter_year_value = self.filter_year.get().strip()
        if filter_year_value:
            try:
                filter_year_int = int(filter_year_value)
                filtered_movies = [m for m in filtered_movies if m['year'] == filter_year_int]
            except ValueError:
                # Если введено не число, показываем пустой результат
                filtered_movies = []
        
        # Сортировка по году (от новых к старым)
        filtered_movies.sort(key=lambda x: x['year'], reverse=True)
        
        # Добавление в таблицу
        for movie in filtered_movies:
            # Форматирование рейтинга
            rating_display = f"{movie['rating']:.1f}"
            
            self.tree.insert("", tk.END, values=(
                movie['id'],
                movie['title'],
                movie['genre'],
                movie['year'],
                rating_display
            ))
        
        # Обновление статистики
        self.update_statistics()
    
    def update_statistics(self):
        """Обновление статистики"""
        if not self.movies:
            self.stats_label.config(text="📊 Всего фильмов: 0 | ⭐ Средний рейтинг: 0.0 | 📅 Диапазон годов: Н/Д | 🎭 Жанров: 0")
            return
        
        total_movies = len(self.movies)
        avg_rating = sum(m['rating'] for m in self.movies) / total_movies
        years = [m['year'] for m in self.movies]
        year_range = f"{min(years)}-{max(years)}"
        unique_genres = len(set(m['genre'] for m in self.movies))
        
        # Находим фильм с максимальным рейтингом
        top_movie = max(self.movies, key=lambda x: x['rating'])
        
        stats_text = (f"📊 Всего фильмов: {total_movies} | "
                     f"⭐ Средний рейтинг: {avg_rating:.1f} | "
                     f"📅 Годы: {year_range} | "
                     f"🎭 Жанров: {unique_genres} | "
                     f"🏆 Топ фильм: '{top_movie['title']}' ({top_movie['rating']:.1f}⭐)")
        
        self.stats_label.config(text=stats_text)
    
    def clear_filters(self):
        """Сброс всех фильтров"""
        self.filter_genre.set("Все")
        self.filter_year.delete(0, tk.END)
        self.refresh_table()
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные:\n{str(e)}")
            return False
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if not os.path.exists(self.data_file):
            # Создание пустого файла
            self.movies = []
            self.save_data()
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.movies = json.load(f)
            self.refresh_table()
            
            # Подсчет статистики для сообщения
            total = len(self.movies)
            avg_rating = sum(m['rating'] for m in self.movies) / total if total > 0 else 0
            
            messagebox.showinfo("Успех", f"✅ Данные успешно загружены!\n\n"
                               f"Загружено фильмов: {total}\n"
                               f"Средний рейтинг: {avg_rating:.1f}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
            self.movies = []

def main():
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()

if __name__ == "__main__":
    main()