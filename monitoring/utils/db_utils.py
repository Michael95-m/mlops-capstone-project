from typing import Callable

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import sessionmaker


def open_sqa_session(engine) -> sqlalchemy.orm.Session:
    """Open SQLAlchemy session.

    Args:
        engine (sqlalchemy.engine): SQLAlchemy engine.

    Returns:
        sqlalchemy.orm.Session: class Session.
    """

    Session = sessionmaker(bind=engine)
    session = Session()
    return session