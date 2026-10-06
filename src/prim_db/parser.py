import shlex
from abc import ABC, abstractmethod
from typing import Self

from prettytable import PrettyTable

from .core import (
    create_table,
    delete,
    drop_table,
    info_table,
    insert,
    list_tables,
    select,
    update,
)
from .decorators import create_cacher, handle_db_errors
from .utils import delete_table_data, load_table_data, save_metadata, save_table_data

_select_cache = create_cacher()


class Command(ABC):
    @classmethod
    def try_command(cls, raw) -> Self | None:
        """Создает команду из строки ввода или возвращает None."""
        try:
            if not isinstance(raw, str):
                return None

            args = cls._split(raw)
            cls._validate_args(args)
            return cls.try_apply(args)
        except (ValueError, IndexError):
            return None

    @classmethod
    @abstractmethod
    def try_apply(cls, args) -> Self | None:
        """Создает команду из аргументов или возвращает None."""
        pass

    @abstractmethod
    def _execute(self, metadata) -> str:
        """Выполняет команду."""
        ...

    @handle_db_errors
    def execute(self, metadata) -> str:
        """Выполняет команду."""
        return self._execute(metadata)

    @classmethod
    @abstractmethod
    def _validate_args(cls, args):
        """Проверяет аргументы команды."""
        ...

    @staticmethod
    def _get_table(metadata, table_name):
        """Возвращает метаданные существующей таблицы."""
        ...

    @staticmethod
    def _assert_argument_count(length_validator, args):
        """Проверяет количество аргументов команды."""
        if not length_validator(len(args)):
            raise ValueError("Некорректное кол-во аргументов команды")

    @staticmethod
    def _assert_keyword_on_position(index, keyword, args):
        """Проверяет ключевое слово на заданной позиции."""
        if not args[index] == keyword:
            raise ValueError("Ошибка при разборе аргументов команды")

    @staticmethod
    def _split(raw):
        """Разбивает строку ввода на аргументы."""
        args = shlex.split(raw)
        return args


class DDLCommand(Command):
    @staticmethod
    def _save_metadata(metadata):
        """Сохраняет метаданные базы данных."""
        save_metadata(metadata)
        _select_cache.clear()


class DMLCommand(Command):
    @staticmethod
    def _load_table_data(table_name):
        """Загружает данные таблицы."""
        return load_table_data(table_name)

    @staticmethod
    def _save_table_data(table_name, data):
        """Сохраняет данные таблицы."""
        save_table_data(table_name, data)
        _select_cache.clear()

    @staticmethod
    def _format_rows(table_metadata, rows):
        """Форматирует записи таблицы в текстовую таблицу."""
        field_names = [column.name for column in table_metadata.columns.columns]

        pretty_table = PrettyTable()
        pretty_table.field_names = field_names
        for row in rows:
            pretty_table.add_row([row.get(name) for name in field_names])

        return pretty_table.get_string()

    @staticmethod
    def _parse_values(args_values):
        """Разбирает список значений для вставки."""
        ...

    @staticmethod
    def _parse_where(args_clause):
        """Разбирает условие where в словарь."""
        ...

    @staticmethod
    def _parse_set(args_clause):
        """Разбирает выражение set в словарь."""
        ...

    @staticmethod
    def _split(raw):
        """Разбивает строку ввода на аргументы с сохранением кавычек."""
        return shlex.split(raw, posix=False)


class ServiceCommand(Command):
    """Базовый класс служебных команд."""


class CreateTableCommand(DDLCommand):
    def __init__(self, table_name, columns):
        """Создает команду создания таблицы."""
        self._table_name = table_name
        self._col_descriptions = columns

    @classmethod
    def try_apply(cls, args):
        """Создает команду из строки ввода или возвращает None."""
        return CreateTableCommand(args[1], tuple(args[2:]))

    def _execute(self, metadata):
        """Создает таблицу."""
        create_table(metadata, self._table_name, self._col_descriptions)

        DDLCommand._save_metadata(metadata)

        return f"Таблица {self._table_name} создана успешно"

    @classmethod
    def _validate_args(cls, args):
        """Проверяет аргументы команды."""
        Command._assert_argument_count(lambda n: n >= 2, args)
        Command._assert_keyword_on_position(0, "create_table", args)


class DropTableCommand(DDLCommand):
    def __init__(self, table_name):
        """Создает команду удаления таблицы."""
        self._table_name = table_name

    @classmethod
    def try_apply(cls, args):
        """Создает команду из строки ввода или возвращает None."""
        return DropTableCommand(args[1])

    def _execute(self, metadata):
        """Удаляет таблицу."""
        drop_table(metadata, self._table_name)
        DDLCommand._save_metadata(metadata)
        delete_table_data(self._table_name)

        return f"Таблица {self._table_name} успешно удалена"

    @classmethod
    def _validate_args(cls, args):
        """Проверяет аргументы команды."""
        Command._assert_argument_count(lambda n: n == 2, args)
        Command._assert_keyword_on_position(0, "drop_table", args)


