# Лабораторная работа №7: HTTP клиент, сервер, REST API

Репозиторий содержит полноценное клиент-серверное решение на языке Python для реализации и исследования веб-протокола прикладного уровня HTTP (HyperText Transfer Protocol) и архитектурного стиля REST API (Representational State Transfer). Разработано в рамках курса **«Сети ЭВМ и телекоммуникации»**.

- **Учебное заведение:** ЮЗГУ
- **Кафедра:** Программной инженерии
- **Группа:** ПО-32б
- **Студент:** Эрденко М. Д.
- **Преподаватель:** ст. преподаватель кафедры ПИ Ефремов В. В.
- **Лицензия:** GNU General Public License v3.0 (GPL-3.0)

## Особенности реализации

- В строгом соответствии с требованиями методических указаний: **каждая строка исходного кода снабжена подробным комментарием**.
- Серверная часть (`rest_server.py`):
  - Построена на базе стандартных классов `HTTPServer` и `BaseHTTPRequestHandler` стандартной библиотеки Python (без тяжелых внешних фреймворков и сторонних зависимостей).
  - Реализует REST-интерфейс ресурса `/api/v1/devices` с поддержкой всех ключевых методов:
    - `GET /api/v1/devices` — получение коллекции устройств (HTTP 200 OK);
    - `GET /api/v1/devices/<id>` — получение устройства по идентификатору (HTTP 200 OK / 404 Not Found);
    - `POST /api/v1/devices` — добавление нового устройства из JSON-тела (HTTP 201 Created);
    - `PUT /api/v1/devices/<id>` — обновление параметров устройства (HTTP 200 OK / 404 Not Found);
    - `DELETE /api/v1/devices/<id>` — удаление устройства (HTTP 200 OK / 404 Not Found).
  - Формирует корректные служебные HTTP-заголовки: `Content-Type: application/json; charset=utf-8`, `Content-Length`, `Server`.
- Клиентская часть (`rest_client.py`):
  - Использует модуль `urllib.request` для последовательного тестирования всех CRUD-операций.
  - Устанавливает заголовки `Content-Type`, `Accept: application/json`, `User-Agent`.
  - Корректно обрабатывает коды ответов и ошибки `urllib.error.HTTPError`.
- Сетевой сниффинг (`http_rest_exchange.pcap`):
  - Полный перехват HTTP-трафика сессии, детальный анализ структуры PDU:
    - HTTP Request Line (метод, относительный URI, версия `HTTP/1.1`);
    - HTTP Request Headers (`Host`, `User-Agent`, `Content-Type`, `Content-Length`);
    - HTTP Request Body (JSON полезная нагрузка);
    - HTTP Response Status Line (версия, код состояния `200 OK` / `201 Created` / `404 Not Found`);
    - HTTP Response Headers и JSON тело ответа.

## Запуск

1. Запуск сервера:
```bash
python rest_server.py
```

2. Запуск клиента:
```bash
python rest_client.py
```
