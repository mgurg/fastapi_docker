from typing import Any, Generic, TypeVar

from sqlalchemy import and_, select, update
from sqlalchemy.orm import Session

from app.models.models import BaseModel

T = TypeVar("T", bound=BaseModel)


# save
# saveAll
# findById
# existsById
# findAll
# findAllById
# count
# deleteById
# delete
# deleteAllById
# deleteAll
# deleteAll


class GenericRepo(Generic[T]):
    def __init__(self, session: Session, model: type[T]):
        """
        Initializes the repository with the given session and model.

        :param session: The SQLAlchemy session to use.
        :param model: The SQLAlchemy model to use.
        """
        self.session = session
        self.model = model

    def get_all(self) -> list[T]:
        """
        Retrieves all objects from the database.

        :return: A list of all objects of the model type.
        """
        result = self.session.execute(select(self.model))
        return result.scalars().all()

    def get_by_id(self, id: int) -> T | None:
        """
        Retrieves an object by its ID.

        :param id: The ID of the object to retrieve.
        :return: The object if found, None otherwise.
        """
        result = self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    def create(self, **kwargs: dict[str, Any]) -> T:
        """
        Creates a new object with the given keyword arguments.

        :param kwargs: The keyword arguments to use for creating the object.
        :return: The newly created object.
        """
        obj = self.model(**kwargs)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)

        return obj

    def create_all(self, data_list: list[dict[str, Any]]) -> None:
        # created_items = []
        for user_data in data_list:
            obj = self.model(**user_data)
            self.session.add(obj)
            # created_items.append(obj)
        self.session.commit()


    def update(self, id: int, **kwargs: dict[str, Any]) -> None:
        """
        Updates an object with the given ID and keyword arguments.

        :param id: The ID of the object to update.
        :param kwargs: The keyword arguments to use for updating the object.

        Returns:
            object:
        """
        self.session.execute(update(self.model).where(self.model.id == id).values(**kwargs))
        self.session.commit()


    def delete(self, id: int) -> T | None:
        """
        Deletes an object by its ID.

        :param id: The ID of the object to delete.
        :return: The deleted object if found, None otherwise.
        """
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj


    def filter(self, page: int = 1, per_page: int = 10, **kwargs: dict[str, Any]) -> list[T]:
        """
        Filters objects based on the given keyword arguments and paginate the result.

        :param page: The page number to retrieve.
        :param per_page: The number of items per page.
        :param kwargs: The keyword arguments to use for filtering the objects.
        :return: A list of objects that match the filter criteria.
        """
        offset = (page) * per_page
        filters = [getattr(self.model, k) == v for k, v in kwargs.items()]
        query = select(self.model).where(and_(*filters)).limit(per_page).offset(offset)
        result = self.session.execute(query)
        return result.scalars().all()
