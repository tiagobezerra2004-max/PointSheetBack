import logging

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class DatabaseUnavailable(Exception):
    """Indica que a verificação de disponibilidade do banco falhou."""


def create_database_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)


engine = create_database_engine()


def check_database_connection() -> None:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        logger.warning("Falha na verificação do banco (%s).", type(error).__name__)
        raise DatabaseUnavailable from error
