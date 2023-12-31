from my_logging import logger
import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QPushButton, QApplication
from dbf_reading import ReadingWindow
from dbf_creating import CreatingWindow


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('DBF reader')
        self.setFixedSize(300, 100)
        self.layout = QWidget()
        self.reading_window = None
        self.creating_window = None
        self.main_layout = QGridLayout()
        self.btn_read_dbf = QPushButton('Чтение DBF файлов')
        self.btn_read_dbf.clicked.connect(self.show_reading_window)
        self.btn_create_dbf = QPushButton('Создание DBF файлов')
        self.btn_create_dbf.clicked.connect(self.show_creating_window)
        self.main_layout.addWidget(self.btn_read_dbf, 0, 0)
        self.main_layout.addWidget(self.btn_create_dbf, 1, 0)
        self.layout.setLayout(self.main_layout)
        self.setCentralWidget(self.layout)

    def show_reading_window(self):
        """
        :return: показ окна редактирования DBF файла по кнопке
        """
        if self.reading_window is None:
            self.reading_window = ReadingWindow()
        self.reading_window.show()

    def show_creating_window(self):
        """
        :return: показ окна создания DBF файла по кнопке
        """
        if self.creating_window is None:
            self.creating_window = CreatingWindow()
        self.creating_window.show()

    def closeEvent(self, event):
        """
        :param event: передается событие закрытия окна
        :return: закрывает все окна, которые в данный момент открыты
        """
        app.closeAllWindows()


if __name__ == '__main__':
    logger.info(f'Запущен файл {__file__}')
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec()
