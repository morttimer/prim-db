from shlex import split
from sys import exit

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata

METADATA_FILE_PATH = "./db_meta.json"


def print_help():
    """Выводит справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Запускает основной цикл обработки команд."""
    print_help()
    while True:
        metadata = load_metadata(METADATA_FILE_PATH)

        try:
            command = input(">>> Введите команду: ")
            command_args = split(command)

            match command_args[0]:
                case "create_table":
                    new_meta = create_table(metadata, command_args[1], command_args[2:])
                    save_metadata(METADATA_FILE_PATH, new_meta)
                    print("Таблица успешно создана")
                case "list_tables":
                    print(*list_tables(metadata))
                case "drop_table":
                    new_meta = drop_table(metadata, *command_args[1:])
                    save_metadata(METADATA_FILE_PATH, new_meta)
                    print("Таблица успешно удалена")
                case "exit":
                    exit(0)
                case "help":
                    print_help()
                case _:
                    print(f"Команды {command_args[0]} не существует. См. help")
        except EOFError:
            exit(0)
        except KeyboardInterrupt:
            exit(1)
        except Exception as e:
            print(f"Произошла ошибка во время выполнения команды: {e}")
