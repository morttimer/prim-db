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

            same_name_tables = self._find_table(table.name)
            if same_name_tables:
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
        target_table = self._find_table(table_name)

        if not target_table:
            raise ValueError(f"Таблица с именем {table_name} не найдена")

        self._tables = [t for t in self._tables if t not in target_table]

    def create_table(self, table_name, column_desc):
        """Создает таблицу с заданными столбцами."""
        if self._find_table(table_name):
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

    def _find_table(self, table_name):
        """Возвращает таблицы с заданным именем."""
        return [t for t in self._tables if t.name == table_name]

    def list_tables(self):
        """Возвращает текстовое описание всех таблиц."""
        all_tables_info = []
        all_tables_info.append("Все таблицы базы данных\n")
        all_tables_info.append("-" * 4)
        all_tables_info.append("\n")
        for t in self._tables:
            col_list = t.columns.columns
            all_tables_info.append(f"Название таблицы: {t.name}\n")
            all_tables_info.append(
                f"Столбцы таблицы: {[(col.name, col.type) for col in col_list]}\n"
            )
            all_tables_info.append("-" * 4)
            all_tables_info.append("\n")
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
