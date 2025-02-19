import argparse
import re

# Регулярное выражение для проверки URL (http://example.com ИЛИ https://example.com)
URL_PATTERN = re.compile(r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
#функция проверяющая корректность host
def validate_hosts(hosts_str):
    """Разделяет строку по запятым и проверяет каждый хост на соответствие формату URL."""
    
    hosts = hosts_str.split(",")  # Разделяем строку по запятым
    for host in hosts:
        if not URL_PATTERN.match(host):
            raise argparse.ArgumentTypeError(
                f"Неверный формат адреса: {host}. Ожидается формат http://example.com или https://example.com"
            )
    return hosts  # Возвращаем список хостов

def validate_file(file_path):
    """ Читает файл разбитый по строкам и проверяет, что URL корректен """
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
   
    
#создание парсера аргументов
parser = argparse.ArgumentParser()
#создание группы, где используется лишь один из параметров
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-H","--hosts",help = "Введите имя хоста(ов), несколько адресов указывайте через запятую без пробелов",type=validate_hosts)
group.add_argument("-F","--file",help="Путь к файлу со списком хостов (по одному в строке)",type=validate_file)

parser.add_argument("-C","--count",help = "введите количество запросов",required=False,type=int,default=1)

parser.add_argument("-O","--output",help = "путь до файла куда нужно сохранить вывод",required=False)

args = parser.parse_args()
#выбор того куда выводить информацию 
if not args.output:
    print(args.hosts if args.hosts else args.file, args.count)
else:
    try:
        with open(args.output,'w',encoding='utf-8') as file:
            hosts = args.hosts if args.hosts else args.file, args.count
            file.write(f"Хосты: {hosts}\nКоличество запросов: {args.count}\n")
        print(f"Результат сохранен в файл: {args.output}")
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