class ListTablesCommand(DDLCommand):
    @classmethod
    def try_apply(cls, args):
        """Создает команду из строки ввода или возвращает None."""
        return ListTablesCommand()

    def _execute(self, metadata):
        """Выводит список всех таблиц."""
        list_tables(metadata)

        return ""

    @classmethod
    def _validate_args(cls, args):
        """Проверяет аргументы команды."""
        Command._assert_argument_count(lambda n: n == 1, args)
        Command._assert_keyword_on_position(0, "list_tables", args)


class InfoCommand(DMLCommand):
    def __init__(self, table_name):
        """Создает команду вывода информации о таблице."""
        self._table_name = table_name

    @classmethod
    def try_apply(cls, args):
        """Создает команду из строки ввода или возвращает None."""
        return InfoCommand(args[1])

    def _execute(self, metadata):
        """Выводит информацию о таблице."""

        info_table(metadata, self._load_table_data(self._table_name), self._table_name)
        return ""

    @classmethod
    def _validate_args(cls, args):
        """Проверяет аргументы команды."""
        Command._assert_argument_count(lambda n: n == 2, args)
        Command._assert_keyword_on_position(0, "info", args)


class InsertCommand(DMLCommand):
    def __init__(self, table_name, values):
        """Создает команду вставки записи."""
        self._table_name = table_name
        self._values = values

    # <command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...)
    # - создать запись.
    @classmethod
    def try_apply(cls, args):
        """Создает команду из строки ввода или возвращает None."""
        return InsertCommand(args[2], args[4])

    def _execute(self, metadata):
        """Добавляет запись в таблицу."""
        self._save_table_data(
            self._table_name,
            insert(
                metadata,
                self._table_name,
                self._load_table_data(self._table_name),
                self._values,
            ),
        )
        return f"Строка успешно добавлена в таблицу {self._table_name}"

    @classmethod
    def _validate_args(cls, args):
        """Проверяет аргументы команды."""
        Command._assert_argument_count(lambda n: n >= 4, args)
        Command._assert_keyword_on_position(0, "insert", args)
        Command._assert_keyword_on_position(1, "into", args)
        Command._assert_keyword_on_position(3, "values", args)

    @staticmethod
    def _split(raw):
        """Разбивает строку ввода на аргументы."""

        head, sep, tail = raw.partition(" values ")
        args = shlex.split(head)
        if not sep:
            raise ValueError("Должны быть переданы значения после values")

        tail = tail.strip()
        if not (tail.startswith("(") and tail.endswith(")")):
            raise ValueError("Значения должны быть заключены в скобки")

        lexer = shlex.shlex(tail[1:-1], posix=False)
        lexer.whitespace = ", \t"
        lexer.whitespace_split = True
        insert_data = tuple(v.strip() for v in lexer)

        return [*args, "values", insert_data]


class SelectCommand(DMLCommand):
    def __init__(self, table_name, where_clause):
        """Создает команду выборки записей."""
        self._table_name = table_name
        self._where_clause = where_clause

    @classmethod
    def try_apply(cls, args):
        """Создает команду из строки ввода или возвращает None."""
        if len(args) == 3:
            return SelectCommand(args[2], ())
        else:
            return SelectCommand(args[2], (args[4], args[6]))

    def _execute(self, metadata):
        """Выводит записи таблицы."""
        return _select_cache(
            (self._table_name, self._where_clause),
            lambda: self._perform_select(metadata),
        )

    def _perform_select(self, metadata):
        """Выбирает записи таблицы и форматирует их."""
        select_result = select(
            metadata,
            self._table_name,
            self._load_table_data(self._table_name),
            self._where_clause,
        )
        return self._format_rows(metadata.find_table(self._table_name), select_result)

    @classmethod
    def _validate_args(cls, args):
        """Проверяет аргументы команды."""
        Command._assert_argument_count(lambda n: n == 3 or n == 7, args)
        Command._assert_keyword_on_position(0, "select", args)
        Command._assert_keyword_on_position(1, "from", args)
        if len(args) == 7:
            Command._assert_keyword_on_position(3, "where", args)
            Command._assert_keyword_on_position(5, "=", args)


