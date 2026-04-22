from sqlalchemy.orm import DeclarativeBase
from typing import TypeVar


ORMOBJECT = TypeVar('T', bound=DeclarativeBase)