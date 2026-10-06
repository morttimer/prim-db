from typing import Iterable


class DataBaseMetadata:
    def __init__(self, tables):
        """Создает метаданные базы данных из списка таблиц."""
        if not isinstance(tables, Iterable) or isinstance(tables, str):
            raise TypeError("Описание таблиц должно быть итерируемой коллекцией")

        self._tables = []

        for table in tables:
            if not isinstance(table, TableMetadata):
                raise TypeError(
                    "Описание таблицы должно быть объектом класса TableMetadata"
                )

            if self.find_table(table.name) is not None:
                raise ValueError(
                    "Таблиц с одинаковым именем не должно существовать "
                    "в пределах одной базы данных"
                )

            self._tables.append(table)

    @property
    def tables(self):
        return tuple(self._tables)

    @classmethod
    def from_dict(cls, data):
        """Создает метаданные базы данных из словаря."""
        return cls([TableMetadata.from_dict(table) for table in data["tables"]])

    def to_dict(self):
        """Преобразует метаданные базы данных в словарь."""
        return {"tables": [t.to_dict() for t in self._tables]}

    def drop_table_by_name(self, table_name):
        """Удаляет таблицу по имени."""
        target_table = self.find_table(table_name)

        if target_table is None:
            raise ValueError(f"Таблица с именем {table_name} не найдена")

        self._tables.remove(target_table)

    def create_table(self, table_name, column_desc):
        """Создает таблицу с заданными столбцами."""
        if self.find_table(table_name) is not None:
            raise ValueError(f"Таблица с именем {table_name} уже существует")

        updated_col_desc = []
        for col in column_desc:
            splitted_col = col.split(":")
            updated_col_desc.append({"name": splitted_col[0], "type": splitted_col[1]})

        id_column = [col for col in updated_col_desc if col["name"] == "ID"]
        if not id_column:
            updated_col_desc = [{"name": "ID", "type": "int"}, *updated_col_desc]

        self._tables.append(
            TableMetadata(table_name, ColumnsMetadata.from_dict(updated_col_desc))
        )

    def find_table(self, table_name):
        """Возвращает таблицу с заданным именем."""
        return next((t for t in self._tables if t.name == table_name), None)

    def list_tables(self):
        """Возвращает текстовое описание всех таблиц."""
        all_tables_info = []
        for t in self._tables:
            all_tables_info.append(f"{t.name}")
        return all_tables_info


class TableMetadata:
    def __init__(self, name, columns):
        """Создает метаданные таблицы."""
        if not isinstance(name, str):
            raise TypeError("Название таблицы должно быть строкой")

        if not isinstance(columns, ColumnsMetadata):
            raise TypeError(
                "Описание столбцов таблицы должно быть объектом класса ColumnsMetadata"
            )

        self._name = name
        self._columns = columns

    @property
    def name(self):
        return self._name

    @property
    def columns(self):
        return self._columns

    @classmethod
    def from_dict(cls, data):
        """Создает метаданные таблицы из словаря."""
        return cls(data["name"], ColumnsMetadata.from_dict(data["columns"]))

    def to_dict(self):
        """Преобразует метаданные таблицы в словарь."""
        return {"name": self._name, "columns": self._columns.to_dict()}

    def convert_row(self, values):
        """Преобразует значения строки к типам столбцов."""
        data_columns = self._columns.columns[1:]
        if len(values) != len(data_columns):
            raise ValueError(
                f"Ожидается значений: {len(data_columns)}, передано: {len(values)}"
            )

        return tuple(col.convert(v) for col, v in zip(data_columns, values))

    def convert_value(self, col_name, raw_value):
        """Преобразует значение к типу столбца с заданным именем."""
        column = self._columns.find_by_name(col_name)
        if column is None:
            raise ValueError(f"Столбца с именем {col_name} не существует")

        return column.convert(raw_value)


class ColumnMetadata:
    def __init__(self, col_name, col_type):
        """Создает метаданные столбца."""
        if not isinstance(col_name, str):
            raise TypeError("Название столбца должно быть строкой")

        if col_type not in ["int", "str", "bool"]:
            raise ValueError("Тип столбца таблицы должен быть один из: int, str, bool")

        self._name = col_name
        self._type = col_type

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @classmethod
    def from_dict(cls, data):
        """Создает метаданные столбца из словаря."""
        return cls(data["name"], data["type"])

    def to_dict(self):
        """Преобразует метаданные столбца в словарь."""
        return {"name": self._name, "type": self._type}

    def convert(self, raw_value):
        """Преобразует значение из строки ввода к типу столбца."""
        unquoted = ColumnMetadata._unquote(raw_value)

        if self._type == "str" and unquoted is not None:
            return unquoted

        if self._type == "int" and unquoted is None:
            try:
                return int(raw_value)
            except ValueError:
                pass

        if self._type == "bool" and raw_value.lower() in ("true", "false"):
            return raw_value.lower() == "true"

        raise ValueError(f"Некорректное значение: {raw_value}")

    @staticmethod
    def _unquote(raw_value):
        """Возвращает значение без кавычек или None, если кавычек нет."""
        if len(raw_value) < 2 or raw_value[0] not in ('"', "'"):
            return None

        if raw_value[-1] != raw_value[0]:
            return None

        return raw_value[1:-1]


class ColumnsMetadata:
    def __init__(self, columns):
        """Создает набор столбцов таблицы."""
        if not isinstance(columns, Iterable) or isinstance(columns, str):
            raise TypeError(
                "Описание столбцов таблицы должно быть итерируемой коллекцией"
            )

        self._columns = []
        for column in columns:
            if not isinstance(column, ColumnMetadata):
                raise TypeError(
                    "Описание столбца таблицы должно быть "
                    "объектом класса ColumnMetadata"
                )

            same_name_columns = [
                col for col in self._columns if col.name == column.name
            ]
            if same_name_columns:
                raise ValueError(
                    "Столбцов с одинаковым именем не должно существовать "
                    "в пределах одной таблицы"
                )

            self._columns.append(column)

    def __len__(self):
        """Возвращает количество столбцов."""
        return len(self._columns)

    @property
    def columns(self):
        return tuple(self._columns)

    @classmethod
    def from_dict(cls, data):
        """Создает набор столбцов из списка словарей."""
        return cls([ColumnMetadata.from_dict(column) for column in data])

    def to_dict(self):
        """Преобразует набор столбцов в список словарей."""
        return [c.to_dict() for c in self._columns]

    def find_by_name(self, col_name):
        """Возвращает столбец с заданным именем."""
        return next((c for c in self._columns if c.name == col_name), None)