class UpdateCommand(DMLCommand):
    def __init__(self, table_name, set_clause, where_clause):
        """Создает команду обновления записей."""
        self._table_name = table_name
        self._set_clause = set_clause
        self._where_clause = where_clause

    @classmethod
    def try_apply(cls, args):
        """Создает команду из строки ввода или возвращает None."""
        return UpdateCommand(args[1], (args[3], args[5]), (args[7], args[9]))

    def _execute(self, metadata):
        """Обновляет записи таблицы."""

        table_data, modified_count = update(
            metadata,
            self._table_name,
            self._load_table_data(self._table_name),
            self._where_clause,
            self._set_clause,
        )

        self._save_table_data(self._table_name, table_data)

        return f"Изменено {modified_count} записей"

    @classmethod
    def _validate_args(cls, args):
        """Проверяет аргументы команды."""
        Command._assert_argument_count(lambda n: n == 10, args)
        Command._assert_keyword_on_position(0, "update", args)
        Command._assert_keyword_on_position(2, "set", args)
        Command._assert_keyword_on_position(4, "=", args)
        Command._assert_keyword_on_position(6, "where", args)
        Command._assert_keyword_on_position(8, "=", args)


class DeleteCommand(DMLCommand):
    def __init__(self, table_name, where_clause):
        """Создает команду удаления записей."""
        self._table_name = table_name
        self._where_clause = where_clause

    # <command> delete from <имя_таблицы> where <столбец> = <значение>
    @classmethod
    def try_apply(cls, args):
        """Создает команду из строки ввода или возвращает None."""
        return DeleteCommand(args[2], (args[4], args[6]))

    def _execute(self, metadata):
        """Удаляет записи таблицы."""
        table_data = self._load_table_data(self._table_name)
        delete_result = delete(
            metadata,
            self._table_name,
            table_data,
            self._where_clause,
        )

        self._save_table_data(self._table_name, delete_result)

        return f"Удалено {len(table_data) - len(delete_result)} записей"

    @classmethod
    def _validate_args(cls, args):
        """Проверяет аргументы команды."""
        Command._assert_argument_count(lambda n: n == 7, args)
        Command._assert_keyword_on_position(0, "delete", args)
        Command._assert_keyword_on_position(1, "from", args)
        Command._assert_keyword_on_position(3, "where", args)
        Command._assert_keyword_on_position(5, "=", args)


class HelpCommand(ServiceCommand):
    @classmethod
    def try_apply(cls, args):
        """Создает команду из строки ввода или возвращает None."""
        return HelpCommand()

    def _execute(self, metadata):
        """Выводит справку по командам."""
        print("\n***Процесс работы с таблицей***")
        print("Функции:")
        print(
            "<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу"
        )
        print("<command> list_tables - показать список всех таблиц")
        print("<command> drop_table <имя_таблицы> - удалить таблицу")

        print("\n***Операции с данными***")
        print("Функции:")
        print(
            "<command> insert into <имя_таблицы> values "
            "(<значение1>, <значение2>, ...) - создать запись"
        )
        print(
            "<command> select from <имя_таблицы> where <столбец> = <значение> "
            "- прочитать записи по условию"
        )
        print("<command> select from <имя_таблицы> - прочитать все записи")
        print(
            "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
            "where <столбец_условия> = <значение_условия> - обновить запись"
        )
        print(
            "<command> delete from <имя_таблицы> where <столбец> = <значение> "
            "- удалить запись"
        )
        print("<command> info <имя_таблицы> - вывести информацию о таблице")

        print("\nОбщие команды:")
        print("<command> exit - выход из программы")
        print("<command> help - справочная информация\n")

        return ""

    @classmethod
    def _validate_args(cls, args):
        """Проверяет аргументы команды."""
        Command._assert_argument_count(lambda n: n == 1, args)
        Command._assert_keyword_on_position(0, "help", args)


class ExitCommand(ServiceCommand):
    @classmethod
    def try_apply(cls, args):
        """Создает команду из строки ввода или возвращает None."""
        return ExitCommand()

    def _execute(self, metadata):
        """Завершает работу программы."""
        exit(0)

    @classmethod
    def _validate_args(cls, args):
        """Проверяет аргументы команды."""
        Command._assert_argument_count(lambda n: n == 1, args)
        Command._assert_keyword_on_position(0, "exit", args)


class CommandRegistry:
    _COMMANDS = (
        CreateTableCommand,
        DropTableCommand,
        ListTablesCommand,
        InfoCommand,
        InsertCommand,
        SelectCommand,
        UpdateCommand,
        DeleteCommand,
        HelpCommand,
        ExitCommand,
    )

    def find_appropriate_command(self, args):
        """Возвращает команду, подходящую для строки ввода, или None."""
        ...
        for command in self._COMMANDS:
            apply_result = command.try_command(args)
            if apply_result:
                return apply_result

        return None
