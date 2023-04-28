import json
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


# функция для получения хеша строки
def get_hash(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()


# класс для хранения таблицы и ее изменений
class Table:
    def __init__(self):
        self.data = []
        self.hash_table = {}
        self.revision = 0

    # функция для добавления строки в таблицу
    def add_row(self, row):
        # находим место, где нужно вставить строку, чтобы сохранить сортировку
        i = 0
        while i < len(self.data) and row['id'] > self.data[i]['id']:
            i += 1
        self.data.insert(i, row)
        # обновляем хеш-таблицу
        self.hash_table[get_hash(row['id'])] = row
        # увеличиваем номер ревизии
        self.revision += 1

    # функция для удаления строки из таблицы
    def remove_row(self, row_id):
        # находим индекс строки
        i = self.find_row_index(row_id)
        if i != -1:
            # удаляем строку из таблицы и из хеш-таблицы
            row = self.data.pop(i)
            del self.hash_table[get_hash(row['id'])]
            # увеличиваем номер ревизии
            self.revision += 1

    # функция для поиска индекса строки по ее id
    def find_row_index(self, row_id):
        # ищем строку в хеш-таблице
        row = self.hash_table.get(get_hash(row_id))
        if row is None:
            return -1
        # ищем строку в списке
        for i, r in enumerate(self.data):
            if r['id'] == row_id:
                return i
        return -1

    # функция для получения изменений, произошедших после указанной ревизии
    def get_changes_since_revision(self, revision):
        # создаем список измененных строк
        changed_rows = []
        for row in self.data:
            # если строка была изменена после указанной ревизии, добавляем ее в список
            if row['revision'] > revision:
                changed_rows.append(row)
        # возвращаем список измененных строк и новый номер ревизии
        return changed_rows, self.revision

    # функция для получения текущего состояния таблицы
    def get_state(self):
        # создаем копию списка строк
        rows = self.data.copy()
        # устанавливаем номер ревизии для каждой строки
        for row in rows:
            row['revision'] = self.revision
        # возвращаем список строк и номер ревизии
        return rows, self.revision


# класс для обработки HTTP-запросов
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # парсим URL и параметры запроса
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        # если запрос на получение текущего состояния таблицы
        if parsed_url.path == '/table':
            # получаем текущее состояние таблицы и отправляем ответ в виде JSON
            rows, revision = table.get_state()
            self.send_json_response(rows, revision)

        # если запрос на получение изменений, произошедших после указанной ревизии
        elif parsed_url.path == '/table/changes':
            # если не задан параметр 'since', возвращаем ошибку
            if 'since' not in query_params:
                self.send_response(400)
                self.end_headers()
                return
            # получаем номер ревизии из параметра 'since'
            since_revision = int(query_params['since'][0])
            # получаем изменения, произошедшие после указанной ревизии
            changed_rows, revision = table.get_changes_since_revision(since_revision)
            # отправляем ответ в виде JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'rows': changed_rows, 'revision': revision}).encode())

    def do_POST(self):
        # парсим URL
        parsed_url = urlparse(self.path)
        # если запрос на добавление строки
        if parsed_url.path == '/table/add':
            # получаем данные строки из тела запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            row = json.loads(post_data.decode())
            # добавляем строку в таблицу
            table.add_row(row)
            # получаем текущее состояние таблицы и отправляем ответ в виде JSON
            rows, revision = table.get_state()
            self.send_json_response(rows, revision)

        # если запрос на удаление строки
        elif parsed_url.path == '/table/remove':
            # получаем id строки из параметра 'id'
            query_params = parse_qs(parsed_url.query)
            if 'id' not in query_params:
                self.send_response(400)
                self.end_headers()
                return
            row_id = query_params['id'][0]
            # удаляем строку из таблицы
            table.remove_row(row_id)
            # получаем текущее состояние таблицы и отправляем ответ в виде JSON
            rows, revision = table.get_state()
            self.send_json_response(rows, revision)

    # функция получает текущее состояние таблицы и отправляет ответ в виде JSON
    def send_json_response(self, rows, revision):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'rows': rows, 'revision': revision}).encode())


# создаем экземпляр таблицы
table = Table()
# заполняем таблицу начальными данными
table.add_row({'id': '1', 'name': 'BTC', 'price': 111, 'revision': 1})
table.add_row({'id': '2', 'name': 'LTC', 'price': 222, 'revision': 2})
table.add_row({'id': '3', 'name': 'ETH', 'price': 333, 'revision': 3})

# адрес и порт сервера
server_address = ('localhost', 8080)
# создаем HTTP-сервер
httpd = HTTPServer(server_address, RequestHandler)

print(f'Starting server on {server_address[0]}:{server_address[1]}')
# запускаем HTTP-сервер
httpd.serve_forever()
