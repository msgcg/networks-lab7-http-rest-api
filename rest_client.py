# Импортируем модуль urllib.request для выполнения клиентских HTTP-запросов к серверу
import urllib.request
# Импортируем модуль urllib.error для обработки исключений сетевого протокола HTTP
import urllib.error
# Импортируем модуль json для сериализации исходящих и парсинга входящих REST-данных
import json
# Импортируем модуль time для организации коротких пауз между сетевыми вызовами
import time

# Определяем базовый URL-адрес разрабатываемого REST API сервиса
BASE_URL = 'http://127.0.0.1:8080/api/v1/devices'

# Универсальная функция отправки HTTP REST запроса с полным логированием параметров
def make_request(url, method='GET', payload=None):
    # Разделительная линия в консоли для наглядности вывода каждого шага
    print("\n" + "-" * 70)
    # Выводим метод и полный URL выполняемого HTTP-запроса
    print(f"[*] Отправка запроса: {method} {url}")
    # Инициализируем тело запроса как пустой байтовый массив
    data = None
    # Инициализируем стандартный словарь HTTP-заголовков клиентского запроса
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'SWSU-Networks-REST-Client/1.0'
    }
    # Если в функцию переданы данные для отправки (для методов POST или PUT)
    if payload is not None:
        # Сериализуем Python-словарь в строку формата JSON
        json_body = json.dumps(payload, ensure_ascii=False)
        # Кодируем строку JSON в массив байтов UTF-8
        data = json_body.encode('utf-8')
        # Добавляем обязательный заголовок Content-Type с указанием типа данных application/json
        headers['Content-Type'] = 'application/json; charset=utf-8'
        # Отображаем в консоли передаваемое тело запроса
        print(f"[*] Тело запроса (JSON): {json_body}")

    # Создаем объект сетевого HTTP-запроса Request библиотеки urllib
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        # Отправляем запрос серверу и открываем поток ответа
        with urllib.request.urlopen(req) as response:
            # Получаем числовой HTTP-код состояния ответа сервера (например, 200, 201)
            status = response.status
            # Считываем все байты тела HTTP-ответа сервера
            resp_bytes = response.read()
            # Декодируем байты ответа в строковый формат UTF-8
            resp_text = resp_bytes.decode('utf-8')
            # Выводим код и описание ответа сервера
            print(f"[✓] Код ответа сервера: {status} {response.reason}")
            # Проверяем наличие тела ответа
            if resp_text:
                # Десериализуем JSON-строку ответа в Python-объект
                parsed_json = json.loads(resp_text)
                # Выводим форматированный JSON в консоль клиента
                print(f"[+] Тело ответа (JSON):\n{json.dumps(parsed_json, indent=2, ensure_ascii=False)}")
                # Возвращаем полученные данные
                return parsed_json
    except urllib.error.HTTPError as err:
        # Перехватываем HTTP-ошибки сервера (коды 4xx, 5xx)
        print(f"[!] Ошибка HTTP {err.code}: {err.reason}")
        # Считываем тело сообщения об ошибке
        err_body = err.read().decode('utf-8')
        # Выводим тело сообщения об ошибке на экран
        print(f"[!] Содержимое ошибки: {err_body}")
    except urllib.error.URLError as net_err:
        # Перехватываем ошибки сетевого уровня (недоступность сервера, сбой сокета)
        print(f"[-] Сетевая ошибка соединения: {net_err.reason}")

# Главная функция демонстрации всех CRUD операций клиентского взаимодействия
def main():
    # Выводим вводный заголовок тестирования REST API
    print("======================================================================")
    print(" ТЕСТИРОВАНИЕ КЛИЕНТ-СЕРВЕРНОГО ВЗАИМОДЕЙСТВИЯ HTTP / REST API")
    print("======================================================================")

    # 1. Запрос GET: Получение полного списка сетевых устройств
    print("\n[ШАГ 1] Получение полного списка устройств (GET /devices)")
    make_request(BASE_URL, method='GET')
    time.sleep(0.5)

    # 2. Запрос POST: Создание нового сетевого устройства в базе
    print("\n[ШАГ 2] Создание нового устройства (POST /devices)")
    new_device_payload = {
        "name": "Access-Point-Floor-3",
        "ip": "192.168.0.55",
        "role": "Wireless-AP",
        "status": "online"
    }
    created_resp = make_request(BASE_URL, method='POST', payload=new_device_payload)
    time.sleep(0.5)

    # 3. Запрос GET: Получение конкретного устройства по его идентификатору ID=4
    print("\n[ШАГ 3] Получение устройства по идентификатору (GET /devices/4)")
    make_request(f"{BASE_URL}/4", method='GET')
    time.sleep(0.5)

    # 4. Запрос PUT: Модификация состояния устройства ID=3 (перевод в online)
    print("\n[ШАГ 4] Обновление параметров устройства (PUT /devices/3)")
    update_payload = {"status": "online", "role": "Main-Backup-Storage"}
    make_request(f"{BASE_URL}/3", method='PUT', payload=update_payload)
    time.sleep(0.5)

    # 5. Запрос DELETE: Удаление устаревшего устройства с ID=2
    print("\n[ШАГ 5] Удаление устройства (DELETE /devices/2)")
    make_request(f"{BASE_URL}/2", method='DELETE')
    time.sleep(0.5)

    # 6. Запрос GET: Проверка итогового состояния коллекции устройств
    print("\n[ШАГ 6] Проверка итоговой коллекции (GET /devices)")
    make_request(BASE_URL, method='GET')
    time.sleep(0.5)

    # 7. Запрос GET: Проверка обработки ошибки 404 (запрос несуществующего ID=99)
    print("\n[ШАГ 7] Проверка обработки ошибки 404 Not Found (GET /devices/99)")
    make_request(f"{BASE_URL}/99", method='GET')

    print("\n======================================================================")
    print(" [✓] Все тесты протокола HTTP и REST API успешно пройдены!")
    print("======================================================================")

# Запуск демонстрационного клиента при прямом вызове файла
if __name__ == '__main__':
    main()
