from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit,
    QDateEdit, QHBoxLayout, QGroupBox, QTabWidget
)
from PyQt5.QtCore import QDate, Qt
import traceback


class ProcedureRunner(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.tabs = QTabWidget()
        self.result_areas = {}

        self.init_tabs()

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def init_tabs(self):
        def create_group(title, widgets, proc_number):
            group = QGroupBox(title)
            vbox = QVBoxLayout()
            for w in widgets:
                vbox.addWidget(w)
            result_area = QTextEdit()
            result_area.setReadOnly(True)
            result_area.setFontFamily("Courier New")
            result_area.setLineWrapMode(QTextEdit.NoWrap)
            result_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            result_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.result_areas[proc_number] = result_area
            vbox.addWidget(result_area)
            group.setLayout(vbox)
            return group

        # Tab 1: Readers by specialization and occupation
        tab1 = QWidget()
        vbox1 = QVBoxLayout()
        self.input_spec = QLineEdit()
        self.input_spec.setPlaceholderText("Специальность (оставьте пустым для всех)")
        self.input_occ = QLineEdit()
        self.input_occ.setPlaceholderText("Профессия (оставьте пустым для всех)")
        btn1 = QPushButton("Выполнить")
        btn1.clicked.connect(self.run_proc1)
        vbox1.addWidget(create_group("Читатели по характеристике", [self.input_spec, self.input_occ, btn1], 1))
        tab1.setLayout(vbox1)
        self.tabs.addTab(tab1, "Процедура 1. ЧХ")

        # Tab 2: Readers with a book
        tab2 = QWidget()
        vbox2 = QVBoxLayout()
        self.input_book_name = QLineEdit()
        self.input_book_name.setPlaceholderText("Название книги")
        btn2 = QPushButton("Выполнить")
        btn2.clicked.connect(self.run_proc2)
        vbox2.addWidget(create_group("Читатели с книгой", [self.input_book_name, btn2], 2))
        tab2.setLayout(vbox2)
        self.tabs.addTab(tab2, "Процедура 2. ЧК")

        # Tab 3: Book rental history
        tab3 = QWidget()
        vbox3 = QVBoxLayout()
        self.input_book_history = QLineEdit()
        self.input_book_history.setPlaceholderText("Название книги")
        self.start_date3 = QDateEdit()
        self.start_date3.setCalendarPopup(True)
        self.start_date3.setDate(QDate.currentDate().addMonths(-1))
        self.end_date3 = QDateEdit()
        self.end_date3.setCalendarPopup(True)
        self.end_date3.setDate(QDate.currentDate())
        date_layout3 = QHBoxLayout()
        date_layout3.addWidget(QLabel("С:"))
        date_layout3.addWidget(self.start_date3)
        date_layout3.addWidget(QLabel("По:"))
        date_layout3.addWidget(self.end_date3)
        date_widget3 = QWidget()
        date_widget3.setLayout(date_layout3)
        btn3 = QPushButton("Выполнить")
        btn3.clicked.connect(self.run_proc3)
        vbox3.addWidget(create_group("История аренды книги", [self.input_book_history, date_widget3, btn3], 3))
        tab3.setLayout(vbox3)
        self.tabs.addTab(tab3, "Процедура 3. ИА")

        # Tab 4: Librarian performance
        tab4 = QWidget()
        vbox4 = QVBoxLayout()
        self.start_date4 = QDateEdit()
        self.start_date4.setCalendarPopup(True)
        self.start_date4.setDate(QDate.currentDate().addMonths(-1))
        self.end_date4 = QDateEdit()
        self.end_date4.setCalendarPopup(True)
        self.end_date4.setDate(QDate.currentDate())
        date_layout4 = QHBoxLayout()
        date_layout4.addWidget(QLabel("С:"))
        date_layout4.addWidget(self.start_date4)
        date_layout4.addWidget(QLabel("По:"))
        date_layout4.addWidget(self.end_date4)
        date_widget4 = QWidget()
        date_widget4.setLayout(date_layout4)
        btn4 = QPushButton("Выполнить")
        btn4.clicked.connect(self.run_proc4)
        vbox4.addWidget(create_group("Эффективность библиотекарей", [date_widget4, btn4], 4))
        tab4.setLayout(vbox4)
        self.tabs.addTab(tab4, "Процедура 4. ЭБ")

        # Tab 5: Overdue returns
        tab5 = QWidget()
        vbox5 = QVBoxLayout()
        btn5 = QPushButton("Выполнить")
        btn5.clicked.connect(self.run_proc5)
        vbox5.addWidget(create_group("Просроченные возвраты", [btn5], 5))
        tab5.setLayout(vbox5)
        self.tabs.addTab(tab5, "Процедура 5. ПВ")

        # Tab 6: Inventory movements
        tab6 = QWidget()
        vbox6 = QVBoxLayout()
        self.start_date6 = QDateEdit()
        self.start_date6.setCalendarPopup(True)
        self.start_date6.setDate(QDate.currentDate().addMonths(-1))
        self.end_date6 = QDateEdit()
        self.end_date6.setCalendarPopup(True)
        self.end_date6.setDate(QDate.currentDate())
        date_layout6 = QHBoxLayout()
        date_layout6.addWidget(QLabel("С:"))
        date_layout6.addWidget(self.start_date6)
        date_layout6.addWidget(QLabel("По:"))
        date_layout6.addWidget(self.end_date6)
        date_widget6 = QWidget()
        date_widget6.setLayout(date_layout6)
        btn6 = QPushButton("Выполнить")
        btn6.clicked.connect(self.run_proc6)
        vbox6.addWidget(create_group("Движение книг", [date_widget6, btn6], 6))
        tab6.setLayout(vbox6)
        self.tabs.addTab(tab6, "Процедура 6. ДК")

        # Tab 7: Librarian workload
        tab7 = QWidget()
        vbox7 = QVBoxLayout()
        self.input_librarian = QLineEdit()
        self.input_librarian.setPlaceholderText("Фамилия библиотекаря")
        self.start_date7 = QDateEdit()
        self.start_date7.setCalendarPopup(True)
        self.start_date7.setDate(QDate.currentDate().addMonths(-1))
        self.end_date7 = QDateEdit()
        self.end_date7.setCalendarPopup(True)
        self.end_date7.setDate(QDate.currentDate())
        date_layout7 = QHBoxLayout()
        date_layout7.addWidget(QLabel("С:"))
        date_layout7.addWidget(self.start_date7)
        date_layout7.addWidget(QLabel("По:"))
        date_layout7.addWidget(self.end_date7)
        date_widget7 = QWidget()
        date_widget7.setLayout(date_layout7)
        btn7 = QPushButton("Выполнить")
        btn7.clicked.connect(self.run_proc7)
        vbox7.addWidget(create_group("Нагрузка библиотекаря", [self.input_librarian, date_widget7, btn7], 7))
        tab7.setLayout(vbox7)
        self.tabs.addTab(tab7, "Процедура 7. НБ")

        # Tab 8: Genre statistics
        tab8 = QWidget()
        vbox8 = QVBoxLayout()
        self.input_genre = QLineEdit()
        self.input_genre.setPlaceholderText("Название жанра")
        btn8 = QPushButton("Выполнить")
        btn8.clicked.connect(self.run_proc8)
        vbox8.addWidget(create_group("Статистика по жанрам", [self.input_genre, btn8], 8))
        tab8.setLayout(vbox8)
        self.tabs.addTab(tab8, "Процедура 8. СЖ")

        # Tab 9: Book financials
        tab9 = QWidget()
        vbox9 = QVBoxLayout()
        self.input_book_fin = QLineEdit()
        self.input_book_fin.setPlaceholderText("Название книги")
        btn9 = QPushButton("Выполнить")
        btn9.clicked.connect(self.run_proc9)
        vbox9.addWidget(create_group("Финансовая информация о книге", [self.input_book_fin, btn9], 9))
        tab9.setLayout(vbox9)
        self.tabs.addTab(tab9, "Процедура 9. ФИ")

        # Tab 10: Top books
        tab10 = QWidget()
        vbox10 = QVBoxLayout()
        self.start_date10 = QDateEdit()
        self.start_date10.setCalendarPopup(True)
        self.start_date10.setDate(QDate.currentDate().addMonths(-1))
        self.end_date10 = QDateEdit()
        self.end_date10.setCalendarPopup(True)
        self.end_date10.setDate(QDate.currentDate())
        date_layout10 = QHBoxLayout()
        date_layout10.addWidget(QLabel("С:"))
        date_layout10.addWidget(self.start_date10)
        date_layout10.addWidget(QLabel("По:"))
        date_layout10.addWidget(self.end_date10)
        date_widget10 = QWidget()
        date_widget10.setLayout(date_layout10)
        btn10 = QPushButton("Выполнить")
        btn10.clicked.connect(self.run_proc10)
        vbox10.addWidget(create_group("Топ книг", [date_widget10, btn10], 10))
        tab10.setLayout(vbox10)
        self.tabs.addTab(tab10, "Процедура 10. ТК")

    def display_results(self, result_sets, proc_number):

        area = self.result_areas[proc_number]
        if not result_sets:
            area.setPlainText("Нет результатов.")
            return

        output = ""
        for columns, rows in result_sets:
            # 1. Получаем ширину каждой колонки
            col_widths = [len(col) for col in columns]
            for row in rows:
                for i, value in enumerate(row):
                    col_widths[i] = max(col_widths[i], len(str(value)))

            # 2. Формируем строку заголовков
            header = " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(columns))
            separator = "-+-".join("-" * col_widths[i] for i in range(len(columns)))
            output += header + "\n" + separator + "\n"

            # 3. Формируем строки данных
            for row in rows:
                line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(columns)))
                output += line + "\n"
            output += "\n"

        area.setPlainText(output)

    def run_procedure(self, proc_name, params, proc_number):
        try:
            results = self.db.call_procedure(proc_name, params)
            self.display_results(results, proc_number)
        except Exception as e:
            self.result_areas[proc_number].setPlainText(f"[Ошибка при вызове {proc_name}]\n{str(e)}")
            print(traceback.format_exc())

    def run_proc1(self):
        spec = self.input_spec.text() or None
        occ = self.input_occ.text() or None
        self.run_procedure("GetReadersBySpecializationAndOccupation", (spec, occ), 1)

    def run_proc2(self):
        book_name = self.input_book_name.text()
        self.run_procedure("GetReadersWithBook", (book_name,), 2)

    def run_proc3(self):
        book_name = self.input_book_history.text()
        start = self.start_date3.date().toString("yyyy-MM-dd")
        end = self.end_date3.date().toString("yyyy-MM-dd")
        self.run_procedure("GetBookRentalHistory", (book_name, start, end), 3)

    def run_proc4(self):
        start = self.start_date4.date().toString("yyyy-MM-dd")
        end = self.end_date4.date().toString("yyyy-MM-dd")
        self.run_procedure("GetLibrarianPerformance", (start, end), 4)

    def run_proc5(self):
        self.run_procedure("GetOverdueReturns", (), 5)

    def run_proc6(self):
        start = self.start_date6.date().toString("yyyy-MM-dd")
        end = self.end_date6.date().toString("yyyy-MM-dd")
        self.run_procedure("GetInventoryMovements", (start, end), 6)

    def run_proc7(self):
        librarian = self.input_librarian.text()
        start_date = self.start_date7.date()
        end_date = self.end_date7.date()

        # Проверка, что начальная дата не позже конечной
        if start_date > end_date:
            self.result_areas[7].setPlainText("Ошибка: начальная дата не может быть позже конечной")
            return

        start = start_date.toString("yyyy-MM-dd")
        end = end_date.toString("yyyy-MM-dd")
        self.run_procedure("GetLibrarianWorkload", (librarian, start, end), 7)

    def run_proc8(self):
        genre = self.input_genre.text()
        self.run_procedure("GetAverageReturnTimeByGenre", (genre,), 8)

    def run_proc9(self):
        book_name = self.input_book_fin.text()
        self.run_procedure("GetBookFinancials", (book_name,), 9)

    def run_proc10(self):
        start = self.start_date10.date().toString("yyyy-MM-dd")
        end = self.end_date10.date().toString("yyyy-MM-dd")
        self.run_procedure("GetTopBooks", (start, end), 10)