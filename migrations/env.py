import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import find_dotenv
from dotenv import load_dotenv
from pydantic.networks import PostgresDsn
from sqlalchemy import pool
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.api.utils.enums.env_enum import EnvEnum

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


load_dotenv(find_dotenv())
config = context.config
environment = os.getenv("ENVIRONMENT")


if environment == EnvEnum.PYTEST.value:
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_SQLALCHEMY_DATABASE_URI","")
else:
    SQLALCHEMY_DATABASE_URI = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        path=os.getenv("POSTGRES_DB", "")
    )
    SQLALCHEMY_DATABASE_URI = str(SQLALCHEMY_DATABASE_URI)

config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URI)
fileConfig(config.config_file_name)

from app.db.enabled_migration_models import BaseDBModel

target_metadata = BaseDBModel.metadata

# FIXME Схема текущего проекта.
schema = "template_schema"



def include_object(object, name, type_, reflected, compare_to):
    """Вызываемая функция, которой предоставляется возможность вернуть True или False
    для любого объекта, указывая, должен ли данный объект учитываться при автогенерации.
    https://alembic.sqlalchemy.org/en/latest/api/runtime.html
    #alembic.runtime.environment.EnvironmentContext.configure.params.include_object.

    Args:
        object: объект SchemaItem, такой, как объект Table, Column,
            Index UniqueConstraint или ForeignKeyConstraint
        name: имя объекта. Обычно оно доступно через object.name
        type_: строка, описывающая тип объекта; в настоящее время
            "table", "column", "index", "unique_constraint", "foreign_key_constraint"
        reflected: True, если данный объект был создан на основе отражения таблицы,
            False, если он получен из локального объекта MetaData.
        compare_to: объект, c которым сравнивается, если доступен, иначе None
    """
    if type_ == "table" and object.schema != schema:
        return False

    # He добавляем рефлексивные колонки
    if type_ == "column" and not reflected:
        return False

    return True


def include_name(name, type_, parent_names):
    """Вызываемая функция, которой предоставляется возможность возвращать True или False
    для любого отраженного объекта базы данных на основе ero имени,
    включая имена схем баз данных
    https://alembic.sqlalchemy.org/en/latest/api/runtime.html
    #alembic.runtime.environment.EnvironmentContext.configure.params.include_name.

    Args:
        name: имя объекта, например, имя схемы или имя таблицы.
            Будет равно None при указании имени схемы по умолчанию
            для подключения к базе данных
        type_: строка, описывающая тип объекта; в настоящее время
            "schema", "table", "column", "index", "unique_constraint"
             или "foreign_key_constraint"
        parent_names:
            словарь имен "родительских" объектов, которые являются относительными
            по отношению к задаваемому имени. Ключи в этом словаре
            могут включать: "имя_схемы", "имя_таблицы".

    Returns:

    """
    if type_ == "schema":
        # this **will* include the default schema
        return name in [schema]
    return True


def process_revision_directives(context, revision, directives):
    """Вызываемая функция, которой будет передана структура, представляющая конечный
    результат операции автогенерации или простой операции "ревизии". Ей можно
    манипулировать, чтобы повлиять на то, как команда alembic revision в
    конечном итоге выводит новые скрипты ревизии.

    https://alembic.sqlalchemy.org/en/latest/api/runtime.html#alembic.runtime.
    environment.EnvironmentContext.configure.params.process_revision_directives

    Args:
        context: это используемый MigrationContext
            https://alembic.sqlalchemy.org/en/latest/api/runtime.html
            #alembic.runtime.migration.MigrationContext
        revision: кортеж идентификаторов ревизий, представляющих текущую
            ревизию базы данных
        directives: Параметр directives представляет собой список Python, содержащий
            одну директиву MigrationScript и представляет файл ревизии,
            который должен быть сгенерирован. Этот список, a также ero содержимое
            можно свободно изменять для создания любого набора команд.
            B разделе Настройка генерации ревизий показан пример такой настройки.
            https://alembic.sqlalchemy.org/en/latest/api/autogenerate.html
            #customizing-revision
    """
    # Этот код нужен для тестирования алембик миграций
    if config.cmd_opts.autogenerate:
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []


def run_migrations_offline() -> None:
    """Запуск миграции в оффлайн режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        echo=True,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Запуск миграции в онлайн режиме."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        version_table_schema=schema,
        include_name=include_name,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Нужно для тестов т.к. версия алембика хранится именно там
        await connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        await connection.commit()

        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
