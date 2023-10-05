# Template service v2

----------------------

#### [О структуре шаблона](./ABOUT.md)

> В этой секции стоит дать общее описание проекта (что за проект, основное назначение,
> тезисно функционал и др.)

Сервис используется как шаблонный для создания других сервисов.

## Основной функционал:

> В этом блоке описываем все, что делает сервис:
> Например:
> - Сбор постов по RSS фидам
> - Обновление даты последнего парсинга источника

## Алгоритм работы:

> В этой секции описываем основную логику работы приложения.
> ### Например:
> Сервис используется как шаблонный сервис.
> В нем реализованы основные методологии, используемые в остальных сервисах.
> - базовый круд
> - пример контроллеров
> - пример тестов (интеграционных и юнитов)
> - и тд. что необходимо знать разработчику, впервые сталкивающимся с текущим проектом

# 1. Установка

## При **первом** запуске необходимо:

Настроить переменные окружения: 

#### **Вариант 1** Создать файл `.env` в корне проекта:

```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=example
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres

ENVIRONMENT=local
TEST_SQLALCHEMY_DATABASE_URI="postgresql+asyncpg://postgres:example@localhost:5432/test"
```
#### **Вариант 2** Переименовать файл .env.example в .env


### Описание возможных ENV параметров

> Тут указываем все настройки, которые приложение использует для работы.

| Name                           | Description                     | Default value     |
|--------------------------------|---------------------------------|-------------------|
| `POSTGRES_USER`                | Пользователь PG                 | `user`            |
| `POSTGRES_PASSWORD`            | Пароль PG                       | `None`            |
| `POSTGRES_HOST`                | PG хост                         | `localhost`       |
| `POSTGRES_PORT`                | PG порт                         | `5432`            |
| `POSTGRES_DB`                  | Имя БД PG                       | `None`            |
| `ENVIRONMENT`                  | Наименование текущего окружения | `None`            |
| `TEST_SQLALCHEMY_DATABASE_URI` | URI для тестовой бд             | `3003`            |             
| `PROJECT_NAME`                 | Название проекта                | `example project` |             
| `LOG_LEVEL`                    | Уровень логов                   | `INFO`            |             

# 2. Запуск проекта:

## 2.1. С помощью докера

> Создаем docker-compose.yml и описываем в нем профили запуска. Пример лежит в проекте

Запуск возможен в 6-и вариациях:

- `docker compose up` - запуск только текущего сервиса;
- `docker compose --profile stack up -d --scale template_service=0` - запуск только стека;
- `docker compose --profile postgres up` - запуск сервиса + postgresql;
- `docker compose --profile mongodb up` - запуск сервиса + mongo;
- `docker compose --profile kafka up` - запуск сервиса + kafka + kafka_ui;
- `docker compose --profile all up` - запуск сервиса + mongo + postgresql;

> флаг `--build` перебилдит текущий проект

## 2.2. Запуск без докера 

Ставим флаг `poetry config virtualenvs.in-project true`, если хотим создавать .venv в
текущей папки проекта (опционально)

- Устанавливаем зависимости `poetry install`;
- Ставим `pre-commit install` для линта кода;
- Запускам миграции `alembic` командой `alembic -x data=true upgrade head`;
- Запускаем стек `docker compose --profile stack up -d --scale template_service=0`;
- Запускаем приложение `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`;

# 3. Использование

## 3.1 Запуск тестов

> Здесь можно указывать все, что связано с тестами. Допустим указать параметры для
> пропуска "долгих" тестов, какие тесты отключены и почему и тд

```bash
pytest --maxfail=1 --cov=app -vv --cov-config .coveragerc
```

```bash
docker-compose exec template_service pytest --maxfail=1 --cov=app  -vv --cov-config .coveragerc
```

Пропуск "долгих" тестов:

```bash
pytest --maxfail=1 --cov=app -vv --cov-config .coveragerc -m "not long"
```

## 3.2 Линтеры

> Блок с линтерами. Идейно пока хватает pre-commit, но мало ли что.

Запуск линтеров по всему проекту:

```bash
pre-commit run --all-files
```

## 3.3 Миграции

> Блок с алембиком (если он нужен)

- `alembic revision --autogenerate -m "message"` - генерация новой миграции
- `alembic upgrade head` - накат миграций
- `alembic -x data=true upgrade head ` - накат миграций вместе с данными. Выполняется
  функция data_upgrades() в файле миграции
- `alembic upgrade head --sql > migration.sql` - генерация SQL файла с миграциями.
- `alembic downgrade -1` - откат миграции на 1 версию назад

# 4. Дополнительная информация

> В этом блоке указываем дополнительную информацию, которую сложно структурировать по
> существующим блокам

> В ключевых местах проекта оставлены теги *FIXME*.

## 4.1 Для работы с новым проектом необходимо:

### 1. "Чистка" текущего проекта:

- Удалить все миграции из папки `migrations/versions`;
- Удалить все модели из папки `app/v1/models`;
- Удалить все контроллеры из папки `app/v1/controllers`;
- Удалить лишние импорты и роуты из `app/v1/__init__py`;
- Удалить файлы `role_schema.py` и `user_schema.py` из папки `app/v1/controllers`;
- Удалить файлы `role_crud.py` и `user_crud.py` из папки `app/v1/crud`;
- Удалить все тесты в папке `app/tests/api/v1`

### 2. Настройка проекта:

#### 2.1 Настройка миграций и моделей:

Если планируется использовать Alembic и SQLAlchemy:

- в файле `migrations/env.py` прописываем `schema = "Используемая схема"`
- описать модели и импортировать их в файл `app/api/db/enabled_migrations_models.py` для
  включения этих моделей в миграции

Если алембик и SQLAlchemy использовать не планируется:

