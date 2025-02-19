import argparse

#создание парсера аргументов
parser = argparse.ArgumentParser()
parser.add_argument("-H","--hosts",help = "введите имя хост(а/ов)",required=True,type=str)
parser.add_argument("-C","--count",help = "введите количество запросов",required=False,type=int,default=1)

args = parser.parse_args()

print(args.hosts, args.count)
