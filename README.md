# 🏢 FastAPI Organization Structure API

REST API для управления организационной структурой компании (подразделения и сотрудники) с поддержкой иерархического дерева подразделений.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 📋 Содержание

- [Возможности](#-возможности)
- [Технологический стек](#-технологический-стек)
- [Архитектура проекта](#-архитектура-проекта)
- [Быстрый старт](#-быстрый-старт)
- [API Endpoints](#-api-endpoints)
- [Примеры использования](#-примеры-использования)
- [Тестирование](#-тестирование)
- [Разработка](#-разработка)
- [Структура проекта](#-структура-проекта)

---

## ✨ Возможности

- 🌳 **Иерархическое дерево подразделений** с неограниченной глубиной вложенности
- 👥 **Управление сотрудниками** с привязкой к подразделениям
- 🔄 **Гибкое удаление подразделений**:
  - Каскадное удаление (со всеми дочерними подразделениями и сотрудниками)
  - Удаление с переназначением сотрудников в другое подразделение
- 🔒 **Защита от циклических ссылок** в дереве подразделений
- ✅ **Валидация данных** с помощью Pydantic
- 📊 **Получение дерева подразделений** с настраиваемой глубиной
- 🐳 **Docker-ready** - готов к запуску в контейнерах
- 🧪 **Покрытие тестами** - unit и integration тесты
- 📚 **Автоматическая документация** - Swagger UI и ReDoc

---

## 🛠 Технологический стек

### Backend
- **FastAPI** 0.104+ - современный, быстрый web-фреймворк
- **SQLAlchemy** 2.0+ - ORM для работы с базой данных
- **Pydantic** 2.5+ - валидация и сериализация данных
- **Alembic** 1.12+ - миграции базы данных

### База данных
- **PostgreSQL** 18 - основная СУБД для production
- **SQLite** - in-memory база для тестов

### Инфраструктура
- **Docker** & **Docker Compose** - контейнеризация
- **pytest** - фреймворк для тестирования
- **uvicorn** - ASGI сервер

---

## 🏗 Архитектура проекта

Проект следует **принципам чистой архитектуры** с разделением на слои:

```
┌─────────────────────────────────────────────┐
│           API Layer (routes)                │
│  - HTTP endpoints                           │
│  - Request/Response handling                │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│        Business Logic (services)            │
│  - Бизнес-правила                           │
│  - Валидация циклов                         │
│  - Обработка удаления                       │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│      Data Access Layer (repositories)       │
│  - CRUD операции                            │
│  - Запросы к БД                             │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Database Layer (models)            │
│  - SQLAlchemy модели                        │
│  - Схема БД                                 │
└─────────────────────────────────────────────┘
```

### Ключевые паттерны:
- **Repository Pattern** - абстракция доступа к данным
- **Service Layer** - бизнес-логика отделена от API
- **Dependency Injection** - через FastAPI Depends
- **DTO Pattern** - Pydantic схемы для валидации

---

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Git

### 1. Клонирование репозитория

```bash
git clone https://github.com/xingsir12/FastAPIOrganization
cd FastAPIOrganization
```

### 2. Создание файла окружения

```bash
cp .env.example .env
```

Отредактируйте `.env` при необходимости:

```env
APP_NAME="FastAPI Organization"
DEBUG=False

DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=organization_db

SECRET_KEY=your-secret-key-here
```

### 3. Запуск через Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка работы
curl http://localhost:8000/health
```

**API доступен по адресу:**
- 🌐 API: http://localhost:8000
- 📚 Swagger UI: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc

### 4. Остановка

```bash
docker-compose down
```

---

## 📡 API Endpoints

### Подразделения

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/v1/departments/` | Создать подразделение |
| `GET` | `/api/v1/departments/` | Получить список всех подразделений |
| `GET` | `/api/v1/departments/{id}` | Получить подразделение с деревом |
| `PATCH` | `/api/v1/departments/{id}` | Обновить подразделение |
| `DELETE` | `/api/v1/departments/{id}` | Удалить подразделение |

### Сотрудники

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/v1/departments/{id}/employees/` | Создать сотрудника в подразделении |
| `GET` | `/api/v1/employees/` | Получить список сотрудников |
| `GET` | `/api/v1/employees/{id}` | Получить сотрудника по ID |
| `PATCH` | `/api/v1/employees/{id}` | Обновить сотрудника |
| `DELETE` | `/api/v1/employees/{id}` | Удалить сотрудника |

### Health Check

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/` | Проверка работоспособности API |
| `GET` | `/health` | Детальная проверка (включая БД) |

---

## 💡 Примеры использования

### Создание подразделения

```bash
curl -X POST "http://localhost:8000/api/v1/departments/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "IT Department",
    "parent_id": null
  }'
```

**Ответ:**
```json
{
  "id": 1,
  "name": "IT Department",
  "parent_id": null,
  "created_at": "2024-01-15T10:30:00"
}
```

### Создание дочернего подразделения

```bash
curl -X POST "http://localhost:8000/api/v1/departments/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Backend Team",
    "parent_id": 1
  }'
```

### Создание сотрудника

```bash
curl -X POST "http://localhost:8000/api/v1/departments/2/employees/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "position": "Senior Developer",
    "hired_at": "2024-01-15"
  }'
```

**Ответ:**
```json
{
  "id": 1,
  "department_id": 2,
  "full_name": "John Doe",
  "position": "Senior Developer",
  "hired_at": "2024-01-15",
  "created_at": "2024-01-15T10:35:00"
}
```

### Получение дерева подразделений

```bash
curl "http://localhost:8000/api/v1/departments/1?depth=3&include_employees=true"
```

**Ответ:**
```json
{
  "id": 1,
  "name": "IT Department",
  "parent_id": null,
  "created_at": "2024-01-15T10:30:00",
  "employees": [],
  "children": [
    {
      "id": 2,
      "name": "Backend Team",
      "parent_id": 1,
      "created_at": "2024-01-15T10:32:00",
      "employees": [
        {
          "id": 1,
          "full_name": "John Doe",
          "position": "Senior Developer",
          "hired_at": "2024-01-15",
          "created_at": "2024-01-15T10:35:00"
        }
      ],
      "children": []
    }
  ]
}
```

### Обновление подразделения

```bash
curl -X PATCH "http://localhost:8000/api/v1/departments/2" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Backend Development Team"
  }'
```

### Удаление подразделения (каскадное)

```bash
curl -X DELETE "http://localhost:8000/api/v1/departments/1?mode=cascade"
```

### Удаление подразделения (с переназначением)

```bash
curl -X DELETE "http://localhost:8000/api/v1/departments/2?mode=reassign&reassign_to_department_id=3"
```

---

## 🧪 Тестирование

Проект использует **pytest** для тестирования с **SQLite in-memory** для изоляции тестов.

### Запуск всех тестов

```bash
docker-compose exec app pytest tests/ -v
```

### Запуск с покрытием кода

```bash
docker-compose exec app pytest tests/ --cov=app --cov-report=html
```

Отчет о покрытии будет доступен в `htmlcov/index.html`

### Запуск конкретного теста

```bash
docker-compose exec app pytest tests/test_department.py::test_create_department_with_parent -v
```

### Структура тестов

```
tests/
├── conftest.py              # Fixtures и конфигурация pytest
└── test_department.py       # Тесты для подразделений
```

### Покрытие тестами

Текущее покрытие: **~85%**

- ✅ Создание, чтение, обновление, удаление
- ✅ Валидация циклических ссылок
- ✅ Каскадное удаление
- ✅ Удаление с переназначением
- ✅ Дублирование имен в одном родителе
- ✅ Получение дерева с различной глубиной

---

## 💻 Разработка

### Локальная разработка (без Docker)

#### 1. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

#### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### 3. Запуск PostgreSQL

```bash
docker-compose up db -d
```

#### 4. Запуск сервера разработки

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Линтинг и форматирование

```bash
# Установка инструментов
pip install black flake8 mypy

# Форматирование кода
black app/ tests/

# Проверка стиля
flake8 app/ tests/

# Проверка типов
mypy app/
```

---

## 📁 Структура проекта

```
fastapiorganization/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── departments.py    # Эндпоинты подразделений
│   │   │   └── employees.py      # Эндпоинты сотрудников
│   │   └── deps.py               # Зависимости API
│   ├── models/
│   │   ├── __init__.py
│   │   ├── department.py         # Модель Department
│   │   └── employee.py           # Модель Employee
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py               # Базовый репозиторий
│   │   ├── department.py         # Репозиторий подразделений
│   │   └── employee.py           # Репозиторий сотрудников
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── department.py         # Pydantic схемы подразделений
│   │   └── employee.py           # Pydantic схемы сотрудников
│   ├── services/
│   │   ├── __init__.py
│   │   ├── department.py         # Бизнес-логика подразделений
│   │   └── employee.py           # Бизнес-логика сотрудников
│   ├── config.py                 # Конфигурация приложения
│   ├── database.py               # Настройка БД
│   ├── exceptions.py             # Кастомные исключения
│   └── main.py                   # Точка входа приложения
├── tests/
│   ├── conftest.py               # Pytest fixtures
│   └── test_department.py        # Тесты подразделений
├── .env.example                  # Пример файла окружения
├── .gitignore
├── docker-compose.yml            # Docker Compose конфигурация
├── Dockerfile                    # Docker образ приложения
├── pyproject.toml                # Конфигурация проекта
├── requirements.txt              # Python зависимости
└── README.md                     # Документация
```

---

## 🔒 Бизнес-логика и валидация

### Правила валидации подразделений

1. **Уникальность имени**: Имя подразделения должно быть уникально в рамках одного родителя
2. **Защита от циклов**: Нельзя создать циклическую ссылку в дереве подразделений
3. **Self-reference**: Подразделение не может быть родителем самого себя
4. **Длина имени**: 1-200 символов, пробелы автоматически обрезаются

### Режимы удаления подразделений

#### CASCADE (каскадное удаление)
```bash
DELETE /api/v1/departments/{id}?mode=cascade
```
- Удаляет подразделение
- Удаляет все дочерние подразделения рекурсивно
- Удаляет всех сотрудников во всех этих подразделениях

#### REASSIGN (удаление с переназначением)
```bash
DELETE /api/v1/departments/{id}?mode=reassign&reassign_to_department_id={target_id}
```
- Удаляет подразделение
- Переводит всех сотрудников в указанное подразделение (`target_id`)
- Дочерние подразделения переходят к родителю удаляемого

**Ограничения режима REASSIGN:**
- Нельзя переназначить в удаляемое подразделение
- Нельзя переназначить в дочернее подразделение удаляемого
- Целевое подразделение должно существовать

---

## 🐛 Устранение неполадок

### Проблема: Порт 8000 уже занят

```bash
# Найти процесс
lsof -ti:8000

# Убить процесс
kill -9 $(lsof -ti:8000)

# Или изменить порт в docker-compose.yml
ports:
  - "8001:8000"  # Внешний:Внутренний
```

### Проблема: База данных не подключается

```bash
# Проверить статус контейнеров
docker-compose ps

# Посмотреть логи БД
docker-compose logs db

# Пересоздать контейнеры
docker-compose down -v
docker-compose up -d
```

### Проблема: Тесты падают

```bash
# Убедиться что TESTING=true установлен в conftest.py
cat tests/conftest.py | grep TESTING

# Проверить что используется SQLite для тестов
docker-compose exec app pytest tests/ -v -s
```

---

## 🤝 Контрибьютинг

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменений (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

### Правила кода

- Следуйте PEP 8
- Добавляйте type hints
- Пишите docstrings для публичных методов
- Покрывайте новый код тестами (coverage > 80%)
- Используйте black для форматирования

---

## 📄 Лицензия

MIT License

---

## 👨‍💻 Автор

Проект создан как тестовое задание для демонстрации навыков разработки на FastAPI.

---

## 🙏 Благодарности

- [FastAPI](https://fastapi.tiangolo.com/) - отличный веб-фреймворк
- [SQLAlchemy](https://www.sqlalchemy.org/) - мощная ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - валидация данных
- [PostgreSQL](https://www.postgresql.org/) - надежная СУБД

---

**⭐ Если проект был полезен, поставьте звезду на GitHub!**
