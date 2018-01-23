# -*- coding: UTF-8 -*-
"""
This module provides a class for storing stratigraphical information in a database.
"""

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from typing import List

from GeologicalToolbox.Exceptions import DatabaseException
from GeologicalToolbox.DBHandler import Base


class StratigraphicObject(Base):
    """
    A class for storing stratigraphical information in a database.
    """
    # define db table name and columns
    __tablename__ = 'stratigraphy'

    id = sq.Column(sq.INTEGER, sq.Sequence('strat_id_seq'), primary_key=True)
    unit_name = sq.Column(sq.VARCHAR(50), unique=True)
    age = sq.Column(sq.FLOAT(), default=-1)

    def __init__(self, session, name, age=-1):
        # type: (Session, str, float) -> None
        """
        Initialize a stratigraphic unit

        :param session: SQLAlchemy session, which includes the database connection
        :type session: Session
        :param name: Name of the stratigraphic unit
        :type name: str
        :param age: age of the stratigraphic unit (-1 if none)
        :type age: float
        :return: nothing
        :raises ValueError: if age is not compatible to float
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        try:
            age = int(age)
        except ValueError as e:
            raise ValueError("Cannot convert age to int:\n{}".format(str(e)))

        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        self.__session = session
        self.unit_name = str(name)
        self.age = -1 if (age < 0) else age

    def __repr__(self):
        # type: () -> str
        """
        Returns a text-representation of the AbstractDBObject

        :return: Returns a text-representation of the AbstractDBObject
        :rtype: str
        """
        return "<AbstractDBObject(id='{}', name='{}', age='{}')>".format(self.id, self.unit_name, self.age)

    def __str__(self):
        # type: () -> str
        """
        Returns a text-representation of the AbstractDBObject

        :return: Returns a text-representation of the AbstractDBObject
        :rtype: str
        """
        return "[{}]: name='{}', age='{}'".format(self.id, self.unit_name, self.age)

    # define setter and getter for columns and local data
    @property
    def horizon_age(self):
        # type: () -> float
        """
        The age of the stratigraphic unit

        :type: float
        :raises ValueError: if new value is convertible to type int
        """
        return float(self.age)

    @horizon_age.setter
    def horizon_age(self, value):
        # type: (float) -> None
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
    def name(self):
        # type: () -> str
        """
        The name of the stratigraphic unit

        :type: str
        """
        return self.unit_name

    @name.setter
    def name(self, value):
        # type: (str) -> None
        """
        see getter
        """
        self.unit_name = str(value)

    @property
    def session(self):
        # type: () -> Session
        """
        The current Session object

        :type: Session
        :raises TypeError: if new value is not of an instance of Session
        """
        return self.__session

    @session.setter
    def session(self, value):
        # type: (Session) -> None
        """
        see getter
        """
        if not isinstance(value, Session):
            raise TypeError("Value is not of type {} (it is {})!".format(Session, type(value)))

        self.__session = value

    def save_to_db(self):
        # type: () -> None
        """
        Saves all changes of the line or the line itself to the connected database

        :return: Nothing
        :raises IntegrityError: if the commit to the database fails and rolls all changes back
        """
        self.__session.add(self)
        try:
            self.__session.commit()
        except IntegrityError as e:
            # Failure during database processing? -> rollback changes and raise error again
            raise IntegrityError(
                    'Cannot commit changes in stratigraphy table, Integrity Error (double unique values?) -- {} -- ' +
                    'Rolling back changes...'.format(e.statement), e.params, e.orig, e.connection_invalidated)

    @classmethod
    def init_stratigraphy(cls, session, name, age=-1, update=False):
        # type: (Session, str, float, bool) -> cls
        """
        Initialize a stratigraphic unit. Create a new one if unit doesn't exists in the database, else use the existing.

        :param session: SQLAlchemy session, which includes the database connection
        :type session: Session
        :param name: Name of the stratigraphic unit
        :type name: str
        :param age: age of the stratigraphic unit (-1 if none)
        :type age: float
        :param update: update age if stratigraphic unit exists
        :type update: bool
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
            return cls(session, name, age)
        if result.count() == 1:  # one result found -> stratigr. unit exists in db -> return and possibly update
            result = result.one()
            result.session = session
            if update:  # change age value
                result.horizon_age = age
            return result

        # more than one result? => heavy failure, name should be unique => DatabaseException
        for res in result.all():
            print(res)
        raise DatabaseException(
                'More than one ({}) horizon with the same name: {}! Database error!'.format(result.count(), name))

    # load units from db
    @classmethod
    def load_all_from_db(cls, session):
        # type: (Session) -> List[StratigraphicObject]
        """
        Returns all stratigraphic units stored in the database connected to the SQLAlchemy Session session

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session
        :return: a list of stratigraphic units representing the result of the database query
        :rtype: List[StratigraphicObject]
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        result = session.query(cls).all()
        for horizon in result:  # set session value
            horizon.session = session
        return result

    @classmethod
    def load_by_name_from_db(cls, name, session):
        # type: (str, Session) -> StratigraphicObject
        """
        Returns the stratigraphic unit with the given name in the database connected to the SQLAlchemy Session session

        :param name: The name of the requested stratigraphic unit
        :type name: str
        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session
        :return: As the name is a unique value, only one result can be returned or None
        :rtype: StratigraphicObject or None
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

        raise DatabaseException('More than one ({}) horizon with the same name: {}! Database error!'.
                                format(result.count(), name))

    @classmethod
    def load_by_age_from_db(cls, min_age, max_age, session):
        # type: (float, float, Session) -> List[StratigraphicObject]
        """
        Returns a list of stratigraphic units with an age between min_age and max_age from the database connected to
        the SQLAlchemy Session session. If no result was found, this function returns an empty list.

        :param min_age: Minimal age of the stratigraphic units
        :type min_age: float
        :param max_age: Maximal age of the stratigraphic units
        :type max_age: float
        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session
        :return: Returns a list of stratigraphic units with an age between min_age and max_age.
        :rtype: List[StratigraphicObject]
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
