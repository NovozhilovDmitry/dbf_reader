from my_logging import logger
import sys
import traceback
import pathlib
from datetime import datetime
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QRunnable, QThreadPool, QSettings, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (QMainWindow,
                             QWidget,
                             QLabel,
                             QGridLayout,
                             QApplication,
                             QLineEdit,
                             QPushButton,
                             QFileDialog,
                             QMessageBox,
                             QTableWidget,
                             QTableWidgetItem,
                             QHeaderView,
                             )
from functions import get_len_of_table
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600


class WorkerSignals(QObject):
    finish = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:  # выполняем переданный из window метод
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()  # формирует ошибку
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:  # если ошибок не было, то формируем сигнал .result и передаем результат `result`
            self.signals.result.emit(result)  # Вернуть результат обработки
        finally:
            self.signals.finish.emit()  # Готово


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle('Эмулятор ЕПВВ')  # заголовок главного окна
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.btn_icon = QPixmap("others/folder.png")
        self.layout = QWidget()
        self.main_layout = QGridLayout()
        self.settings = QSettings('config.ini', QSettings.Format.IniFormat)
        self.threadpool = QThreadPool()
        self.header_layout()  # функция с добавленными элементами интерфейса для верхней части
        self.layout.setLayout(self.main_layout)
        self.setCentralWidget(self.layout)
        self.get_settings()

    def print_output(self, s):  # слот для сигнала из потока о завершении выполнения функции
        logger.info(s)

    def finish_message(self):
        """
        done
        :return:
        """
        dlg = QMessageBox()
        dlg.setWindowTitle('DBF')
        dlg.setText('Функция выполнена')
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        button = dlg.exec()

    def thread_handle_files(self):
        """
        done
        :return:
        """
        logger.info(' ')
        worker = Worker(self.fn_main)  # функция, которая выполняется в потоке
        worker.signals.result.connect(self.print_output)  # сообщение после завершения выполнения задачи
        worker.signals.finish.connect(self.finish_message)  # сообщение после завершения потока
        self.threadpool.start(worker)

    def fn_main(self, progress_callback):
        """
        :param progress_callback: результат выполнения функции в потоке
        :return: выполненная функция
        """
        path = self.lineedit_path_to_file.text()
        self.table.setRowCount(get_len_of_table(path))
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(['Имя', 'Дата создания', 'Статус', 'Размер'])
        new_list = format_list_result(list_result)
        row = 0
        for i in new_list:
            self.table.setItem(row, 0, QTableWidgetItem(i[0]))
            self.table.setItem(row, 1, QTableWidgetItem(i[1]))
            self.table.setItem(row, 2, QTableWidgetItem(i[2]))
            self.table.setItem(row, 3, QTableWidgetItem(i[3]))
            row += 1
        self.list_pdb.clear()
        for i in self.pdb_name_list:
            self.list_pdb.addItem(i)
        self.table.setSortingEnabled(True)

        return f'функция {traceback.extract_stack()[-1][2]} выполнена'

    def paths_validation(self):
        """
        done
        :return:
        """
        full_str_error = []
        if not pathlib.Path(self.lineedit_path_to_file.text()).exists():
            full_str_error.append(self.lineedit_path_to_file.text())
        if len(full_str_error) == 0:
            logger.info('Успешная валидация путей')
            return True
        if len(full_str_error) > 0:
            error_message = 'Проверьте корректность следующих введенных путей:\n'
            for i in full_str_error:
                error_message = error_message + i + '\n'
            dlg = QMessageBox()
            dlg.setWindowTitle('Ошибка валидации путей')
            dlg.setText(error_message)
            dlg.setStandardButtons(QMessageBox.StandardButton.Close)
            button = dlg.exec()
            logger.error('Ошибка валидации путей')
            return False

    def header_layout(self):
        """
        :return: добавление виджетов в верхнюю часть интерфейса на главном окне
        """
        self.label_path_to_file = QLabel('Путь к файлу')
        self.lineedit_path_to_file = QLineEdit()
        self.lineedit_path_to_file.setPlaceholderText('Укажите путь к DBF файлу')
        self.btn_set_path = self.lineedit_path_to_file.addAction(QIcon(self.btn_icon),
                                                                 QLineEdit.ActionPosition.TrailingPosition)
        self.btn_set_path.triggered.connect(self.get_path)
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.btn_handler = QPushButton('Загрузить данные из таблицы в файл DBF')
        self.btn_handler.clicked.connect(self.thread_handle_files)
        self.main_layout.addWidget(self.label_path_to_file, 0, 0)
        self.main_layout.addWidget(self.lineedit_path_to_file, 0, 1)
        self.main_layout.addWidget(self.btn_handler, 7, 0, 1, 2)

    def get_path(self):
        """
        done
        :return:
        """
        get_dir = QFileDialog.getOpenFileName(self, caption='Выбрать файл')
        if get_dir:
            get_dir = get_dir[0]
        else:
            get_dir = 'Путь не выбран'
        self.lineedit_path_to_file.setText(get_dir)

    def get_settings(self):
        """
        done
        :return: заполнение полей из настроек
        """
        try:
            width = int(self.settings.value('GUI/width'))
            height = int(self.settings.value('GUI/height'))
            x = int(self.settings.value('GUI/x'))
            y = int(self.settings.value('GUI/y'))
            self.setGeometry(x, y, width, height)
            logger.info('Настройки размеров окна загружены.')
        except:
            logger.warning('Настройки размеров окна НЕ загружены. Установлены размеры по умолчанию')
        self.lineedit_path_to_file.setText(self.settings.value('path/dir_path'))
        logger.info('Файл с пользовательскими настройками проинициализирован')

    def closeEvent(self, event):
        """
        done
        :param event: событие, которое можно принять или переопределить при закрытии
        :return: охранение настроек при закрытии приложения
        """
        # сохранение размеров и положения окна
        self.settings.beginGroup('GUI')
        self.settings.setValue('width', self.geometry().width())
        self.settings.setValue('height', self.geometry().height())
        self.settings.setValue('x', self.geometry().x())
        self.settings.setValue('y', self.geometry().y())
        self.settings.endGroup()
        self.settings.beginGroup('path')
        self.settings.setValue('dir_path', self.lineedit_path_to_file.text())
        self.settings.endGroup()
        logger.info(f'Пользовательские настройки сохранены. Файл {__file__} закрыт')


if __name__ == '__main__':
    logger.info(f'Запущен файл {__file__}')
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())

