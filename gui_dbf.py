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
                             )
from functions import (get_len_of_table,
                       get_headers_from_dbf,
                       get_value_from_dbf,
                       lower_list
                       )
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
        self.setWindowTitle('Просмотр DBF файлов')  # заголовок главного окна
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
        """
        :param s: сообщение
        :return: когда функция завершается, выводится в лог сообщение из функции, которое указано в return
        """
        logger.info(s)

    def finish_message(self):
        """
        :return: после завершения функции в отдельном потоке выводится окно с данными о затраченном времени
        """
        dlg = QMessageBox()
        dlg.setWindowTitle('DBF')
        dlg.setText(f'Функция выполнена за {self.count_time}')
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.exec()

    def thread_reading_dbf_file(self):
        """
        :return: выполнение переданной функции в отдельном потоке
        """
        logger.info('Начато выполнение чтение DBF файла')
        worker = Worker(self.fn_read_dbf)  # функция, которая выполняется в потоке
        worker.signals.result.connect(self.print_output)  # сообщение после завершения выполнения функции
        worker.signals.finish.connect(self.finish_message)  # сообщение после завершения потока
        self.threadpool.start(worker)

    def fn_read_dbf(self, progress_callback):
        """
        :param progress_callback: результат выполнения функции в потоке
        :return: выполненная функция
        """
        start = datetime.now()
        path = self.lineedit_path_to_file.text()
        count_rows = get_len_of_table(path)
        self.table.setRowCount(count_rows)
        list_of_headers = get_headers_from_dbf(path)
        self.table.setColumnCount(len(list_of_headers))
        self.table.setHorizontalHeaderLabels(list_of_headers)
        #
        # for column, record in enumerate(lower_list(list_of_headers)):
        #     for row in range(0, count_rows):
        #         value = get_value_from_dbf(path, record)
        #         self.table.setItem(row, column, QTableWidgetItem(value[row]))

        self.table.setSortingEnabled(True)
        end = datetime.now()
        self.count_time = end - start
        return f'функция {traceback.extract_stack()[-1][2]} выполнена'

    def add_row_to_table(self):
        """
        :return: добавить новую строку в таблицу
        """
        last_row = self.table.rowCount()
        self.table.insertRow(last_row)

    def delete_some_row_from_table(self):
        """
        :return: удаление выбранной пользователем строки в таблице
        """
        row = self.table.currentRow()
        if row == 0:
            QMessageBox.warning(self, 'ВНИМАНИЕ!', 'ПЕРВУЮ СТРОКУ УДАЛЯТЬ НЕЛЬЗЯ')
        elif row == -1:
            QMessageBox.question(self, 'Сообщение', "Выберите строку, которую вы хотите удалить",
                                 QMessageBox.StandardButton.Ok)
        else:
            msg = QMessageBox.question(self, 'Подтверждение удаления строки',
                                       f"Вы действительно хотите удалить строку <b style='color: red;'>{row + 1}</b>?",
                                       QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                logger.info(f'Пользователь отменил удаление строки {row + 1}')
                return
            elif msg == QMessageBox.StandardButton.Ok:
                logger.info(f'Удалена строка {row + 1}')
                self.table.removeRow(row)
            else:
                logger.warning('Неизвестная ошибка. Не нажаты кнопки Ok/Cancel при подтвеждении удаления строки')

    def thread_creating_dbf_file(self):
        """
        :return: выполнение переданной функции в отдельном потоке
        """
        logger.info('Начато выполнение чтение DBF файла')
        worker = Worker(self.fn_create_dbf)  # функция, которая выполняется в потоке
        worker.signals.result.connect(self.print_output)  # сообщение после завершения выполнения функции
        worker.signals.finish.connect(self.finish_message)  # сообщение после завершения потока
        self.threadpool.start(worker)

    def fn_create_dbf(self):
        pass

    def paths_validation(self):
        """
        :return: проверяет корректность путей. Если путь не найден, то выводится окно с ошибкой
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
            dlg.exec()
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
        self.btn_handler = QPushButton('Загрузить данные из таблицы в файл DBF')
        # self.btn_handler.clicked.connect(self.thread_reading_dbf_file)
        self.btn_handler.clicked.connect(self.fn_read_dbf)
        self.btn_add_new_row = QPushButton('Добавить строку')
        self.btn_add_new_row.clicked.connect(self.add_row_to_table)
        self.btn_del_row = QPushButton('Удалить строку')
        self.btn_del_row.clicked.connect(self.delete_some_row_from_table)
        self.main_layout.addWidget(self.label_path_to_file, 0, 0)
        self.main_layout.addWidget(self.lineedit_path_to_file, 0, 1)
        self.main_layout.addWidget(self.table, 1, 0, 1, 2)
        self.main_layout.addWidget(self.btn_handler, 2, 0, 1, 2)
        self.main_layout.addWidget(self.btn_add_new_row, 3, 0)
        self.main_layout.addWidget(self.btn_del_row, 3, 1)

    def get_path(self):
        """
        :return: получить путь к файлу и записать его в поле
        """
        get_dir = QFileDialog.getOpenFileName(self, caption='Выбрать файл')
        if get_dir:
            get_dir = get_dir[0]
        else:
            get_dir = 'Путь не выбран'
        self.lineedit_path_to_file.setText(get_dir)

    def get_settings(self):
        """
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
        :param event: событие, которое можно принять или переопределить при закрытии
        :return: охранение настроек при закрытии приложения
        """
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
