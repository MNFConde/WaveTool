from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton


class my_main_windows(QMainWindow):
    def __init__(self):
        super().__init__()
        btn = QPushButton("按钮", self)

if __name__ == "__main__":
    app = QApplication([])
    windows = my_main_windows()
    windows.show()
    app.exec_()