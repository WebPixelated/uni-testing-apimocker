# API Testing Framework — apimocker.com

Фреймворк для автоматизированного тестирования REST API [apimocker.com](https://apimocker.com).  
Реализован на основе **Layered Architecture Pattern** с отчётностью Allure и логированием через Loguru.

---

## Стек технологий

| Инструмент        | Назначение                                   |
| ----------------- | -------------------------------------------- |
| Python 3.13       | Язык разработки                              |
| Pytest            | Test runner                                  |
| Requests          | HTTP-клиент для API-тестов                   |
| Playwright        | Зависимость фреймворка (скриншоты при фейле) |
| Allure            | Отчётность                                   |
| Loguru            | Логирование                                  |
| Pydantic Settings | Конфигурация через `.env`                    |
| Poetry            | Управление зависимостями                     |

---

## Архитектура проекта

```
testingapi/
├── tests/                  # Test Layer — тесты и фикстуры
│   ├── conftest.py
│   ├── test_users.py
│   ├── test_posts.py
│   ├── test_todos.py
│   └── test_comments.py
│
├── api/                    # Service Layer — HTTP-клиент
│   ├── base_client.py      # Базовый клиент (requests.Session)
│   ├── mock_api_client.py  # Методы для apimocker.com
│   └── endpoints.py        # URL-константы
│
├── core/                   # Infrastructure Layer
│   ├── config.py           # Настройки (Pydantic Settings + .env)
│   ├── logger.py           # Loguru setup
│   └── allure_steps.py     # Декораторы @step, @api_step, attach-хелперы
│
└── .github/
    └── workflows/
        └── ci.yml          # GitHub Actions
```

### Принцип слоёв

- **Tests** — только `assert` и фикстуры, без прямых вызовов `requests`
- **API** — вся HTTP-логика, сериализация, envelope-разворачивание
- **Core** — конфиг, логгер, allure-утилиты; не знает о тестах и API

---

## Установка

### Требования

- Python 3.13+
- [Poetry](https://python-poetry.org/docs/#installation)
- [Allure CLI](https://allurereport.org/docs/install/) (для просмотра отчётов)

### Шаги

```bash
# 1. Клонировать репозиторий
git clone https://github.com/WebPixelated/testingapi.git
cd testingapi

# 2. Установить зависимости
poetry install

# 3. Создать .env файл
Конфигурация описана ниже в README файле
```

---

## Конфигурация

Все настройки задаются через `.env` файл:

```env
BASE_URL=https://apimocker.com
REQUEST_TIMEOUT=10

LOG_LEVEL=DEBUG
LOG_FILE=logs/test_run.log
LOG_ROTATION=10 MB
```

---

## Запуск тестов

```bash
# Все тесты
poetry run pytest

# Только smoke-тесты
poetry run pytest -m smoke

# Конкретный модуль
poetry run pytest tests/test_users.py

# Параллельный запуск (pytest-xdist)
poetry run pytest -n auto
```

---

## Allure-отчёт

```bash
# Открыть интерактивный отчёт
allure serve allure-results
```

При падении теста к отчёту автоматически прикрепляются:

- JSON с последним запросом и ответом
- Лог-файл текущего прогона

---

## Покрытие

| Ресурс      | GET list | GET by ID | POST | PUT | DELETE |
| ----------- | -------- | --------- | ---- | --- | ------ |
| `/users`    | ✅       | ✅        | ✅   | ✅  | ✅     |
| `/posts`    | ✅       | ✅        | ✅   | ✅  | ✅     |
| `/todos`    | ✅       | ✅        | ✅   | ✅  | ✅     |
| `/comments` | ✅       | ✅        | ✅   | ✅  | ✅     |
