import dbf


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
        return table.field_count


def get_value_from_dbf(path_to_dbf_file, header_name):
    """
    исправить на другую библиотеку
    :param path_to_dbf_file: путь к DBF файлу
    :param header_name: имя хедера
    :return: возвращает список по имени хедера
    """
    values = []

    class Record(object):
        def __init__(self, items):
            for (name, value) in items:
                setattr(self, name, value)

    for record in dbfread.DBF(path_to_dbf_file, recfactory=Record, lowernames=True):
        values.append(str(eval('record.' + header_name)))
    return values


def lower_list(some_list):
    """
    :param some_list: значения из списка, которые будут преобразовываться в нижний регистр
    :return: новый список со значениями в нижнем регистре
    """
    new_list = []
    for i in some_list:
        new_list.append(str(i).lower())
    return new_list




# table = dbf.Table('sh130123.dbf')
# table = dbf.Table('temp130123.dbf', 'TRADEDATE D; PRICEDATE D; SECURITYID C(12); REGNUMBER C(20); '
#                                     'FACEVALUE N(20,4); WAPRICE N(20,4); MATDATE D; CURRENCY C(3); MARKET C(4)')
# table.open(mode=dbf.READ_WRITE)
# data = ((dbf.Date(2023, 1, 13), dbf.Date(2023, 1, 13), 'RU000A101665', 'RU35014NJG0', 700.0, 97.47, dbf.Date(2024, 1, 14), 'RUB', ''),
#         (dbf.Date(2023, 1, 13), dbf.Date(2023, 1, 13), 'RU000A1014S3', '4B02-01-12414-F-001P', 800.0, 97.97, dbf.Date(2025, 1, 15), 'RUB', ''),
#         (dbf.Date(2023, 1, 13), dbf.Date(2023, 1, 13), 'RU000A101RB4', 'RU34015BEL0', 860.0, 101.47, dbf.Date(2026, 1, 16), 'RUB', ''))
# for i in data:
#     table.append(i)
# print(table)
# print('Имена полей: ', table.field_names)
# print('Количество записей в таблице: ', table.field_count)
#
# for record in table:
#     print('запись: ', record)

# for data in (
#         (dbf.Date(2023, 12, 31),
#          dbf.Date(2024, 12, 31),
#          'RU000A123456',
#          'RU350987654',
#          800.0,
#          197.47,
#          dbf.Date(2025, 12, 31),
#          'RUB',
#          '    '),
#         ):
#     table.append(data)

# table.close()
