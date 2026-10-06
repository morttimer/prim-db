from .decorators import confirm_action, log_time
from .model import DataBaseMetadata


def create_table(metadata, table_name, columns):
    """Создает таблицу в метаданных и возвращает их."""
    _check_metadata(metadata)

    metadata.create_table(table_name, columns)
    return metadata


@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных и возвращает их."""
    _check_metadata(metadata)

    metadata.drop_table_by_name(table_name)
    return metadata


def list_tables(metadata):
    """Возвращает описание всех таблиц."""
    _check_metadata(metadata)

    print(_create_tables_info(metadata.list_tables()))


def info_table(metadata, table_data, table_name):
    """Выводит информацию о таблице."""
    target_table = _get_table(metadata, table_name)

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {_create_columns_info(target_table.columns.columns)}")
    print(f"Количество записей: {len(table_data) if table_data else 0}")


@log_time
def insert(metadata, table_name, table_data, values):
    """Добавляет запись в данные таблицы и возвращает их."""
    target_table = _get_table(metadata, table_name)

    converted_values = target_table.convert_row(values)
    updated_values = _add_id_col(table_data, converted_values)

    table_data.append(_create_table_row(target_table.columns.columns, updated_values))

    return table_data


@confirm_action("удаление данных из таблицы")
def delete(metadata, table_name, table_data, where):
    """Возвращает данные таблицы без записей, подходящих под условие."""
    target_table = _get_table(metadata, table_name)

    col_name, value = _convert_clause(target_table, where)

    return [row for row in table_data if row[col_name] != value]


def update(metadata, table_name, table_data, where_clause, set_clause):
    """Обновляет записи, подходящие под условие, и возвращает данные и их количество."""
    target_table = _get_table(metadata, table_name)

    col_name_where, where_value = _convert_clause(target_table, where_clause)
    col_name_set, set_value = _convert_clause(target_table, set_clause)

    modified = 0
    for row in table_data:
        if row[col_name_where] == where_value:
            row[col_name_set] = set_value
            modified += 1

    return table_data, modified


@log_time
def select(metadata, table_name, table_data, where_clause=None):
    """Возвращает записи таблицы, подходящие под условие."""
    target_table = _get_table(metadata, table_name)

    if not where_clause:
        return table_data

    col_name, value = _convert_clause(target_table, where_clause)

    return [row for row in table_data if row[col_name] == value]


def _check_metadata(metadata):
    """Проверяет, что метаданные являются объектом DataBaseMetadata."""
    if not isinstance(metadata, DataBaseMetadata):
        raise TypeError("Метаданные должны быть объектом класса DataBaseMetadata")


def _get_table(metadata, table_name):
    """Возвращает метаданные существующей таблицы."""
    _check_metadata(metadata)

    target_table = metadata.find_table(table_name)
    if target_table is None:
        raise ValueError(f"Таблицы с именем {table_name} не существует")

    return target_table


def _convert_clause(target_table, clause):
    """Возвращает имя столбца и значение условия, приведенное к типу столбца."""
    col_name, raw_value = clause

    return col_name, target_table.convert_value(col_name, raw_value)


def _add_id_col(table_data, values):
    """Добавляет следующий ID в начало значений записи."""
    if not table_data:
        next_id = 1
    else:
        next_id = max([t["ID"] for t in table_data]) + 1

    return (next_id,) + values


def _create_table_row(table_columns, updated_values):
    """Создает запись таблицы из значений столбцов."""
    result_row = dict()
    for metadata_column, value_to_add in zip(table_columns, updated_values):
        result_row[metadata_column.name] = value_to_add

    return result_row


def _create_columns_info(columns):
    """Возвращает описание столбцов в виде строки."""
    col_info = ""
    for col in columns:
        col_info += f"{col.name}:{col.type}, "
    return col_info[:-2]


def _create_tables_info(tables):
    """Возвращает список таблиц в виде строки."""
    table_info = ""
    for t in tables:
        table_info += f"{t}, "
    return table_info[:-2]
