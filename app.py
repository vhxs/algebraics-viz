import sys

from PyQt6.QtWidgets import (
    QApplication,
)

from algebraics.ui.main_widget import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 1000)
    window.show()
    sys.exit(app.exec())
