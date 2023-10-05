# Делаем свой базовый образ с установкой переменных окружения
FROM python:3.11-slim as base-image

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    # переопределяем стандартное расположение poetry, чтобы в дальнейшем использовать
    POETRY_HOME="/opt/poetry" \
    # создаст venv в PROJECT_PATH
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.5.0 \
    PROJECT_PATH="/app"

ENV PATH="$POETRY_HOME/bin:$PATH"

################################################################
# Установка всех зависимостей
FROM base-image as build-image
RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc build-essential curl && rm -rf /var/lib/apt/lists/*

RUN mkdir -m 777 /app
WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry install --no-dev

##############################################################
# Образ для разработки
FROM base-image AS development-image
ENV PRODUCTION=False
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential curl && rm -rf /var/lib/apt/lists/* && \
    groupadd --gid 2000 user && useradd --uid 2000 --gid user --shell /bin/bash --create-home user

COPY --from=build-image --chown=user:user $PROJECT_PATH $PROJECT_PATH
COPY --from=build-image --chown=user:user $POETRY_HOME $POETRY_HOME

WORKDIR $PROJECT_PATH
RUN poetry install

COPY --chown=user:user ./app /app/app
# Копируем файлы необходимые для миграций с помощью alembic
COPY --chown=user:user ./alembic.ini /app/
COPY --chown=user:user ./migrations /app/migrations

# Установим утилиту wait-for-it.sh с помощью которой можно ждать сервис пока он не
# начнет работать на каком-то порту. Полезно при работе с postgres во время накатывания
# миграций.
RUN curl -o /usr/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x /usr/bin/wait-for-it.sh

USER user
CMD [".venv/bin/uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "3000"]


##############################################################
# Образ для production: не ставятся dev зависимости, uvicorn запускается без hot reload
FROM base-image AS production-image
ENV PRODUCTION=True
RUN groupadd --gid 2000 user && useradd --uid 2000 --gid user --shell /bin/bash --create-home user

COPY --from=build-image --chown=user:user $PROJECT_PATH $PROJECT_PATH
COPY --from=build-image --chown=user:user /app/.venv /app/
COPY --chown=user:user ./app /app/app

USER user

WORKDIR $PROJECT_PATH
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]


##############################################################
# Образ для накатывания миграций алембиком
FROM development-image AS alembic-image
CMD [".venv/bin/alembic", "-c", "./alembic.ini", "-x", "data=true", "upgrade", "head"]
