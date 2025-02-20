import argparse
import re
import time
import asyncio
import aiohttp


# Регулярное выражение для проверки URL
URL_PATTERN = re.compile(r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
results = {}


def display_results(results: dict):
    """Выводит результаты тестирования веб-серверов на консоль

    Args:
        results (dict): Словарь с результатами проверки хостов. Ключи словаря — имена хостов,
                        значения — словари с метриками для каждого хоста
    """
    print("\n=== Итоговая статистика по хостам ===\n")
    for host, data in results.items():
        print(f"Host: {host}")
        print(f"  Success: {data['Success']}")
        print(f"  Failed: {data['Failed']}")
        print(f"  Errors: {data['Errors']}")
        print(f"  Min: {data['Min']} ms")
        print(f"  Max: {data['Max']} ms")
        print(f"  Avg: {data['Avg']} ms\n")


def save_to_file(output_path: str, results: dict):
    """Сохраняет результаты проверки хостов в текстовый файл.

    Args:
        output_path (str): Путь к файлу, в который будут сохранены результаты.
                           Если файл не существует, он будет создан. Если файл существует,
                           его содержимое будет перезаписано.
        results (dict): Словарь с результатами проверки хостов. Ключи словаря — имена хостов,
                        значения — словари с метриками для каждого хоста

    Raises:
        SystemExit: Вызывается в следующих случаях:
                   - Указанный путь ведёт к директории, а не к файлу (IsADirectoryError).
                   - Нет прав на запись в файл (PermissionError).
                   - Ошибка ввода-вывода при записи файла (IOError).
                   - Файл не найден (FileNotFoundError).
    """
    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write("=== Итоговая статистика по хостам ===\n\n")
            for host, data in results.items():
                file.write(f"Host: {host}\n")
                file.write(f"  Success: {data['Success']}\n")
                file.write(f"  Failed: {data['Failed']}\n")
                file.write(f"  Errors: {data['Errors']}\n")
                file.write(f"  Min: {data['Min']} ms\n")
                file.write(f"  Max: {data['Max']} ms\n")
                file.write(f"  Avg: {data['Avg']} ms\n\n")
        print(f"Результаты сохранены в файл: {output_path}")

    except FileNotFoundError:
        print(f"Ошибка: файл {args.output} не найден.")
        raise SystemExit(1)
    except IsADirectoryError:
        print(
            f"Ошибка: путь {
                args.output} указывает на директорию, а не на файл."
        )
        raise SystemExit(1)
    except PermissionError:
        print(f"Ошибка: у вас нет прав на запись в файл {args.output}.")
        raise SystemExit(1)
    except IOError as e:
        print(f"Ошибка записи в файл {args.output}: {e}")
        raise SystemExit(1)


def get_args() -> argparse.Namespace:
    """Парсит аргументы командой строки

    Returns:
        Namespace: Объект, содержащий аргументы командной строки.
    """
    # создание парсера аргументов
    parser = argparse.ArgumentParser()
    # создание группы, где используется лишь один из параметров
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-H",
        "--hosts",
        help="Введите имя хоста(ов), несколько адресов указывайте через запятую без пробелов",
        type=validate_hosts,
    )
    group.add_argument(
        "-F",
        "--file",
        help="Путь к файлу со списком хостов (по одному в строке)",
        type=validate_file,
    )
    # добавление аргументов
    parser.add_argument(
        "-C",
        "--count",
        help="введите количество запросов",
        required=False,
        type=lambda x: (
            int(x) if int(x) > 0 else parser.error("Значение должно быть больше нуля")),
        default=1,
    )

    parser.add_argument(
        "-O",
        "--output",
        help="путь до файла куда нужно сохранить вывод",
        required=False,
    )

    return parser.parse_args()


def validate_hosts(hosts: str) -> list:
    """Разделяет строку по запятым и проверяет каждый хост на соответствие формату URL

    Args:
        hosts (str): строка с переданными URL через запятую

    Raises:
        argparse.ArgumentTypeError: вызывается в случае не соответсвия URL шаблону регулярного выражения

    Returns:
        list: массив провалидированных URL
    """

    hosts = hosts.split(",")
    for host in hosts:
        if not URL_PATTERN.match(host):
            raise argparse.ArgumentTypeError(
                f"Неверный формат адреса: {host}. Ожидается формат http://example.com или https://example.com")

    return hosts


