import json
from pathlib import Path

from .constants import DATA_DIR, JSON_INDENT, METADATA_FILE_PATH, TABLE_FILE_EXTENSION
from .model import DataBaseMetadata


def init_metadata():
    """Создает пустой файл метаданных, если он отсутствует."""
    if Path(METADATA_FILE_PATH).exists():
        return

    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    save_metadata(DataBaseMetadata([]))


def load_metadata():
    """Загружает метаданные из JSON-файла."""
    try:
        with open(METADATA_FILE_PATH, encoding="utf-8") as f:
            metadata = json.load(f)

        return DataBaseMetadata.from_dict(metadata)
    except FileNotFoundError:
        print(f"Файл по пути {METADATA_FILE_PATH} не найден!")

        return DataBaseMetadata([])


def save_metadata(data):
    """Сохраняет метаданные в JSON-файл."""
    if not isinstance(data, DataBaseMetadata):
        raise TypeError("Аргумент data должен быть объектом класса DataBaseMetadata")

    data_dict = data.to_dict()
    with open(METADATA_FILE_PATH, mode="w+", encoding="utf-8") as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=JSON_INDENT)


def load_table_data(table_name):
    """Загружает данные таблицы из JSON-файла."""
    try:
        with open(_table_data_path(table_name), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_table_data(table_name, data):
    """Сохраняет данные таблицы в JSON-файл."""
    with open(_table_data_path(table_name), mode="w+", encoding="utf-8") as f:
        return json.dump(data, f, ensure_ascii=False, indent=JSON_INDENT)


def delete_table_data(table_name):
    """Удаляет файл данных таблицы."""
    Path(_table_data_path(table_name)).unlink(missing_ok=True)


def _table_data_path(table_name):
    """Возвращает путь к файлу данных таблицы."""
    return f"{DATA_DIR}/{table_name}{TABLE_FILE_EXTENSION}"
