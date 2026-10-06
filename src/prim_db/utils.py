import json

from .model import DataBaseMetadata


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла."""
    try:
        with open(filepath, encoding="utf-8") as f:
            metadata = json.load(f)

        return DataBaseMetadata.from_dict(metadata)
    except FileNotFoundError:
        print(f"Файл по пути {filepath} не найден!")

        return DataBaseMetadata([])


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    if not isinstance(data, DataBaseMetadata):
        raise TypeError("Аргумент data должен быть объектом класса DataBaseMetadata")

    data_dict = data.to_dict()
    with open(filepath, mode="w", encoding="utf-8") as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=2)