- Выпиливаем зависимости `poetry remove alembic sqlalchemy`
- Удаляем файл `alembic.ini`
- Удаляем папку `migrations`
- Удаляем папку `app/api/db`
- Удаляем папки `app/api/v1/crud` и `app/api/v1/models`
- Удаляем из `app/tests/conftest.py` все фикстуры, использующие БД

### 2.2 Настройка переменных окружения

Все настройки проекта находятся в файле `app/config.py`. Конфигурация автоматически
собирает переменные из окружения. Для валидации конфига
используется `pydantic.BaseSettings` https://docs.pydantic.dev/usage/settings/

### 3. Тестирование проекта

По умолчанию подключено:

- Тесты миграций (файл `app/tests/api/utils/test_migrations`).
  test_up_down_consistency() является довольно медленным тестом при большом количестве
  миграций;
- Тестовый клиент fastapi переведен на асинхронный движок (`httpx`);
- Тест хелсчека
- Все тесты по умолчанию интеграционные, т.е. используется тестовая БД.
- Каждый тестовый класс получает "чистое" состояние бд, если необходимо задать состояние
  для тестового класса, посмотри пример в файле `test_user_controller.py`

### 4. Подготовка проекта к деплою

Чтобы merge пайплайн прошел, необходимо перенести нужные для тестирования env настройки
в `.gitlab-ci.yml` файл.

```yaml
.vars:
  variables:
    # Сюда пишем необходимые переменные для запуска тестов на уровне пайплайнов гитлаба
    TEST_SQLALCHEMY_DATABASE_URI: postgresql+asyncpg://postgres@postgres:5432/postgres
    ENVIRONMENT: PYTEST
    POSTGRES_HOST_AUTH_METHOD: trust # сюда можно прописать свои переменные окружения
```

## 4.2 Важные дополнения

### BaseDBModel

Все модели стоит наследовать от `app/api/db/base_class.py:BaseDBModel`, т.к.
базовый класс легче расширять

### BaseENUM

Все ENUM стоит так же наследовать от `app/api/utils/enums/base_enum.py:BaseENUM`.

### BaseSchema

Все схемы Pydantic так же стоит наследовать
от `app/api/v1/schemas/base_schema.py:BaseSchema`. В ней по умолчанию прописаны
корректная работа с datetime, указан декодер по умолчанию

### PGEngineConnector

Новая реализация класса коннектора для пг. Решает 4 проблемы:

- Коннектор поддерживает несколько engine соединений
- Изоляция соединения. Оно теперь спрятано в скоуп класса
- Один URI содержит общий пул соединений в пострес
- При тестировании приложения не возникает циркулярных импортов


### Работа через cli.py

`cli.py` это удобный способ разработки через консольные команды.
Идея заключается в том, что какие-то действия, к примеру
написание сложных запросов в SQLAlchemy, Вы изолируете от контекста 
их выполнения (конечной функции). 

Ближайшим аналогом такого подхода является test-driven-development
и, фактически, те скрипты, которые вы используете для отладки тех или иных
действий потом можно скопировать в будущий тест.  


Начало работы с `cli.py`: 

> Скопируйте содержимое папки `cli.example` в корневой каталог микросервиса.

> Проверьте работу командой
``` sh
python cli.py cli.hello "hello_stranger()"
```

Список команд:
``` sh
python cli.py cli.hello "hello_stranger()" # проверить что cli.py работает
python cli.py cli.db "create_role()" # создать роль
python cli.py cli.db "get_role()" # получить роль
python cli.py cli.produce "ping_pong_produce()" # отправить сообщение в топик ping_pong
python cli.py cli.consume "ping_pong_consume()" # подписаться на топик ping_pong
```

### Работа c Makefile

`Makefile` это удобный способ назначать короткие 
для запоминания имена для "длинных" команд.

Допустим у Вас есть команда `alembic upgrade head`, 
которая применяет миграцию.  

Вы можете назначить ей удобное короткое, 
для запоминания имя в файле `Makefile`:
``` sh
migrate:
	alembic upgrade head
```

Теперь Вам достаточно ввести в консоли:
``` sh
make migrate
```

Искомая команда будет выполнена.


#### Отправить http запрос через Swagger
Для отправки http запроса Вам необходимо сделать 
`port-forwarding` с помощью приложения `Lens`.
Для этого Вам необходимо найти данный микросервис
в списке доступных подов (namespace `k8s-dev`).
После щщелчка на данный микросервис в общем списке
Вы увидите окно c опциями пода.
Здесь Вам необходимо найти опцию `Ports` и 
щщелкнуть по значению `3000:3000`
В окне вашего браузера будет открыт сваггер данного микросервиса.  

#### Отправить тестовые данные через топик ping_pong
Данный микросервис читает информацию из топика
`ping_pong`.

Сюда можно отправить сообщение:
``` json
{"ping": 11, "pong": 12}

```
Искомое сообщение будет записано в базу данных.


### Переезд микросервисов на Pydantic2 
#TODO удалить

Для переезда на `Pydantic2` Вам необходимо в файле 
pyproject.toml указать следующие зависимости:  
``` python
fastapi = { extras = ["all"], version = "0.100.0" }
pydantic-settings = "^2.0.2"
```
Далее необходимо перейти в консоль и выполнить следующие команды:  
``` sh
poetry shell 
poetry update
pip install 
pip install bump-pydantic
bump-pydantic app
```

Вы должны увидеть сообщение о том, что код Вашего микросервиса
успешно отредактирован скриптом миграции на `Pydantic2`.  

Далее Вам необходимо произвести рефакторинг файла `app/config.py` 
Вашего микросервиса в соответствии с файлом
`app/config.py` данного микросервиса (`template_service`).
