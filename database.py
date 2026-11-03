from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session


DATABASE_URL = "mysql+pymysql://root:PKcJ5JfU@127.0.0.1/DriverKarma"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = Session(engine)

    try:
        yield db
    finally:
        db.close()
