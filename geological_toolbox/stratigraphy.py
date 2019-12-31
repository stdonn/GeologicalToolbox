# -*- coding: UTF-8 -*-
"""
This module provides a class for storing stratigraphical information in a database.
"""

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from typing import List

from geological_toolbox.exceptions import DatabaseException
from geological_toolbox.db_handler import Base, AbstractDBObject


class StratigraphicObject(Base, AbstractDBObject):
    """
    A class for storing stratigraphical information in a database.

    :param name: Name of the stratigraphic unit
    :param age: age of the stratigraphic unit (-1 if none)
    :return: nothing
    :raises ValueError: if age is not compatible to float
    """
    # define db table name and columns
    __tablename__ = "stratigraphy"

    id = sq.Column(sq.INTEGER, sq.Sequence("stratigraphy_id_seq"), primary_key=True)
    unit_name = sq.Column(sq.VARCHAR(50), unique=True)
    age = sq.Column(sq.FLOAT(), default=-1)

    def __init__(self, name: str, age: float = -1, *args, **kwargs) -> None:
        """
        Initialize a stratigraphic unit
        """
        AbstractDBObject.__init__(self, *args, **kwargs)

        try:
            age = int(age)
        except ValueError as e:
            raise ValueError("Cannot convert age to int:\n{}".format(str(e)))

        self.unit_name = str(name)
        self.age = -1 if (age < 0) else age

    def __repr__(self) -> str:
        return "<AbstractDBObject(id='{}', name='{}', age='{}')>".format(self.id, self.unit_name, self.age)

    def __str__(self) -> str:
        return "[{}]: name='{}', age='{}'".format(self.id, self.unit_name, self.age)

    # define setter and getter for columns and local data
    @property
    def horizon_age(self) -> float:
        """
        The age of the stratigraphic unit

        :raises ValueError: if new value is convertible to type int
        """
        return float(self.age)

    @horizon_age.setter
    def horizon_age(self, value: float) -> None:
        """
        See getter
        """
        try:
            value = float(value)
        except ValueError:
            raise ValueError("Cannot convert value ({}) to type int.".format(str(value)))

        if value <= 0:
            self.age = -1
        else:
            self.age = value

    @property
    def statigraphic_name(self) -> str:
        """
        The statigraphic_name of the stratigraphic unit
        """
        return self.unit_name

    @statigraphic_name.setter
    def statigraphic_name(self, value: str) -> None:
        """
        see getter
        """
        self.unit_name = str(value)

    @classmethod
    def init_stratigraphy(cls, session: Session, name: str, age: float = -1,
                          update: bool = False) -> "StratigraphicObject":
        """
        Initialize a stratigraphic unit. Create a new one if unit doesn't exists in the database, else use the existing.

        :param session: SQLAlchemy session, which includes the database connection
        :param name: Name of the stratigraphic unit
        :param age: age of the stratigraphic unit (-1 if none)
        :param update: update age if stratigraphic unit exists
        :raises ValueError: if age is not compatible to float
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        try:
            age = float(age)
        except ValueError as e:
            raise ValueError("Cannot convert age to float:\n{}".format(str(e)))

        if age < 0:
            age = -1

        # check if horizon exists (unique name)
        result = session.query(StratigraphicObject).filter(StratigraphicObject.unit_name == name)
        if result.count() == 0:  # no result found -> create new stratigraphic unit
            return cls(name, age, session=session)
        if result.count() == 1:  # one result found -> stratigr. unit exists in db -> return and possibly update
            result = result.one()
            result.session = session
            if update:  # change age value
                result.horizon_age = age
            return result

        # more than one result? => heavy failure, statigraphic_name should be unique => DatabaseException
        # for res in result.all():
        #     print(res)
        raise DatabaseException(
            "More than one ({}) horizon with the same statigraphic_name: {}! Database error!".format(result.count(), name))

    # load units from db
    @classmethod
    def load_all_from_db(cls, session: Session) -> List["StratigraphicObject"]:
        """
        Returns all stratigraphic units stored in the database connected to the SQLAlchemy Session session

        :param session: represents the database connection as SQLAlchemy Session
        :return: a list of stratigraphic units representing the result of the database query
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        result = session.query(cls).all()
        for horizon in result:  # set session value
            horizon.session = session
        return result

    @classmethod
    def load_by_stratigraphic_name_from_db(cls, name: str, session: Session) -> "StratigraphicObject" or None:
        """
        Returns the stratigraphic unit with the given name in the database connected to the SQLAlchemy Session session

        :param name: The name of the requested stratigraphic unit
        :param session: represents the database connection as SQLAlchemy Session
        :return: As the name is a unique value, only one result can be returned or None
        :raises DatabaseException: if more than one result was found (name is an unique value)
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        result = session.query(cls).filter(cls.unit_name == name)
        if result.count() == 0:
            return None
        if result.count() == 1:
            result = result.one()
            result.session = session
            return result

        raise DatabaseException("More than one ({}) horizon with the same statigraphic_name: {}! Database error!".
                                format(result.count(), name))

    @classmethod
    def load_by_age_from_db(cls, min_age: float, max_age: float, session: Session) -> List["StratigraphicObject"]:
        """
        Returns a list of stratigraphic units with an age between min_age and max_age from the database connected to
        the SQLAlchemy Session session. If no result was found, this function returns an empty list.

        :param min_age: Minimal age of the stratigraphic units
        :param max_age: Maximal age of the stratigraphic units
        :param session: represents the database connection as SQLAlchemy Session
        :return: Returns a list of stratigraphic units with an age between min_age and max_age.
        :raises ValueError: if min_age or max_age is not compatible to float
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        min_age = float(min_age)
        max_age = float(max_age)
        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        result = session.query(cls).filter(sq.between(cls.age, min_age, max_age)).all()
        for horizon in result:
            horizon.session = session
        return result
