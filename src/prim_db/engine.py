from sys import exit

from .parser import CommandRegistry, HelpCommand
from .utils import init_metadata, load_metadata


def run():
    """Запускает основной цикл обработки команд."""
    init_metadata()
    metadata = load_metadata()
    HelpCommand().execute(metadata)

    registry = CommandRegistry()
    while True:
        metadata = load_metadata()

        try:
            raw_command = input(">>> Введите команду: ")
            command = registry.find_appropriate_command(raw_command)
            if command is None:
                print(f"Команды {raw_command} не существует. См. help")
                continue

            result = command.execute(metadata)

            if result is not None:
                print(result)

        except EOFError:
            exit(0)
        except KeyboardInterrupt:
            exit(1)
        except Exception as e:
            print(f"Произошла ошибка во время выполнения команды: {e}")
