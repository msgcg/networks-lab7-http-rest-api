# Импортируем стандартный модуль HTTP-сервера для обработки сетевых запросов прикладного уровня
from http.server import HTTPServer, BaseHTTPRequestHandler
# Импортируем модуль json для сериализации и десериализации структур данных формата REST
import json
# Импортируем модуль re для сопоставления URL-маршрутов с регулярными выражениями
import re

# Инициализируем хранилище сетевых устройств в оперативной памяти (имитация базы данных)
DEVICES_DB = {
    1: {"id": 1, "name": "Core-Router-01", "ip": "192.168.0.1", "role": "Gateway", "status": "online"},
    2: {"id": 2, "name": "Switch-Floor-2", "ip": "192.168.0.2", "role": "Distribution", "status": "online"},
    3: {"id": 3, "name": "Server-Storage", "ip": "192.168.0.10", "role": "Storage", "status": "offline"}
}
# Переменная счетчика для генерации уникальных числовых идентификаторов новых записей
NEXT_ID = 4

# Объявляем класс обработчика HTTP-запросов, наследующий стандартный BaseHTTPRequestHandler
class RestApiHandler(BaseHTTPRequestHandler):

    # Вспомогательный метод для отправки стандартных JSON-ответов клиенту с заданным кодом состояния
    def _send_json_response(self, status_code, data):
        # Преобразуем переданные данные в строку JSON с поддержкой кириллицы
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        # Кодируем сформированную строку JSON в массив байтов UTF-8
        body = json_str.encode('utf-8')
        # Отправляем в заголовок ответа числовой код статуса HTTP (200, 201, 404 и др.)
        self.send_response(status_code)
        # Устанавливаем заголовок Content-Type с указанием типа содержимого application/json и кодировки UTF-8
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        # Устанавливаем заголовок Content-Length с точным размером тела ответа в байтах
        self.send_header('Content-Length', str(len(body)))
        # Устанавливаем заголовок идентификации сервера
        self.send_header('Server', 'SWSU-Networks-REST/1.0')
        # Завершаем блок заголовков пустой строкой в соответствии со спецификацией HTTP
        self.end_headers()
        # Записываем байтовое тело ответа в сетевой поток вывода
        self.wfile.write(body)

    # Обработчик входящих HTTP-запросов методом GET (чтение коллекции или отдельного ресурса)
    def do_GET(self):
        # Проверяем, запрашивает ли клиент полный список сетевых устройств
        if self.path == '/api/v1/devices':
            # Извлекаем все устройства из хранилища в виде списка и отправляем с кодом 200 OK
            self._send_json_response(200, {"success": True, "count": len(DEVICES_DB), "items": list(DEVICES_DB.values())})
        # Проверяем соответствие запроса шаблону получения одного устройства по числовому ID
        elif re.match(r'^/api/v1/devices/(\d+)$', self.path):
            # Извлекаем строковый идентификатор устройства из URL и преобразуем в целое число
            dev_id = int(self.path.split('/')[-1])
            # Проверяем существование записи с данным идентификатором в словаре
            if dev_id in DEVICES_DB:
                # Если устройство найдено, отправляем его параметры с кодом 200 OK
                self._send_json_response(200, {"success": True, "device": DEVICES_DB[dev_id]})
            else:
                # Если идентификатор не найден, формируем и отправляем ошибку 404 Not Found
                self._send_json_response(404, {"success": False, "error": f"Устройство с ID {dev_id} не найдено"})
        else:
            # Для неизвестных путей возвращаем стандартный ответ 404 Not Found
            self._send_json_response(404, {"success": False, "error": "Маршрут API не поддерживается"})

    # Обработчик входящих HTTP-запросов методом POST (создание нового ресурса)
    def do_POST(self):
        # Разрешаем создание новых записей только по базовому пути коллекции /api/v1/devices
        if self.path == '/api/v1/devices':
            # Считываем значение заголовка Content-Length для определения размера тела запроса
            content_length = int(self.headers.get('Content-Length', 0))
            # Читаем точное количество байтов тела запроса из входного сетевого потока rfile
            body_bytes = self.rfile.read(content_length)
            # Парсим полученные JSON-данные тела запроса в словарь Python
            payload = json.loads(body_bytes.decode('utf-8'))
            # Объявляем глобальную переменную счетчика идентификаторов
            global NEXT_ID
            # Формируем новую запись сетевого устройства с автоинкрементным идентификатором
            new_device = {
                "id": NEXT_ID,
                "name": payload.get("name", "Unknown-Device"),
                "ip": payload.get("ip", "0.0.0.0"),
                "role": payload.get("role", "Node"),
                "status": payload.get("status", "online")
            }
            # Сохраняем вновь созданную запись в словарь базы данных
            DEVICES_DB[NEXT_ID] = new_device
            # Увеличиваем значение глобального счетчика для следующего устройства
            NEXT_ID += 1
            # Отправляем подтверждение успешного создания с кодом 201 Created и телом созданного ресурса
            self._send_json_response(201, {"success": True, "message": "Устройство успешно зарегистрировано", "device": new_device})
        else:
            # Для некорректных адресов возвращаем ошибку 400 Bad Request
            self._send_json_response(400, {"success": False, "error": "Некорректный эндпоинт для POST-запроса"})

    # Обработчик входящих HTTP-запросов методом PUT (модификация существующего ресурса)
    def do_PUT(self):
        # Проверяем регулярным выражением обращение к конкретному ресурсу по ID
        match = re.match(r'^/api/v1/devices/(\d+)$', self.path)
        if match:
            # Преобразуем извлеченный строковый ID в целое число
            dev_id = int(match.group(1))
            # Проверяем наличие обновляемой записи в базе данных
            if dev_id in DEVICES_DB:
                # Получаем размер передаваемого тела обновления
                content_length = int(self.headers.get('Content-Length', 0))
                # Считываем байты тела запроса
                body_bytes = self.rfile.read(content_length)
                # Декодируем и парсим JSON-объект обновления
                payload = json.loads(body_bytes.decode('utf-8'))
                # Обновляем поля записи переданными параметрами
                DEVICES_DB[dev_id].update(payload)
                # Отправляем успешный ответ с обновленной записью и кодом 200 OK
                self._send_json_response(200, {"success": True, "message": f"Устройство {dev_id} обновлено", "device": DEVICES_DB[dev_id]})
            else:
                # Возвращаем ошибку 404, если объект для обновления отсутствует
                self._send_json_response(404, {"success": False, "error": f"Устройство {dev_id} не найдено"})
        else:
            # Возвращаем 400 Bad Request при неверном формате пути
            self._send_json_response(400, {"success": False, "error": "Не указан ID устройства для обновления"})

    # Обработчик входящих HTTP-запросов методом DELETE (удаление ресурса)
    def do_DELETE(self):
        # Проверяем путь запроса на соответствие шаблону удаления по ID
        match = re.match(r'^/api/v1/devices/(\d+)$', self.path)
        if match:
            # Получаем числовой идентификатор удаляемого ресурса
            dev_id = int(match.group(1))
            # Проверяем наличие удаляемого устройства в структуре данных
            if dev_id in DEVICES_DB:
                # Удаляем запись из словаря по ключу
                removed = DEVICES_DB.pop(dev_id)
                # Возвращаем клиенту подтверждение удаления с кодом 200 OK
                self._send_json_response(200, {"success": True, "message": f"Устройство {dev_id} удалено", "deleted": removed})
            else:
                # Возвращаем ошибку 404 Not Found при отсутствии записи
                self._send_json_response(404, {"success": False, "error": f"Устройство {dev_id} не найдено"})
        else:
            # Возвращаем 400 Bad Request при некорректном запросе
            self._send_json_response(400, {"success": False, "error": "Неверный путь запроса на удаление"})

# Точка входа в программу запуска HTTP/REST сервера
def run_server(host='0.0.0.0', port=8080):
    # Создаем экземпляр стандартного HTTP-сервера с привязкой к адресу и классу обработчика
    server = HTTPServer((host, port), RestApiHandler)
    # Выводим в консоль уведомление о старте сервера и адресе прослушивания
    print(f"[+] REST API сервер запущен на http://{host}:{port}/api/v1/devices")
    try:
        # Запускаем непрерывный цикл ожидания и диспетчеризации входящих HTTP-соединений
        server.serve_forever()
    except KeyboardInterrupt:
        # Обрабатываем сигнал прерывания с клавиатуры (Ctrl+C) для корректной остановки
        print("\n[!] Остановка REST API сервера...")
        # Закрываем сокет прослушивания сервера
        server.server_close()

# Проверяем запуск скрипта в качестве главной программы
if __name__ == '__main__':
    # Запускаем сервер на локальном порту 8080
    run_server(port=8080)
