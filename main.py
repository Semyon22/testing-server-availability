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
            raise argparse.ArgumentTypeError(f"файл {file_path} пуст введите хотя бы один URL ")
        for host in hosts:
            if not URL_PATTERN.match(host):
                raise argparse.ArgumentTypeError(
                    f"Ошибка в файле {file_path}: неверный формат адреса {host}. "
                    f"Ожидается формат http://example.com или https://example.com"
                )
        return hosts
    except FileNotFoundError:
        raise argparse.ArgumentTypeError(f"Файл {file_path} не найден.")
    except IOError:
        raise argparse.ArgumentTypeError(f"Ошибка чтения файла {file_path}")
    
#создание парсера аргументов
parser = argparse.ArgumentParser()
#создание группы, где используется лишь один из параметров
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-H","--hosts",help = "Введите имя хоста(ов), несколько адресов указывайте через запятую без пробелов",type=validate_hosts)
group.add_argument("-F","--file",help="Путь к файлу со списком хостов (по одному в строке)",type=validate_file)

parser.add_argument("-C","--count",help = "введите количество запросов",required=False,type=int,default=1)

args = parser.parse_args()

print(args.hosts if args.hosts else args.file, args.count)
