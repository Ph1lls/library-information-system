from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt


class TableViewer(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_table = None
        self.tables_with_non_unique_ids = ['discount_occupations', 'book_genre', 'book_author']
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Table selection
        self.table_list = QListWidget()
        self.table_list.addItems(self.db.get_tables())
        self.table_list.clicked.connect(self.load_table_data)
        layout.addWidget(QLabel("Выберите таблицу:"))
        layout.addWidget(self.table_list)

        # CRUD buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить запись")
        self.add_btn.clicked.connect(self.add_record)
        self.add_btn.setEnabled(False)

        self.delete_btn = QPushButton("Удалить запись")
        self.delete_btn.clicked.connect(self.delete_record)
        self.delete_btn.setEnabled(False)

        self.save_btn = QPushButton("Сохранить изменения")
        self.save_btn.clicked.connect(self.save_changes)
        self.save_btn.setEnabled(False)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        # Table display
        self.table = QTableWidget()
        self.table.cellChanged.connect(self.on_cell_changed)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_table_data(self):
        self.current_table = self.table_list.currentItem().text()
        columns, rows = self.db.get_table_data(self.current_table)

        self.table.setColumnCount(len(columns))
        self.table.setRowCount(len(rows))
        self.table.setHorizontalHeaderLabels(columns)

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                if j == 0 and self.current_table not in self.tables_with_non_unique_ids:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, j, item)

        self.add_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.save_btn.setEnabled(False)

    def on_cell_changed(self, row, col):
        self.save_btn.setEnabled(True)

    def add_record(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        if self.current_table not in self.tables_with_non_unique_ids:
            # Для таблиц с уникальными ID - генерируем новый ID
            max_id = 0
            for i in range(self.table.rowCount() - 1):  # Исключаем только что добавленную строку
                id_item = self.table.item(i, 0)
                if id_item and id_item.text().isdigit():
                    current_id = int(id_item.text())
                    if current_id > max_id:
                        max_id = current_id

            new_id = max_id + 1
            id_item = QTableWidgetItem(str(new_id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, id_item)

            # Остальные поля оставляем пустыми
            for col in range(1, self.table.columnCount()):
                self.table.setItem(row, col, QTableWidgetItem(""))
        else:
            # Для таблиц с повторяющимися ID - все поля пустые
            for col in range(self.table.columnCount()):
                self.table.setItem(row, col, QTableWidgetItem(""))

        self.save_btn.setEnabled(True)

    def delete_record(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        if self.current_table not in self.tables_with_non_unique_ids:
            # Для таблиц с уникальными ID - проверяем внешние ключи
            id_item = self.table.item(selected_row, 0)
            if not id_item:
                return

            record_id = id_item.text()

            try:
                cursor = self.db.conn.cursor()
                cursor.execute(f"SHOW KEYS FROM {self.current_table} WHERE Key_name = 'PRIMARY'")
                pk_info = cursor.fetchone()
                if not pk_info:
                    QMessageBox.warning(self, "Ошибка", "Не удалось определить первичный ключ таблицы")
                    return

                pk_column = pk_info[4]

                cursor.execute("""
                    SELECT TABLE_NAME, COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                    WHERE REFERENCED_TABLE_NAME = %s 
                    AND REFERENCED_COLUMN_NAME = %s
                """, (self.current_table, pk_column))

                foreign_keys = cursor.fetchall()

                if foreign_keys:
                    for fk in foreign_keys:
                        table_name, column_name = fk
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name} 
                            WHERE {column_name} = %s
                        """, (record_id,))
                        count = cursor.fetchone()[0]

                        if count > 0:
                            QMessageBox.warning(
                                self, "Ошибка удаления",
                                f"Эта запись используется в таблице '{table_name}' ({count} раз).\n"
                                "Сначала удалите или измените эту запись."
                            )
                            return

                self.table.removeRow(selected_row)
                self.save_btn.setEnabled(True)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при проверке связей: {str(e)}")
        else:
            # Для таблиц с повторяющимися ID - просто удаляем строку
            self.table.removeRow(selected_row)
            self.save_btn.setEnabled(True)

    def save_changes(self):
        try:
            cursor = self.db.conn.cursor()
            columns = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]

            if self.current_table in self.tables_with_non_unique_ids:
                # Для таблиц с составным ключом используем полную перезапись
                cursor.execute(f"DELETE FROM {self.current_table}")

                # Вставляем все записи из таблицы
                for row in range(self.table.rowCount()):
                    record = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        record.append(item.text() if item else "")

                    # Проверяем, что запись не пустая
                    if any(record):
                        columns_str = ", ".join(columns)
                        placeholders = ", ".join(["%s"] * len(columns))
                        query = f"INSERT INTO {self.current_table} ({columns_str}) VALUES ({placeholders})"
                        cursor.execute(query, record)
            else:
                # Для таблиц с уникальным ID
                cursor.execute(f"SHOW KEYS FROM {self.current_table} WHERE Key_name = 'PRIMARY'")
                pk_info = cursor.fetchone()
                if not pk_info:
                    QMessageBox.warning(self, "Ошибка", "Не удалось определить первичный ключ таблицы")
                    return

                pk_column = pk_info[4]

                # Удаляем записи, которых нет в таблице
                cursor.execute(f"SELECT {pk_column} FROM {self.current_table}")
                db_ids = {str(row[0]) for row in cursor.fetchall()}

                table_ids = set()
                for row in range(self.table.rowCount()):
                    id_item = self.table.item(row, 0)
                    if id_item:
                        table_ids.add(id_item.text())

                # Удаляем записи из БД, которых нет в таблице
                for record_id in db_ids - table_ids:
                    cursor.execute(f"DELETE FROM {self.current_table} WHERE {pk_column} = %s", (record_id,))

                # Обновляем или добавляем записи
                for row in range(self.table.rowCount()):
                    record = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        record.append(item.text() if item else "")

                    if not record[0]:  # Пропускаем записи без ID
                        continue

                    cursor.execute(f"SELECT COUNT(*) FROM {self.current_table} WHERE {pk_column} = %s", (record[0],))
                    exists = cursor.fetchone()[0] > 0

                    if exists:
                        # Обновляем существующую запись
                        set_clause = ", ".join([f"{col} = %s" for col in columns[1:]])
                        query = f"UPDATE {self.current_table} SET {set_clause} WHERE {pk_column} = %s"
                        cursor.execute(query, record[1:] + [record[0]])
                    else:
                        # Добавляем новую запись
                        columns_str = ", ".join(columns)
                        placeholders = ", ".join(["%s"] * len(columns))
                        query = f"INSERT INTO {self.current_table} ({columns_str}) VALUES ({placeholders})"
                        cursor.execute(query, record)

            self.db.conn.commit()
            QMessageBox.information(self, "Успех", "Изменения сохранены")
            self.save_btn.setEnabled(False)

        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения:\n{str(e)}")