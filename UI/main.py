from linprod_ui import Ui_MainWindow
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication, QMainWindow
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()

        sys.exit(app.exec())

main()