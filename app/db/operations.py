from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from typing import Any, Optional, TypeVar

from sqlalchemy.engine.result import Result
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.util.types import ORMOBJECT


T = TypeVar("T")
Mapper = Callable[[Result], T]

log = logging.getLogger(__name__)


def _execute(session: Session, sql: Select) -> Result:
    """Run the statement and return the raw Result."""
    log.debug("Executing %s", sql)
    return session.execute(sql)


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


def insert_list(session: Session, list_items: list[ORMOBJECT]) -> list[ORMOBJECT]:
    session.add_all(list_items)
    session.commit()
    for item in list_items:
        session.refresh(item)
    return


def insert_item(session: Session, item: ORMOBJECT) -> ORMOBJECT:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
