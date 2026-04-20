from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config.log import create_logger


logger = create_logger()


class Connection:
    def __init__(self):
        self.host = getenv("DB_HOST", "localhost")
        self.port = getenv("DB_PORT", 5432)
        self.user = getenv("DB_USER", "postgres")
        self.password = getenv("DB_PASSWORD", "pwd")
        self.database = getenv("DB_DATABASE", "postgres")
        self.engine = None
        self.SessionFactory = None

    def __enter__(self):
        logger.info("Criando engine para a conexão com o DB")
        try:
            self.engine = \
            create_engine(
                f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}",
                pool_pre_ping=True
            )
        except Exception as ex:
            logger.error("Erro ao criar engine para a conexão com o DB:\n{}".format(ex))

        logger.info("Conexão com o DB criada")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Fechando conexão com o DB")
        self.engine.dispose()
