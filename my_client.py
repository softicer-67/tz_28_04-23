import json
import time
import urllib.request


WHITE = '\033[00m'
GREEN = '\033[0;92m'
RED = '\033[1;31m'


# функция для отображения таблицы
def display_table(rows):
    # выводим строки таблицы
    color = GREEN
    for row in rows:
        print(f'{row["id"]}  {row["name"]}  {color}{row["price"]}{WHITE}')


# функция для получения текущего состояния таблицы
def get_table_state():
    with urllib.request.urlopen('http://localhost:8080/table') as response:
        data = json.loads(response.read().decode())
        return data['rows'], data['revision']


# функция для получения изменений, произошедших после указанной ревизии
def get_table_changes(since_revision):
    with urllib.request.urlopen(f'http://localhost:8080/table/changes?since={since_revision}') as response:
        data = json.loads(response.read().decode())
        return data['rows'], data['revision']


# получаем текущее состояние таблицы и отображаем ее
rows, revision = get_table_state()
display_table(rows)
# запоминаем номер последней ревизии состояния таблицы
last_revision = revision

# основной цикл программы
while True:
    try:
        # получаем изменения, произошедшие после последней ревизии
        rows, revision = get_table_changes(last_revision)
        # в случае, если нет изменений, ждем некоторое время
        if not rows:
            time.sleep(1)
            continue
        # отображаем изменения
        print(f'Changes since revision {last_revision}:')
        display_table(rows)
        # обновляем номер последней ревизии
        last_revision = revision
    except:
        # если произошла ошибка, выводим сообщение и ждем некоторое время, чтобы не перегружать сервер
        print('Error: connection lost')
        time.sleep(5)
