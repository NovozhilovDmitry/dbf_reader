import dbf
import json
import re


def write_data_to_json_file(path_to_file, data):
    """
    :param path_to_file: путь, где будет создан файл
    :param data: данные, которые будут записаны в файл
    :return: записывает в файл
    """
    with open(path_to_file, 'w') as json_file:
        json.dump(data, json_file)


def get_result_from_json(path_to_file):
    """
    :param path_to_file: путь к json файлу
    :return: структуру из json файла
    """
    with open(path_to_file, 'r') as json_file:
        return json.load(json_file)


def get_headers_from_dbf(path_to_dbf_file):
    """
    :param path_to_dbf_file: путь к DBF файлу
    :return: список с хедерами
    """
    header_names = []
    with dbf.Table(path_to_dbf_file) as table:
        for i in table.field_names:
            header_names.append(i)
    return header_names


def get_len_of_table(path_to_dbf_file):
    """
    :param path_to_dbf_file: путь к DBF файлу
    :return: количество записей в файле
    """
    with dbf.Table(path_to_dbf_file) as table:
        return len(table)


def get_value_from_dbf(path_to_dbf_file):
    """
    :param path_to_dbf_file: путь к DBF файлу
    :return: возвращает список записей
    """
    big_list = []
    with dbf.Table(path_to_dbf_file) as table:
        try:
            for records in table:
                for record in records:
                    big_list.append(str(record).strip())
        except:
            pass
    return big_list


def func_chunks_generators(lst, n):
    """
    :param lst: список, который нужно разделить
    :param n: количество записей в каждом списке
    :return: новый список со списками
    """
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


def header_dbf(path_to_dbf_file):
    """
    :param path_to_dbf_file: путь к DBF файлу
    :return: список хедеров с типами данных из DBF файла
    """
    table = dbf.Table(path_to_dbf_file)
    data = str(table)
    start = data.find('--Fields--') + 10
    temp_list = [re.sub(r'\s{2,}', '', i) for i in data[start:].split('b') if re.search(r'[A-Z]', i)]
    header_with_type = []
    for i in temp_list:
        symbol = i.find("'", 1)
        header_with_type.append(i[1:symbol])
    return header_with_type


def save_to_dbf(filename, headers_with_types, data):
    """
    :param filename: имя файла с расширением (можно указать в том числе путь, где будет создан файл)
    :param headers_with_types: список полей с их типами данных
    :param data: кортеж с кортежами записей
    :return: файл DBF
    """
    table = dbf.Table(filename, headers_with_types)
    table.open(mode=dbf.READ_WRITE)
    for i in data:
        table.append(i)


if __name__ == '__main__':
    pass
