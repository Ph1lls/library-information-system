import sys
from PyQt5.QtWidgets import QApplication
from db_connection import Database
from ui_main import MainUI


def main():
    app = QApplication(sys.argv)
    db = Database()
    window = MainUI(db)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
