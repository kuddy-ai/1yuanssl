"""Alembic 环境配置"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 导入模型
from app.config import settings
from app.db.session import Base
from app.models import (  # noqa: F401
    AcmeChallenge,
    CertificateFile,
    CertificateOrder,
    DeploymentTarget,
)

# Alembic Config 对象
config = context.config

# 设置数据库 URL（从环境变量；测试可通过 config.attributes 覆盖）
database_url = config.attributes.get("database_url", settings.DATABASE_URL)
config.set_main_option("sqlalchemy.url", database_url)

# 日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData 对象（用于 autogenerate）
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    离线模式运行迁移
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    在线模式运行迁移（支持 SQLAlchemy async URL）
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
