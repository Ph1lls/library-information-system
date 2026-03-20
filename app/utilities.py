from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import datetime


class Utilities(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.selected_reader_id = None
        self.setup_ui()

    def setup_ui(self):
        self.tabs = QTabWidget()

        # Вкладка поиска по БД
        self.setup_search_tab()

        # Вкладка читательского билета
        self.setup_library_card_tab()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def setup_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Группа поиска
        search_group = QGroupBox("Поиск по базе данных")
        search_layout = QVBoxLayout()

        # Поле ввода и кнопка поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите запрос...")
        self.search_btn = QPushButton("Искать")
        self.search_btn.clicked.connect(self.global_search)

        # Поле результатов
        self.search_results = QTextEdit()
        self.search_results.setReadOnly(True)
        self.search_results.setFont(QFont("Courier New", 10))

        # Компоновка
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.search_results)
        search_group.setLayout(search_layout)

        layout.addWidget(search_group)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Поиск")

    def setup_library_card_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Группа читательского билета
        card_group = QGroupBox("Читательский билет")
        card_layout = QVBoxLayout()

        # Поиск читателя
        search_layout = QHBoxLayout()
        self.reader_search = QLineEdit()
        self.reader_search.setPlaceholderText("ФИО или ID читателя")
        self.reader_search_btn = QPushButton("Найти")
        self.reader_search_btn.clicked.connect(self.search_reader)
        search_layout.addWidget(self.reader_search)
        search_layout.addWidget(self.reader_search_btn)

        # Список читателей
        self.readers_list = QListWidget()
        self.readers_list.itemClicked.connect(self.select_reader)

        # Кнопка генерации
        self.generate_btn = QPushButton("Сгенерировать билет")
        self.generate_btn.clicked.connect(self.generate_library_card)
        self.generate_btn.setEnabled(False)

        # Поле вывода
        self.card_output = QTextEdit()
        self.card_output.setReadOnly(True)
        self.card_output.setFont(QFont("Courier New", 10))

        # Компоновка
        card_layout.addLayout(search_layout)
        card_layout.addWidget(self.readers_list)
        card_layout.addWidget(self.generate_btn)
        card_layout.addWidget(self.card_output)
        card_group.setLayout(card_layout)

        layout.addWidget(card_group)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Читательский билет")

    def global_search(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите поисковый запрос")
            return

        try:
            cursor = self.db.conn.cursor()
            tables = self.db.get_tables()
            results = []

            for table in tables:
                # Получаем столбцы таблицы
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = [col[0] for col in cursor.fetchall()]

                # Формируем условия поиска
                conditions = " OR ".join([f"{col} LIKE %s" for col in columns])
                sql = f"SELECT * FROM {table} WHERE {conditions}"
                cursor.execute(sql, [f"%{query}%"] * len(columns))
                rows = cursor.fetchall()

                if rows:
                    results.append(f"\n=== {table.upper()} ===\n")

                    # Определяем максимальную ширину для каждого столбца
                    col_widths = [len(col) for col in columns]
                    for row in rows:
                        for i, value in enumerate(row):
                            col_widths[i] = max(col_widths[i], len(str(value or '')))

                    # Формируем строку заголовков
                    header = " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(columns))
                    separator = "-+-".join("-" * col_widths[i] for i in range(len(columns)))
                    results.append(header)
                    results.append(separator)

                    # Формируем строки данных
                    for row in rows:
                        line = " | ".join(str(value or '').ljust(col_widths[i]) for i, value in enumerate(row))
                        results.append(line)

                    results.append("")  # Пустая строка между таблицами

            self.search_results.setPlainText("\n".join(results) if results else "Ничего не найдено")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка поиска:\n{str(e)}")

    def search_reader(self):
        query = self.reader_search.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите ФИО или ID читателя")
            return

        self.readers_list.clear()
        try:
            cursor = self.db.conn.cursor()
            sql = """
                SELECT reader_id, reader_lastname, reader_name, reader_surname 
                FROM readers 
                WHERE CONCAT(reader_lastname, ' ', reader_name) LIKE %s
                OR reader_id = %s
                LIMIT 10
            """
            cursor.execute(sql, (f"%{query}%", query))

            for reader in cursor.fetchall():
                item = QListWidgetItem(f"{reader[0]} - {reader[1]} {reader[2]}")
                item.setData(Qt.UserRole, reader[0])
                self.readers_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка поиска читателя:\n{str(e)}")

    def select_reader(self, item):
        self.selected_reader_id = item.data(Qt.UserRole)
        self.generate_btn.setEnabled(True)

    def generate_library_card(self):
        try:
            cursor = self.db.conn.cursor()

            # Получаем информацию о читателе
            cursor.execute("""
                SELECT r.reader_id, r.reader_lastname, r.reader_name, r.reader_phone, 
                       o.occupation_name, d.discount_name, d.percent
                FROM readers r
                LEFT JOIN occupations o ON r.characteristic_id = o.occupation_id
                LEFT JOIN discount_occupations do ON o.occupation_id = do.occupation_id
                LEFT JOIN discounts d ON do.discount_id = d.discount_id
                WHERE r.reader_id = %s
            """, (self.selected_reader_id,))
            reader = cursor.fetchone()

            if not reader:
                QMessageBox.warning(self, "Ошибка", "Читатель не найден")
                return

            # Получаем историю выдач
            cursor.execute("""
                SELECT b.book_name, a.author_lastname, rt.issue_date, rt.return_date, rt.fine_size
                FROM rentals rt
                JOIN book_copies bc ON rt.copy_id = bc.copy_id
                JOIN books b ON bc.book_id = b.book_id
                LEFT JOIN book_author ba ON b.book_id = ba.book_id
                LEFT JOIN authors a ON ba.author_id = a.author_id
                WHERE rt.reader_id = %s
                ORDER BY rt.issue_date DESC
            """, (self.selected_reader_id,))
            rentals = cursor.fetchall()

            # Формируем текст билета
            card_text = [
                "===== ЧИТАТЕЛЬСКИЙ БИЛЕТ =====",
                f"ID: {reader[0]}",
                f"ФИО: {reader[1]} {reader[2]}",
                f"Телефон: {reader[3]}",
                f"Статус: {reader[4] or 'Не указан'}",
                f"Скидка: {reader[5] or 'Нет'} ({reader[6] or 0}%)",
                f"Дата: {datetime.date.today().strftime('%d.%m.%Y')}",
                "",
                "=== ИСТОРИЯ ВЫДАЧ ===",
                f"{'Книга':<30}{'Автор':<20}{'Выдана':<12}{'Возврат':<12}{'Штраф':<10}",
                "-" * 84
            ]

            # Добавляем информацию о выдачах
            for book, author, issue, ret, fine in rentals:
                issue_date = issue.strftime('%d.%m.%Y') if issue else "Нет"
                ret_date = ret.strftime('%d.%m.%Y') if ret else "Нет"
                fine_text = f"{fine} ₽" if fine else "Нет"

                card_text.append(
                    f"{book[:30]:<30}"
                    f"{author[:20]:<20}"
                    f"{issue_date:<12}"
                    f"{ret_date:<12}"
                    f"{fine_text:<10}"
                )

            self.card_output.setPlainText("\n".join(card_text))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации билета:\n{str(e)}")