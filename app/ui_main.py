from PyQt5.QtWidgets import QTabWidget, QWidget
from table_viewer import TableViewer
from procedure_runner import ProcedureRunner
from utilities import Utilities
from visualizations import Visualizations  # Добавьте этот импорт

class MainUI(QTabWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("📚 Библиотечный интерфейс")
        self.resize(900, 600)

        self.viewer_tab = TableViewer(self.db)
        self.proc_tab = ProcedureRunner(self.db)
        self.util_tab = Utilities(self.db)
        self.viz_tab = Visualizations(self.db)  # Добавьте эту строку

        self.addTab(self.viewer_tab, "Таблицы")
        self.addTab(self.proc_tab, "Процедуры")
        self.addTab(self.util_tab, "Утилиты")
        self.addTab(self.viz_tab, "Визуализация")  # Добавьте эту строку