def validate_file(file_path: str) -> list:
    """Проверяет и валидирует файл, содержащий список хостов (URL-адресов).

    Args:
        file_path (str): Путь к файлу, содержащему список хостов (по одному на строку).
                          Ожидается, что каждая строка будет содержать URL-адрес
                          в формате http://example.com или https://example.com.

    Raises:
        SystemExit: Вызывается в следующих случаях:
                    - Файл не найден (FileNotFoundError).
                    - Указанный путь ведёт к директории, а не к файлу (IsADirectoryError).
                    - Нет прав на чтение файла (PermissionError).
                    - Ошибка ввода-вывода при чтении файла (IOError).
                    - Неверная кодировка файла (UnicodeDecodeError).
                    - Файл пуст (нет ни одного хоста).
                    - Один или несколько URL-адресов в файле имеют неверный формат.
    Returns:
        list: Список строк, где каждая строка представляет собой валидный URL-адрес
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            hosts = [host.strip() for host in file if host.strip()]
        if not hosts:
            print(f"файл {file_path} пуст введите хотя бы один URL ")
            raise SystemExit(1)
        for host in hosts:
            if not URL_PATTERN.match(host):
                print(
                    f"Ошибка в файле {file_path}: неверный формат адреса {host}. "
                    f"Ожидается формат http://example.com или https://example.com"
                )
                raise SystemExit(1)
        return hosts
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
        raise SystemExit(1)
    except IsADirectoryError:
        print(
            f"Ошибка: путь {file_path} указывает на директорию, а не на файл.")
        raise SystemExit(1)
    except PermissionError:
        print(f"Ошибка: у вас нет прав на чтение файла {file_path}.")
        raise SystemExit(1)
    except IOError as e:
        print(f"Ошибка чтения файла {file_path}: {e}")
        raise SystemExit(1)
    except UnicodeDecodeError:
        print(f"Ошибка при чтении файла {file_path}: неверная кодировка.")
        raise SystemExit(1)


async def start_request(host: str, count: int):
    """Выполняет асинхронные HTTP-запросы к указанному хосту и собирает статистику.

    Args:
        host (str): URL хоста, к которому выполняются запросы.
        count (int): Количество запросов, которые необходимо отправить.

    Description:
        - Создает асинхронную сессию с помощью aiohttp.
        - Отправляет указанное количество GET-запросов к хосту.
        - Измеряет время ответа и классифицирует статус-коды:
            - 200–299: успешные запросы.
            - 400–599: неудачные запросы.
        - Обрабатывает возможные ошибки (таймауты, проблемы соединения и др.).
        - Сохраняет статистику (успехи, ошибки, минимальное, максимальное и среднее время отклика)
          в глобальном словаре `results`.
    """
    success_count, failed_count, error_count = 0, 0, 0
    response_times = []
    async with aiohttp.ClientSession() as session:
        for _ in range(count):
            try:
                start_time = time.time()
                # один запрос ушел, пока нет ответа выполняется следующий
                response = await session.get(url=host)
                elapsed_time = round((time.time() - start_time) * 1000, 2)
                response_times.append(elapsed_time)

                if 200 <= response.status < 300:
                    success_count += 1
                elif 400 <= response.status < 600:
                    failed_count += 1
            except aiohttp.ClientConnectionError:
                error_count += 1
                print(
                    f"Ошибка: не удалось подключиться к {host}. Проверьте URL и интернет-соединение.")

            except asyncio.TimeoutError:
                error_count += 1
                print(f"Ошибка: время ожидания ответа от {host} истекло.")

            except aiohttp.ClientError as e:
                error_count += 1
                print(f"Ошибка при запросе к {host}: {e}")

    results[host] = {
        "Success": success_count,
        "Failed": failed_count,
        "Errors": error_count,
        "Min": min(response_times) if response_times else None,
        "Max": max(response_times) if response_times else None,
        "Avg": (
            round(sum(response_times) / len(response_times), 2)
            if response_times
            else None
        ),
    }


async def gather_data(hosts: list, count: int):
    """Запускает асинхронные задачи для выполнения запросов к нескольким хостам одновременно.

    Args:
        hosts (list): Список URL-адресов хостов, к которым выполняются запросы.
        count (int): Количество запросов для каждого хоста.

    Description:
        - Для каждого хоста создает асинхронную задачу `start_request()`.
        - Все задачи выполняются параллельно с помощью `asyncio.gather()`,
          что позволяет эффективно обрабатывать множество запросов одновременно.
    """
    tasks = []
    for host in hosts:
        task = asyncio.create_task(start_request(host, count))
        tasks.append(task)
    await asyncio.gather(*tasks)


if __name__ == "__main__":

    # получение списка параметров
    args = get_args()

    print("идёт тестирование доступности серверов")
    # начало тестирования серверов
    asyncio.run(
        gather_data(
            args.hosts if args.hosts else args.file,
            args.count))
    # вывод в консоль или в файл
    if not args.output:
        display_results(results)
    else:
        save_to_file(args.output, results=results)
