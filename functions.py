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
                    big_list.append(str(record))
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


# creating dbf
# table = dbf.Table('temp130123.dbf', 'TRADEDATE D; PRICEDATE D; SECURITYID C(12); REGNUMBER C(20); '
#                                     'FACEVALUE N(20,4); WAPRICE N(20,4); MATDATE D; CURRENCY C(3); MARKET C(4)')
# table.open(mode=dbf.READ_WRITE)
# data = ((dbf.Date(2023, 1, 13), dbf.Date(2023, 1, 13), 'RU000A101665', 'RU35014NJG0', 700.0, 97.47, dbf.Date(2024, 1, 14), 'RUB', ''),
#         (dbf.Date(2023, 1, 13), dbf.Date(2023, 1, 13), 'RU000A1014S3', '4B02-01-12414-F-001P', 800.0, 97.97, dbf.Date(2025, 1, 15), 'RUB', ''),
#         (dbf.Date(2023, 1, 13), dbf.Date(2023, 1, 13), 'RU000A101RB4', 'RU34015BEL0', 860.0, 101.47, dbf.Date(2026, 1, 16), 'RUB', ''))
# for i in data:
#     table.append(i)
