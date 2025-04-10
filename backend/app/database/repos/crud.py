from typing import Generic, TypeVar
from abc import ABC, abstractmethod
from sqlalchemy import select, delete, update
from .base import BaseRepository

T = TypeVar('T')


class CRUDRepository(BaseRepository, Generic[T], ABC):
    @property
    @abstractmethod
    def entry_class(self) -> type[T]:
        raise NotImplementedError

    def create(self, **kwargs) -> T:
        obj = self.entry_class(**kwargs)
        with self.Session() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
        return obj

    def get(self, id: int) -> T | None:
        with self.Session() as session:
            return session.get(self.entry_class, id)

    def get_all(self) -> list[T]:
        stmt = select(self.entry_class)
        with self.Session() as session:
            return list(session.scalars(stmt).all())

    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if obj:
            with self.Session() as session:
                session.delete(obj)
                session.commit()
                return True
        return False

    def delete_by(self, **kwargs) -> int:
        stmt = delete(self.entry_class).filter_by(**kwargs)
        with self.Session() as session:
            result = session.execute(stmt)
            session.commit()
            return result.rowcount

    def update(self, id: int, **kwargs) -> int:
        stmt = update(self.entry_class).where(self.entry_class.id == id).values(**kwargs)
        with self.Session() as session:
            result = session.execute(stmt)
            session.commit()
            return result.rowcount

    def update_by(self, filter_by: dict, update_by: dict) -> int:
        stmt = update(self.entry_class).filter_by(**filter_by).values(**update_by)
        with self.Session() as session:
            result = session.execute(stmt)
            session.commit()
            return result.rowcount

    def filter_by(self, **kwargs) -> list[T]:
        stmt = select(self.entry_class).filter_by(**kwargs)
        with self.Session() as session:
            return list(session.scalars(stmt).all())

    def get_first(self, **kwargs) -> T | None:
        stmt = select(self.entry_class).filter_by(**kwargs)
        with self.Session() as session:
            return session.scalars(stmt).first()

