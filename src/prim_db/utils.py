import json

from .model import DataBaseMetadata
from .settings import DATA_DIR, METADATA_FILE_PATH


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
        json.dump(data_dict, f, ensure_ascii=False, indent=2)


def load_table_data(table_name):
    """Загружает данные таблицы из JSON-файла."""
    try:
        with open(f"{DATA_DIR}/{table_name}.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_table_data(table_name, data):
    """Сохраняет данные таблицы в JSON-файл."""
    with open(f"{DATA_DIR}/{table_name}.json", mode="w+", encoding="utf-8") as f:
        return json.dump(data, f, ensure_ascii=False, indent=2)
