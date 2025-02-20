import argparse
import re
import requests 
import time
from requests.exceptions import (
    ConnectionError, Timeout, HTTPError, SSLError,
    InvalidURL, ContentDecodingError, TooManyRedirects
)

# Регулярное выражение для проверки URL 
URL_PATTERN = re.compile(r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

def validate_hosts(hosts:str)->list:
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
                f"Неверный формат адреса: {host}. Ожидается формат http://example.com или https://example.com"
            )
    

    return hosts  

def validate_file(file_path:str)->list:
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
        with open(file_path,'r',encoding='utf-8') as file:
            hosts=[host.strip() for host in file if host.strip()]
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
        print(f"Ошибка: путь {file_path} указывает на директорию, а не на файл.")
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
   
def get_args() -> argparse.Namespace: 
    """Парсит аргументы командой строки

    Returns:
        Namespace: Объект, содержащий аргументы командной строки.
    """      
    #создание парсера аргументов
    parser = argparse.ArgumentParser()
    #создание группы, где используется лишь один из параметров
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-H","--hosts",help = "Введите имя хоста(ов), несколько адресов указывайте через запятую без пробелов",type=validate_hosts)
    group.add_argument("-F","--file",help="Путь к файлу со списком хостов (по одному в строке)",type=validate_file)
    #добавление аргументов 
    parser.add_argument("-C","--count",help = "введите количество запросов",required=False,type=int,default=1)

    parser.add_argument("-O","--output",help = "путь до файла куда нужно сохранить вывод",required=False)
    
    return parser.parse_args()

def start_requests(hosts:list, count:int )->dict:
    """
    Функция выполняющая запросы к URL, и собирающая информацию о доступности серверов и времени ответа от них

    Args:
        hosts (list): список URL
        count (int): Количество запросов к каждому URL из hosts

    Returns:
        dict: Словарь с результатами проверки хостов. Ключи словаря — имена хостов,
                        значения — словари с метриками для каждого хоста
    """
    results = {}
    print("Идёт тестирование доступности серверов")
    for host in hosts:
        success_count, failed_count, error_count = 0, 0, 0
        response_times = []

        for _ in range(count):
            try:
                

                start_time = time.time()
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(host, headers=headers, timeout=5)  # Установим таймаут 5 секунд

                elapsed_time = round((time.time() - start_time) * 1000, 2)
                response_times.append(elapsed_time)

                if 200 <= response.status_code < 300:
                    success_count += 1
                elif 400 <= response.status_code < 600:
                    failed_count += 1

            except ConnectionError:
                error_count += 1
                print(f"Ошибка: не удалось подключиться к {host}. Проверьте URL и интернет-соединение.")

            except Timeout:
                error_count += 1
                print(f"Ошибка: время ожидания ответа от {host} истекло.")

            except HTTPError as e:
                error_count += 1
                print(f"Ошибка HTTP при запросе к {host}: {e}")

            except SSLError:
                error_count += 1
                print(f"Ошибка SSL при подключении к {host}. Возможны проблемы с сертификатом.")

            except InvalidURL:
                error_count += 1
                print(f"Ошибка: некорректный URL - {host}")

            except ContentDecodingError:
                error_count += 1
                print(f"Ошибка: сервер {host} вернул поврежденные данные.")

            except TooManyRedirects:
                error_count += 1
                print(f"Ошибка: слишком много перенаправлений при попытке доступа к {host}.")

            except requests.RequestException as e:
                error_count += 1
                print(f"Неизвестная ошибка при запросе к {host}: {e}")

        results[host] = {
            "Success": success_count,
            "Failed": failed_count,
            "Errors": error_count,
            "Min": min(response_times) if response_times else None,
            "Max": max(response_times) if response_times else None,
            "Avg": round(sum(response_times) / len(response_times), 2) if response_times else None
        }

    return results


def display_results(results:dict):
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

def save_to_file(output_path:str, results:dict):
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
            with open(output_path, 'w', encoding='utf-8') as file:
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
            print(f"Ошибка: путь {args.output} указывает на директорию, а не на файл.")
            raise SystemExit(1)
    except PermissionError:
            print(f"Ошибка: у вас нет прав на запись в файл {args.output}.")
            raise SystemExit(1)
    except IOError as e:
            print(f"Ошибка записи в файл {args.output}: {e}")
            raise SystemExit(1)
                    


if __name__=="__main__":
    #получение списка параметров
    args=get_args()
    #начало тестирования серверов
    results=start_requests(args.hosts if args.hosts else args.file, args.count) 
    #вывод в консоль или в файл
    if not args.output:
        display_results(results)
    else:
        save_to_file(args.output,results=results)

