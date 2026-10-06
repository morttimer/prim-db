from functools import wraps
from time import monotonic_ns

from .exceptions import UserRejectedCommandError


def handle_db_errors(func):
    """Перехватывает ошибки операций с базой данных и выводит сообщение о них."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except UserRejectedCommandError as e:
            print(e)
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")

    return wrapper


def confirm_action(action_name):
    """Запрашивает подтверждение пользователя перед выполнением действия."""

    def outer(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if answer != "y":
                raise UserRejectedCommandError("Пользователь отменил команду")
            else:
                return func(*args, **kwargs)

        return wrapper

    return outer


def log_time(func):
    """Выводит время выполнения функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        time_before = monotonic_ns()
        result = func(*args, **kwargs)
        elapsed = (monotonic_ns() - time_before) / 10**9
        print(f'Функция "{func.__name__}" выполнилась за {elapsed:.3f} секунд')
        return result

    return wrapper


def create_cacher():
    """Создает функцию кэширования результатов по ключу."""
    cache = {}

    def cache_result(key, value_function):
        """Возвращает результат из кэша или вычисляет и сохраняет его."""
        if key not in cache:
            cache[key] = value_function()

        return cache[key]

    cache_result.clear = cache.clear
    return cache_result
