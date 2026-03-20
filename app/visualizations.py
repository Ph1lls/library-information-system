import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="library_db"
)


class Visualizations(QTabWidget):
    def __init__(self, db):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Создаем вкладки
        self.addTab(self.create_pie_tab(), "Читатели")
        self.addTab(self.create_bar_tab(), "Аренды")
        self.addTab(self.create_books_tab(), "Топ книг")
        self.addTab(self.create_weekday_tab(), "По дням")
        self.addTab(self.create_heatmap_tab(), "Жанры и профессии")

    def create_pie_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        fig = plt.figure(figsize=(10, 6), facecolor='#333333')
        self.plot_reader_distribution(fig)
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        tab.setLayout(layout)
        return tab

    def create_bar_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        fig = plt.figure(figsize=(12, 6), facecolor='#333333')
        self.plot_rentals_by_month(fig)
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        tab.setLayout(layout)
        return tab

    def create_books_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        fig = plt.figure(figsize=(10, 6), facecolor='#333333')
        self.plot_profitable_books(fig)
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        tab.setLayout(layout)
        return tab

    def create_weekday_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        fig = plt.figure(figsize=(10, 6), facecolor='#333333')
        self.plot_weekday_demand(fig)
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        tab.setLayout(layout)
        return tab

    def create_heatmap_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        fig = plt.figure(figsize=(10, 6), facecolor='#333333')
        self.plot_genre_occupation(fig)
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        tab.setLayout(layout)
        return tab

    def plot_reader_distribution(self, fig):
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT o.occupation_name, COUNT(r.reader_id) as count
        FROM readers r
        JOIN specialization_occupation os ON r.characteristic_id = os.characteristic_id
        JOIN occupations o ON os.occupation_id = o.occupation_id
        GROUP BY o.occupation_name
        ORDER BY count DESC
        """
        cursor.execute(query)
        data = cursor.fetchall()

        ax = fig.add_subplot(111, facecolor='#333333')
        if data:
            occupations = [row['occupation_name'] for row in data]
            counts = [row['count'] for row in data]

            colors = ['#FFB6C1', '#FFC0CB', '#FFD1DC', '#FFE4E1', '#F8C8DC']
            wedges, texts, autotexts = ax.pie(
                counts,
                labels=occupations,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                textprops={'color': 'black'},  # Черный цвет для внутренних надписей
                pctdistance=0.8  # Смещаем проценты ближе к центру
            )

            # Белый цвет для внешних подписей
            for text in texts:
                text.set_color('white')
                text.set_fontsize(10)

            # Настройка процентов внутри
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontsize(9)

            ax.set_title('Распределение читателей', pad=20, color='white')
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', color='white')

        cursor.close()

    def plot_rentals_by_month(self, fig):
        cursor = db.cursor()
        query = """
        SELECT MONTH(issue_date) as month, COUNT(*) 
        FROM rentals 
        GROUP BY MONTH(issue_date)
        ORDER BY month
        """
        cursor.execute(query)
        data = cursor.fetchall()

        ax = fig.add_subplot(111, facecolor='#333333')
        months = [datetime(2000, row[0], 1).strftime('%B') for row in data]
        counts = [row[1] for row in data]

        bars = ax.bar(months, counts, color='#FFB6C1', edgecolor='#FF69B4')
        ax.set_title('Аренды по месяцам', pad=20, color='white')
        ax.set_xlabel('Месяц', color='white')
        ax.set_ylabel('Количество', color='white')
        ax.tick_params(axis='x', rotation=45, colors='white')
        ax.tick_params(axis='y', colors='white')

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height}', ha='center', va='bottom', color='white')
        cursor.close()

    def plot_profitable_books(self, fig):
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT 
            b.book_name,
            SUM(
                b.rental_price_per_day * DATEDIFF(
                    IFNULL(r.return_date, CURRENT_DATE), 
                    r.issue_date
                ) * (1 - IFNULL(d.percent, 0)/100)
            ) - SUM(IFNULL(r.fine_size, 0)) AS total_revenue
        FROM books b
        JOIN book_copies bc ON b.book_id = bc.book_id
        JOIN rentals r ON bc.copy_id = r.copy_id
        JOIN readers rd ON r.reader_id = rd.reader_id
        LEFT JOIN specialization_occupation so ON rd.characteristic_id = so.characteristic_id
        LEFT JOIN discount_occupations do ON so.occupation_id = do.occupation_id
        LEFT JOIN discounts d ON do.discount_id = d.discount_id
        GROUP BY b.book_id, b.book_name
        ORDER BY total_revenue DESC
        LIMIT 10
        """

        try:
            cursor.execute(query)
            data = cursor.fetchall()

            ax = fig.add_subplot(111, facecolor='#333333')

            if data:
                books = [row['book_name'][:25] + '...' if len(row['book_name']) > 25 else row['book_name']
                         for row in data]
                revenue = [float(row['total_revenue']) for row in data]

                bars = ax.barh(books, revenue, color='#FFB6C1')

                ax.set_title('Топ 10 самых прибыльных книг (чистая выручка)',
                             pad=20, color='white', fontsize=12)
                ax.set_xlabel('Итоговый доход (руб)', color='white')
                ax.tick_params(axis='x', colors='white')
                ax.tick_params(axis='y', colors='white')
                ax.invert_yaxis()

                # Добавляем значения справа от столбцов
                for i, (book, rev) in enumerate(zip(books, revenue)):
                    ax.text(rev + max(revenue) * 0.01, i,
                            f'{rev:.2f} руб',
                            va='center', color='white', fontsize=9)
            else:
                ax.text(0.5, 0.5, 'Нет данных о доходах',
                        ha='center', va='center', color='white')

            plt.tight_layout()
        except mysql.connector.Error as err:
            print(f"Ошибка базы данных: {err}")
        finally:
            cursor.close()
            

    def plot_weekday_demand(self, fig):
        cursor = db.cursor()
        query = """
        SELECT DAYOFWEEK(issue_date) as weekday, COUNT(*) 
        FROM rentals 
        GROUP BY DAYOFWEEK(issue_date)
        ORDER BY weekday
        """
        cursor.execute(query)
        data = cursor.fetchall()

        ax = fig.add_subplot(111, facecolor='#333333')
        weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        counts = [0] * 7
        for row in data:
            idx = (row[0] + 5) % 7
            counts[idx] = row[1]

        ax.plot(weekdays, counts, marker='o', linestyle='-',
                color='#FF69B4', markersize=8, linewidth=2)
        ax.set_title('Востребованность по дням', pad=20, color='white')
        ax.set_xlabel('День недели', color='white')
        ax.set_ylabel('Аренды', color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(color='#555555', linestyle='--', alpha=0.7)
        cursor.close()

    def plot_genre_occupation(self, fig):
        cursor = db.cursor()
        query = """
        SELECT o.occupation_name, g.genre_name, COUNT(*) 
        FROM rentals r
        JOIN readers rd ON r.reader_id = rd.reader_id
        JOIN specialization_occupation os ON rd.characteristic_id = os.characteristic_id
        JOIN occupations o ON os.occupation_id = o.occupation_id
        JOIN book_copies bc ON r.copy_id = bc.copy_id
        JOIN book_genre bg ON bc.book_id = bg.book_id
        JOIN genres g ON bg.genre_id = g.genre_id
        GROUP BY o.occupation_name, g.genre_name
        """
        cursor.execute(query)
        data = cursor.fetchall()

        # Увеличиваем размер фигуры для лучшего отображения
        fig.set_size_inches(14, 10)
        ax = fig.add_subplot(111, facecolor='#333333')

        df = pd.DataFrame(data, columns=['occupation', 'genre', 'count'])
        pivot_df = df.pivot(index='occupation', columns='genre', values='count').fillna(0)

        # Создаем нежно-розовую палитру
        cmap = sns.light_palette("#FFB6C1", as_cmap=True)

        # Рисуем тепловую карту с настройками
        sns.heatmap(
            pivot_df,
            cmap=cmap,
            ax=ax,
            cbar_kws={'label': 'Количество'},
            linewidths=0.5,
            linecolor='#555555',
            annot=True,  # Добавляем значения в ячейки
            fmt='g',  # Общий формат чисел
            annot_kws={'size': 9, 'color': 'black'}  # Настройки аннотаций
        )

        # Настройка подписей осей
        ax.set_title('Жанры и профессии', pad=25, color='white', fontsize=14)
        ax.set_xlabel('Жанры', color='white', labelpad=15, fontsize=12)
        ax.set_ylabel('Профессии', color='white', labelpad=15, fontsize=12)

        # Настройка подписей жанров (x-axis)
        plt.setp(
            ax.get_xticklabels(),
            rotation=45,
            ha='right',
            rotation_mode='anchor',
            fontsize=10,
            color='white'
        )

        # Настройка подписей профессий (y-axis)
        plt.setp(
            ax.get_yticklabels(),
            fontsize=10,
            color='white'
        )

        # Настройка цветовой шкалы
        cbar = ax.collections[0].colorbar
        cbar.ax.yaxis.set_tick_params(color='white')
        cbar.outline.set_edgecolor('white')
        plt.setp(cbar.ax.get_yticklabels(), color='white', fontsize=10)
        cbar.set_label('Количество', color='white', fontsize=12)

        # Автоматическая регулировка отступов
        plt.tight_layout(pad=3.0)

        cursor.close()

