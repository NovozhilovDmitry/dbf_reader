from my_logging import logger
import traceback
import pathlib
from datetime import datetime
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QThreadPool, QSettings
from PyQt6.QtWidgets import (QMainWindow, QWidget, QGridLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox,
                             QTableWidget)
from functions import write_data_to_json_file, get_result_from_json
from classes import Worker


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
JSONFILENAME = 'headers.json'


class CreatingWindow(QMainWindow):
    def __init__(self):
        super(CreatingWindow, self).__init__()
        self.setWindowTitle('Создание записей')
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.btn_icon = QPixmap("others/folder.png")
        self.layout = QWidget()
        self.main_layout = QGridLayout()
        self.settings = QSettings('config.ini', QSettings.Format.IniFormat)
        self.threadpool = QThreadPool()
        self.header_layout()
        self.layout.setLayout(self.main_layout)
        self.setCentralWidget(self.layout)
        self.get_settings()
        self.data_from_json = self.check_json_file()

    def print_output(self, s):
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
        dlg.setWindowTitle('DBF reader')
        dlg.setText(f'Функция выполнена за {self.count_time}')
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.exec()

    def add_row_to_table(self):
        """
        :return: добавить новую строку в таблицу
        """
        last_row = self.table.rowCount()
        self.table.insertRow(last_row)

    def delete_row_from_table(self):
        """
        :return: удаление выбранной пользователем строки в таблице
        """
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.question(self, 'Сообщение', "Выберите строку, которую вы хотите удалить",
                                 QMessageBox.StandardButton.Ok)
        else:
            msg = QMessageBox.question(self, 'Подтверждение удаления строки',
                                       f"Вы действительно хотите удалить строку <b style='color: red;'>{row + 1}</b>?",
                                       QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                return
            elif msg == QMessageBox.StandardButton.Ok:
                self.table.removeRow(row)
            else:
                logger.warning('Неизвестная ошибка. Не нажаты кнопки Ok/Cancel при подтвеждении удаления строки')

    def add_column_to_table(self):
        """
        :return: добавить новый столбец в таблицу
        """
        last_column = self.table.columnCount()
        self.table.insertColumn(last_column)

    def delete_column_from_table(self):
        """
        :return: удаление выбранного пользователем столбца в таблице
        """
        column = self.table.currentColumn()
        if column == -1:
            QMessageBox.question(self, 'Сообщение', "Выберите столбец, который вы хотите удалить",
                                 QMessageBox.StandardButton.Ok)
        else:
            msg = QMessageBox.question(self, 'Подтверждение удаления',
                                       f"Вы действительно хотите удалить столбец <b style='color: red;'>{column + 1}</b>?",
                                       QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                return
            elif msg == QMessageBox.StandardButton.Ok:
                self.table.removeColumn(column)
            else:
                logger.warning('Неизвестная ошибка. Не нажаты кнопки Ok/Cancel при подтвеждении удаления')

    def check_json_file(self):
        """
        :return: проверяет json-файл. Создает файл, если его нет. Если он есть, то проверяет что в нем
        """
        headers_list = {
            'TRADEDATE': 'D',
            'PRICEDATE': 'D',
            'SECURITYID': 'C(12)',
            'REGNUMBER': 'C(20)',
            'FACEVALUE': 'N(20,4)',
            'WAPRICE': 'N(20,4)',
            'MATDATE': 'D',
            'CURRENCY': 'C(3)',
            'MARKET': 'C(4)'
        }
        if pathlib.Path.exists(pathlib.Path.cwd().joinpath(JSONFILENAME)):
            headers_with_data_types = get_result_from_json(pathlib.Path.cwd().joinpath(JSONFILENAME))
        else:
            write_data_to_json_file(pathlib.Path.cwd().joinpath(JSONFILENAME), headers_list)
            headers_with_data_types = get_result_from_json(pathlib.Path.cwd().joinpath(JSONFILENAME))
        return headers_with_data_types

    def thread_creating_dbf_file(self):
        """
        :return: выполнение переданной функции в отдельном потоке
        """
        path = self.lineedit_create_dbf.text()
        if pathlib.Path(path).exists():
            logger.info('Начато создание DBF файла')
            worker = Worker(self.fn_create_dbf)
            worker.signals.result.connect(self.print_output)
            worker.signals.finish.connect(self.finish_message)
            self.threadpool.start(worker)
        else:
            dlg = QMessageBox()
            dlg.setWindowTitle('Ошибка валидации путей')
            dlg.setText('Проверьте корректность введенного пути')
            dlg.exec()
            logger.error('Ошибка валидации путей')

    def fn_create_dbf(self, progress_callback):
        start = datetime.now()
        path = self.lineedit_create_dbf.text()
        list_of_headers = self.data_from_json
        print(type(list_of_headers))
        count_headers = len(list_of_headers)
        self.table.clear()
        self.table.setRowCount(1)
        self.table.setColumnCount(count_headers)
        self.table.setHorizontalHeaderLabels(list_of_headers)
        # for i, (header_value, header_type) in enumerate(list_of_headers.items()):  # перебор записей в словаре
        #     print(header_value + ' ', header_type)  # хедер + тип данных
        #     self.table.setItem(0, i, QTableWidgetItem(header_value + ' ' + header_type))
        end = datetime.now()
        self.count_time = end - start
        return f'функция {traceback.extract_stack()[-1][2]} выполнена'

    def get_directory_for_create_dbf(self):
        """
        :return: получить путь к файлу и записать его в поле
        """
        get_dir = QFileDialog.getExistingDirectory(self, caption='Выбрать каталог')
        if get_dir:
            get_dir = get_dir
        else:
            get_dir = 'Путь не выбран'
        self.lineedit_create_dbf.setText(get_dir)

    def header_layout(self):
        """
        :return: добавление виджетов в верхнюю часть интерфейса на главном окне
        """
        self.lineedit_create_dbf = QLineEdit()
        self.lineedit_create_dbf.setPlaceholderText('Укажите путь к каталогу, где будет создан DBF файл')
        self.lineedit_create_dbf.setToolTip('Путь к каталогу, где будет создан DBF файл')
        self.btn_set_path_directory = self.lineedit_create_dbf.addAction(QIcon(self.btn_icon),
                                                                         QLineEdit.ActionPosition.TrailingPosition)
        self.btn_set_path_directory.triggered.connect(self.get_directory_for_create_dbf)
        self.table = QTableWidget()
        self.btn_add_new_row = QPushButton('Добавить строку')
        self.btn_add_new_row.clicked.connect(self.add_row_to_table)
        self.btn_add_new_column = QPushButton('Добавить столбец')
        self.btn_add_new_column.clicked.connect(self.add_column_to_table)
        self.btn_del_row = QPushButton('Удалить строку')
        self.btn_del_row.clicked.connect(self.delete_row_from_table)
        self.btn_del_column = QPushButton('Удалить столбец')
        self.btn_del_column.clicked.connect(self.delete_column_from_table)
        self.btn_creating_handler = QPushButton('Загрузить данные из таблицы в DBF файл')
        self.btn_creating_handler.clicked.connect(self.thread_creating_dbf_file)
        self.main_layout.addWidget(self.lineedit_create_dbf, 0, 0, 1, 2)
        self.main_layout.addWidget(self.btn_add_new_row, 1, 0)
        self.main_layout.addWidget(self.btn_add_new_column, 2, 0)
        self.main_layout.addWidget(self.btn_del_row, 1, 1)
        self.main_layout.addWidget(self.btn_del_column, 2, 1)
        self.main_layout.addWidget(self.table, 3, 0, 1, 2)
        self.main_layout.addWidget(self.btn_creating_handler, 4, 0, 1, 2)

    def get_settings(self):
        """
        :return: заполнение полей из настроек
        """
        try:
            width = int(self.settings.value('GUI/c-width'))
            height = int(self.settings.value('GUI/c-height'))
            x = int(self.settings.value('GUI/c-x'))
            y = int(self.settings.value('GUI/c-y'))
            self.setGeometry(x, y, width, height)
            logger.info('Настройки размеров окна загружены.')
        except:
            logger.warning('Настройки размеров окна НЕ загружены. Установлены размеры по умолчанию')
        self.lineedit_create_dbf.setText(self.settings.value('path/create_dir_path'))
        logger.info('Файл с пользовательскими настройками проинициализирован')

    def closeEvent(self, event):
        """
        :param event: событие, которое можно принять или переопределить при закрытии
        :return: охранение настроек при закрытии приложения
        """
        self.settings.beginGroup('GUI')
        self.settings.setValue('c-width', self.geometry().width())
        self.settings.setValue('c-height', self.geometry().height())
        self.settings.setValue('c-x', self.geometry().x())
        self.settings.setValue('c-y', self.geometry().y())
        self.settings.endGroup()
        self.settings.beginGroup('path')
        self.settings.setValue('create_dir_path', self.lineedit_create_dbf.text())
        self.settings.endGroup()
        logger.info(f'Пользовательские настройки сохранены. Файл {__file__} закрыт')


if __name__ == '__main__':
    pass
