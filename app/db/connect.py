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


    def connect(self):
        logger.info("Criando engine para a conexão com o DB")
        
        self.engine = create_engine(
            f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}",
            pool_pre_ping=True
        )
        self.SessionFactory = sessionmaker(bind=self.engine)
        logger.info("Conexão com o DB criada")


    def disconnect(self):
        logger.info("Fechando conexão com o DB")
        self.engine.dispose()


    def get_session(self) -> Session:
        return self.SessionFactory()

db = Connection()

def get_session():
    session = db.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()