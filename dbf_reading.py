from my_logging import logger
import pathlib
import re
import datetime as DT
from datetime import datetime
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QThreadPool, QSettings
from PyQt6.QtWidgets import (QMainWindow, QWidget, QGridLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox,
                             QTableWidget, QTableWidgetItem)
from functions import (get_len_of_table, get_headers_from_dbf, get_value_from_dbf, func_chunks_generators, header_dbf,
                       save_to_dbf, make_copy_file)
from classes import Worker


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600


class ReadingWindow(QMainWindow):
    def __init__(self):
        super(ReadingWindow, self).__init__()
        self.setWindowTitle('Чтение записей')
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

    def print_output(self, s):
        """
        :param s: сообщение
        :return: когда функция завершается, выводится в лог сообщение из функции, которое указано в return
        """
        logger.info(s)

    def information_window(self):
        """
        :return: после завершения функции чтения файла выводится окно с сообщением и данными о затраченном времени
        """
        dlg = QMessageBox()
        dlg.setWindowTitle('DBF reader')
        text = f"""Будьте внимательны при заполнении полей с датами.
Функция выполнена за {self.count_time}"""
        dlg.setText(text)
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.exec()

    def finish_message(self):
        """
        :return: после завершения функции в отдельном потоке выводится окно с данными о затраченном времени
        """
        dlg = QMessageBox()
        dlg.setWindowTitle('DBF reader')
        dlg.setText(f'Функция выполнена за {self.count_time}')
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.exec()

    def thread_reading_dbf_file(self):
        """
        :return: выполнение переданной функции в отдельном потоке
        """
        path = self.lineedit_open_dbf.text()
        if pathlib.Path(path).exists():
            logger.info('Начато чтение DBF файла')
            worker = Worker(self.fn_read_dbf)
            worker.signals.result.connect(self.print_output)
            worker.signals.finish.connect(self.information_window)
            self.threadpool.start(worker)
        else:
            dlg = QMessageBox()
            dlg.setWindowTitle('Ошибка валидации путей')
            dlg.setText('Проверьте корректность введенного пути')
            dlg.exec()
            logger.error('Ошибка валидации путей')

    def fn_read_dbf(self, progress_callback):
        """
        :param progress_callback: результат выполнения функции в потоке
        :return: выполненная функция чтения DBF файла
        """
        start = datetime.now()
        path = self.lineedit_open_dbf.text()
        list_of_headers = get_headers_from_dbf(path)
        count_rows = get_len_of_table(path)
        self.count_headers = len(list_of_headers)
        self.table.clear()
        self.table.setRowCount(count_rows)
        self.table.setColumnCount(self.count_headers)
        self.table.setHorizontalHeaderLabels(list_of_headers)
        records = get_value_from_dbf(path)
        new_list = func_chunks_generators(records, self.count_headers)
        for row, list_records in enumerate(new_list):
            for column in range(0, self.count_headers):
                self.table.setItem(row, column, QTableWidgetItem(list_records[column]))
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        end = datetime.now()
        self.count_time = end - start
        logger.info(f'В файле присутствуют следующие поля: {header_dbf(path)}')
        self.btn_save_dbf.setEnabled(True)
        return f'Чтение dbf выполнено успешно'

    def thread_creating_dbf_file(self):
        """
        :return: выполнение переданной функции в отдельном потоке
        """
        logger.info('Начато сохранение DBF файла')
        worker = Worker(self.fn_save_dbf)
        worker.signals.result.connect(self.print_output)
        worker.signals.finish.connect(self.finish_message)
        self.threadpool.start(worker)

    def fn_save_dbf(self, progress_callback):
        """
        :param progress_callback: результат выполнения функции в потоке
        :return: выполненная функция сохранения записей из таблицы в DBF файл
        """
        start = datetime.now()
        pattern = r'\d{4}[-/.]\d{2}[-/.]\d{2}'
        path = self.lineedit_open_dbf.text()
        temp_list = []
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item is None:
                    continue
                if re.search(pattern, item.text()):
                    temp_list.append(DT.datetime.strptime(item.text(), '%Y-%m-%d').date())
                else:
                    temp_list.append(item.text())
        data = func_chunks_generators(temp_list, self.count_headers)
        make_copy_file(path)
        save_to_dbf(path, header_dbf(path), data)
        end = datetime.now()
        self.count_time = end - start
        return f'Сохранение dbf выполнено успешно'

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
        if row == 0:
            QMessageBox.warning(self, 'ВНИМАНИЕ!', 'ПЕРВУЮ СТРОКУ УДАЛЯТЬ НЕЛЬЗЯ')
            logger.warning('Пользователь попытался удалить первую строку')
        elif row == -1:
            QMessageBox.question(self, 'Сообщение', "Выберите строку, которую вы хотите удалить",
                                 QMessageBox.StandardButton.Ok)
        else:
            msg = QMessageBox.question(self, 'Подтверждение удаления',
                                       f"Вы действительно хотите удалить строку <b style='color: red;'>{row + 1}</b>?",
                                       QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                return
            elif msg == QMessageBox.StandardButton.Ok:
                self.table.removeRow(row)
            else:
                logger.warning('Неизвестная ошибка. Не нажаты кнопки Ok/Cancel при подтвеждении удаления строки')

    def header_layout(self):
        """
        :return: добавление виджетов в верхнюю часть интерфейса на главном окне
        """
        self.lineedit_open_dbf = QLineEdit()
        self.lineedit_open_dbf.setPlaceholderText('Укажите путь к файлу')
        self.lineedit_open_dbf.setToolTip('Путь к DBF файлу для открытия')
        self.btn_set_path = self.lineedit_open_dbf.addAction(QIcon(self.btn_icon),
                                                             QLineEdit.ActionPosition.TrailingPosition)
        self.btn_set_path.triggered.connect(self.get_path_for_open_dbf)
        self.table = QTableWidget()
        self.btn_add_new_row = QPushButton('Добавить строку')
        self.btn_add_new_row.clicked.connect(self.add_row_to_table)
        self.btn_del_row = QPushButton('Удалить строку')
        self.btn_del_row.clicked.connect(self.delete_row_from_table)
        self.btn_reading_handler = QPushButton('Загрузить данные из DBF файла в таблицу')
        self.btn_reading_handler.clicked.connect(self.thread_reading_dbf_file)
        self.btn_save_dbf = QPushButton('Сохранить файл')
        self.btn_save_dbf.clicked.connect(self.thread_creating_dbf_file)
        self.btn_save_dbf.setEnabled(False)
        self.main_layout.addWidget(self.lineedit_open_dbf, 0, 0, 1, 2)
        self.main_layout.addWidget(self.btn_reading_handler, 1, 0)
        self.main_layout.addWidget(self.btn_save_dbf, 1, 1)
        self.main_layout.addWidget(self.table, 2, 0, 1, 2)
        self.main_layout.addWidget(self.btn_add_new_row, 3, 0)
        self.main_layout.addWidget(self.btn_del_row, 3, 1)

    def get_path_for_open_dbf(self):
        """
        :return: получить путь к файлу и записать его в поле
        """
        get_dir = QFileDialog.getOpenFileName(self, caption='Выбрать файл')
        if get_dir:
            get_dir = get_dir[0]
        else:
            get_dir = 'Путь не выбран'
        self.lineedit_open_dbf.setText(get_dir)

    def get_settings(self):
        """
        :return: заполнение полей из настроек
        """
        try:
            width = int(self.settings.value('GUI/r-width'))
            height = int(self.settings.value('GUI/r-height'))
            x = int(self.settings.value('GUI/r-x'))
            y = int(self.settings.value('GUI/r-y'))
            self.setGeometry(x, y, width, height)
            logger.info('Настройки размеров окна загружены.')
        except:
            logger.warning('Настройки размеров окна НЕ загружены. Установлены размеры по умолчанию')
        self.lineedit_open_dbf.setText(self.settings.value('path/open_dir_path'))
        logger.info('Файл с пользовательскими настройками проинициализирован')

    def closeEvent(self, event):
        """
        :param event: событие, которое можно принять или переопределить при закрытии
        :return: охранение настроек при закрытии приложения
        """
        self.settings.beginGroup('GUI')
        self.settings.setValue('r-width', self.geometry().width())
        self.settings.setValue('r-height', self.geometry().height())
        self.settings.setValue('r-x', self.geometry().x())
        self.settings.setValue('r-y', self.geometry().y())
        self.settings.endGroup()
        self.settings.beginGroup('path')
        self.settings.setValue('open_dir_path', self.lineedit_open_dbf.text())
        self.settings.endGroup()
        logger.info(f'Пользовательские настройки сохранены. Файл {__file__} закрыт')


if __name__ == '__main__':
    pass
