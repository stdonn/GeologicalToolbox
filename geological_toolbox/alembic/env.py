# -*- coding: UTF-8 -*-
import inspect
import os
import sys

from alembic import context
from importlib.machinery import SourceFileLoader
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))  # script directory
lib_path = os.path.abspath(os.path.join(local_dir, ".."))
sys.path.append(lib_path)
DBObjects_mod = SourceFileLoader("DatabaseObjects", os.path.join(lib_path, "database_objects.py")).load_module()

config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = DBObjects_mod.Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    # session = DBHandler(connection=url).create_new_session()
    # session.close()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        sqlalchemy_module_prefix="sq.",
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    ini_section = config.get_section(config.config_ini_section)
    db_url = context.get_x_argument(as_dictionary=True).get('db_url')
    if db_url:
        ini_section['sqlalchemy.url'] = db_url

    connectable = engine_from_config(
        ini_section,
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            sqlalchemy_module_prefix="sq.",
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
