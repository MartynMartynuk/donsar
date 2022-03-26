from docx import Document
from donsar_system.settings import MEDIA_ROOT


def open_file(file_name):
    """
    Открывает фойл и создает класс Document на его основе
    :param file_name: имя название открываемого файла
    :return: объект класса Document
    """
    return Document(MEDIA_ROOT + '/' + file_name)


def handler(document: Document, table_number: int, row_start: int, row_end: int,
            column_start: int, column_end: int, null_number: int = 0, column_mode=False):
    """
    Функция-обработчик таблиц Альбома НФХ
    :param document: объект Document
    :param table_number: номер обрабатываемой таблицы в документе
    :param row_start: номер строки, с которой начинаем считывать значения
    :param row_end: номер строки, на которой заканчиваем считывать значения
    :param column_start: номер колонки, с которой начинаем считывать значения
    :param column_end: номер колонки, на которой заканчиваем считывать значения
    :param null_number: номер строки (столбца) со значениями полей
    :param column_mode: реверсивный мод
    :return: словарь строка-список_значений
    """
    result = {}
    table = document.tables[table_number]
    if column_mode:
        for i in range(column_start, column_end):
            column = []
            column_key = table.rows[null_number].cells[i].text
            for j in range(row_start, row_end):
                column.append(table.rows[j].cells[i].text)
            result[column_key] = column
    else:
        for i in range(row_start, row_end):
            row = []
            row_key = table.rows[i].cells[null_number].text
            for j in range(column_start, column_end):
                row.append(table.rows[i].cells[j].text)
            result[row_key] = row
    return result


if __name__ == '__main__':
    print(handler(open_file('Album.docx'), 1, 1, 11, 1, 5))
    print(handler(open_file('Album.docx'), 2, 1, 11, 1, 5))
    print(handler(open_file('Album.docx'), 3, 1, 11, 1, 5))
    print(handler(open_file('Album.docx'), 4, 1, 11, 1, 5))
    print(handler(open_file('Album.docx'), 5, 1, 11, 1, 5))
    print(handler(open_file('Album.docx'), 6, 1, 11, 1, 5))
    print(handler(open_file('Album.docx'), 7, 1, 11, 1, 5))
    # print(handler(open_file('Album.docx'), 0, 2, 28, 1, 10, 1, True))
