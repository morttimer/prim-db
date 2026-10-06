from sys import exit

from .parser import CommandRegistry, HelpCommand
from .utils import load_metadata


def run():
    """Запускает основной цикл обработки команд."""
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

            print(command.execute(metadata))
        except EOFError:
            exit(0)
        except KeyboardInterrupt:
            exit(1)
        except Exception as e:
            print(f"Произошла ошибка во время выполнения команды: {e}")
