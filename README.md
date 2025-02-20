# Программа для тестирования доступности веб-серверов
## Навигация
- [Краткое описание](#краткое-описание)
- [Техническая реализация](#техническая-реализация)
- [Установка(Linux)](#установка-linux)
- [Описание флагов](#описание-флагов)
- [Примеры работы программы](#примеры-работы-программы)

## Краткое описание
<p>Эта консольная программа позволяет тестировать доступность веб-серверов, указанных в виде списка URL-адресов. Она выполняет HTTP/HTTPS-запросы к каждому серверу, собирает статистику о доступности и времени ответа, а также сохраняет результаты в файл или выводит их в консоль.</p>

## Техническая реализация
<ul>
    <li> <b>Язык программирования</b>: Python 3.9.0=<;
    <li> <b>Библиотека для выполнения запросов</b>: requests 2.31.0;
</ul>

## Установка Linux
1. Клонирование репозитория 

```git clone https://github.com/Semyon22/testing-server-availability.git```

2. Переход в директорию testing-server-availability

```cd testing-server-availability```

3. Создание виртуального окружения

```python3 -m venv venv```

4. Активация виртуального окружения

```source venv/bin/activate```

5. Установка зависимостей

```pip3 install -r requirements.txt```

## Описание флагов
<ul>
    <li> <b>-H,--hosts</b>: Принимает список адресов по которым будет производится тестирование.Можно указать несколько адресов через запятую без пробелов.Совместно с флагом -F не применим;
    <li> <b>-А,--file</b>: Принимает адрес файла со списком URL.Хосты должны быть указаным по одному в строке.Совместно с флагом -H не применим;
    <li> <b>-O,--output</b>: Принимает адрес файла для вывода результата.Необязательный параметр.Если не укзан, то вывод производится на консоль;
    <li> <b>-C,--count</b> Принимает значение количества запросов, которые будут отправлены на каждый хост.Необязательный параметр.Если не указан, по умолчанию принимает значение 1;
</ul>

## Примеры работы программы
### 1.Применение флага -H
запуск скрипта: 
```python3 main.py -H https://yandex.ru,https://google.com```
резултат работы программы: 
```
=== Итоговая статистика по хостам ===

Host: https://yandex.ru
  Success: 1
  Failed: 0
  Errors: 0
  Min: 795.34 ms
  Max: 795.34 ms
  Avg: 795.34 ms

Host: https://google.com
  Success: 1
  Failed: 0
  Errors: 0
  Min: 824.37 ms
  Max: 824.37 ms
  Avg: 824.37 ms
```
### 2. Применение флагов -H, -С
запуск скрипта: 
```python3 main.py -H https://yandex.ru,https://google.com -C 5```
резултат работы программы: 
```
=== Итоговая статистика по хостам ===

Host: https://yandex.ru
  Success: 5
  Failed: 0
  Errors: 0
  Min: 248.47 ms
  Max: 822.24 ms
  Avg: 468.64 ms

Host: https://google.com
  Success: 5
  Failed: 0
  Errors: 0
  Min: 768.79 ms
  Max: 887.94 ms
  Avg: 827.92 ms
```
### 3. Применение флага -F
содержание файла hosts.txt:
```
https://google.com
https://nstu.ru
https://amazon.com
```
запуск скрипта: 
```python3 main.py -F hosts.txt```
резултат работы программы: 
```
=== Итоговая статистика по хостам ===

Host: https://google.com
  Success: 1
  Failed: 0
  Errors: 0
  Min: 814.45 ms
  Max: 814.45 ms
  Avg: 814.45 ms

Host: https://nstu.ru
  Success: 1
  Failed: 0
  Errors: 0
  Min: 266.71 ms
  Max: 266.71 ms
  Avg: 266.71 ms

Host: https://amazon.com
  Success: 1
  Failed: 0
  Errors: 0
  Min: 1356.64 ms
  Max: 1356.64 ms
  Avg: 1356.64 ms
```
### Применение флага -O

содержание файла hosts.txt:
```
https://google.com
https://nstu.ru
https://amazon.com
```
запуск скрипта: 
```python3 main.py -F hosts.txt -C 5 -O output.txt```
резултат работы программы(консоль): 
```Результаты сохранены в файл: output.txt```
резултат работы программы(файл): 
``` 
=== Итоговая статистика по хостам ===

Host: https://google.com
  Success: 5
  Failed: 0
  Errors: 0
  Min: 784.52 ms
  Max: 848.33 ms
  Avg: 812.49 ms

Host: https://nstu.ru
  Success: 5
  Failed: 0
  Errors: 0
  Min: 202.96 ms
  Max: 225.03 ms
  Avg: 211.51 ms

Host: https://amazon.com
  Success: 5
  Failed: 0
  Errors: 0
  Min: 968.74 ms
  Max: 1216.2 ms
  Avg: 1028.09 ms

```