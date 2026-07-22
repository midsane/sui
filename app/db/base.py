# we move from engine -> session -> base
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
