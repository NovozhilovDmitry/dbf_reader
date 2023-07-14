import dbfread
import struct
import re

small_dbf_path = 'E:/sh130123.dbf'
large_dbf_path = 'E:/SH061022.DBF'
dbf_dict = {}
# table = dbfread.DBF(small_dbf_path, load=True)
# list_of_fields = []
# for i in table.fields:
#     first_point = str(i).find(',') - 1
#     name = str(i).find('name=') + 6
#     list_of_fields.append(str(i)[name:first_point])


def get_headers_from_dbf(path_to_dbf_file):
    """
    возможно нужно будет переделать, потому что на срезах не круто
    :param path_to_dbf_file: путь к DBF файлу
    :return: список с хедерами
    """
    table = dbfread.DBF(path_to_dbf_file, load=True)
    list_of_fields = []
    for i in table.fields:
        first_point = str(i).find(',') - 1
        name = str(i).find('name=') + 6
        list_of_fields.append(str(i)[name:first_point])
    return list_of_fields


def get_len_of_table(path_to_dbf_file):
    """
    закончено
    :param path_to_dbf_file: путь к DBF файлу
    :return: количество записей в файле
    """
    table = dbfread.DBF(path_to_dbf_file, load=True)
    return len(table)


def get_value_from_dbf(path_to_dbf_file, header_name):
    """
    закончено
    :param path_to_dbf_file: путь к DBF файлу
    :param header_name: имя хедера
    :return: возвращает список по имени хедера
    """
    class Record(object):
        def __init__(self, items):
            for (name, value) in items:
                setattr(self, name, value)

    for record in dbfread.DBF(path_to_dbf_file, recfactory=Record, lowernames=True):
        print(eval('record.' + header_name))
        # получаем все значения по хедеру
        # записываем в отдельные списки?


def lower_list(some_list):
    """
    закончено
    :param some_list: список, который будет преобразовываться для функции в нижний регистр
    :return: новый список со значениями в нижнем регистре
    """
    new_list = []
    for i in some_list:
        new_list.append(str(i).lower())
    return new_list


# get_value_from_dbf(small_dbf_path, 'securityid')
headers_list = lower_list(get_headers_from_dbf(small_dbf_path))
for i in headers_list:
    get_value_from_dbf(small_dbf_path, i)
