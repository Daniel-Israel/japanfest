from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Optional, TypeVar, List

from sqlalchemy.engine.result import Result
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from sqlalchemy.exc import SQLAlchemyError

from app.config.log import create_logger


T = TypeVar("T")
Mapper = Callable[[Result], T]

log = create_logger()


def _execute(session: Session, sql: Select) -> Result:
    """Run the statement and return the raw Result."""
    log.info("Executing %s", sql)
    return session.execute(sql)


def _do_insert(session: Session, items: Sequence[T]) -> List[T]:

    log.info("Inserting %d objects into %s", len(items), session.bind)
    
    try:
        session.add_all(items)
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        log.exception("Failed to insert; transaction rolled back")
        raise

    for item in items:
        session.refresh(item)

    return items


def select_one(session: Session, sql: Select) -> Optional[dict]:
    return _execute(session, sql).mappings().first()


def select_many(session: Session, sql: Select) -> Sequence[Any]:
    return _execute(session, sql).all()


def select_one_with(
    session: Session,
    sql: Select,
    *,
    mapper: Mapper[T] = lambda r: r.mappings().first(),
) -> Optional[T]:
    return mapper(_execute(session, sql))


def select_many_with(
    session: Session,
    sql: Select,
    *,
    mapper: Mapper[T] = lambda r: r.all(),
) -> Sequence[T]:
    return mapper(_execute(session, sql))
