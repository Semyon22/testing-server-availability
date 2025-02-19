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

#создание парсера аргументов
parser = argparse.ArgumentParser()
parser.add_argument("-H","--hosts",help = "Введите имя хоста(ов), несколько адресов указывайте через запятую без пробелов",required=True,type=validate_hosts)
parser.add_argument("-C","--count",help = "введите количество запросов",required=False,type=int,default=1)

args = parser.parse_args()

print(args.hosts, args.count)
