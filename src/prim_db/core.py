from .model import DataBaseMetadata


def create_table(metadata, table_name, columns):
    """Создает таблицу в метаданных и возвращает их."""
    _check_metadata(metadata)

    metadata.create_table(table_name, columns)
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных и возвращает их."""
    _check_metadata(metadata)

    metadata.drop_table_by_name(table_name)
    return metadata


def list_tables(metadata):
    """Возвращает описание всех таблиц."""
    _check_metadata(metadata)

    return metadata.list_tables()


def _check_metadata(metadata):
    """Проверяет, что метаданные являются объектом DataBaseMetadata."""
    if not isinstance(metadata, DataBaseMetadata):
        raise TypeError("Метаданные должны быть объектом класса DataBaseMetadata")
