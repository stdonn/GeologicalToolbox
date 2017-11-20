# -*- coding: UTF-8 -*-
"""
This module provides a class for database access through an SQLAlchemy session and the base class for all database
    related classes.
"""

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

Base = declarative_base()


class DBHandler:
    """
    A class for database access through an SQLAlchemy session.
    """

    def __init__(self, connection='sqlite:///:memory:', debug=False):
        # type: (str, bool) -> None
        """
        Initialize a new database connection via SQLAlchemy

        :param connection: Connection uri to a database, format defined by SQLAlchemy
        :type connection: str

        :param debug: enable debug output for database access (default False)
        :type debug: bool

        :return: Nothing
        """
        engine = sq.create_engine(connection, echo=debug)
        Base.metadata.create_all(engine)
        self.__Session = sessionmaker(bind=engine)

    def get_session(self):
        # type: () -> sessionmaker
        """
        Returns the a session for the current database connection

        :return: Returns the a session for the current database connection
        """
        return self.__Session()


class DBObject:
    """
    This class represents the base class for all database objects
    """
    comment_col = sq.Column(sq.VARCHAR(100), default="")

    def __init__(self, session, comment):
        # type: (Session, str) -> None
        """
        Initialises the class

        :param session: session object create by SQLAlchemy sessionmaker
        :type session: Session

        :param comment: additional comment
        :type comment: str

        :return: Nothing
        :raises ValueError: Raises ValueError if a type conflict is recognised
        """
        if not isinstance(session, Session):
            raise ValueError("'session' value is not of type SQLAlchemy Session!")

        self.__session = session
        self.comment = comment

    @property
    def comment(self):
        # type: () -> str
        """
        Returns the additional comments for the well marker.

        :return: Returns the additional comments for the well marker.
        :rtype: str
        """
        return self.comment_col

    @comment.setter
    def comment(self, comment):
        # type: (str) -> None
        """
        Sets an additional comments for the well marker

        :param comment: additional comment
        :type comment: str

        :return: Nothing
        """
        comment = str(comment)
        if len(comment) > 100:
            comment = comment[:100]
        self.comment_col = comment

    @property
    def session(self):
        # type: () -> Session
        """
        Return the current Session object

        :return: returns the current Session object, which represents the connection to a database
        :rtype: Session
        """
        return self.__session

    @session.setter
    def session(self, session):
        # type: (Session) -> None
        """
        Sets a new session, which represents the connection to a database

        :param session: session object create by SQLAlchemy sessionmaker
        :type session: Session

        :return: Nothing

        :raises TypeError: Raises TypeError if session is not of an instance of Session
        """

        if not isinstance(session, Session):
            raise TypeError("Value is not of type {} (it is {})!".format(Session, type(session)))
        self.__session = session

    # save point to db / update point
    def save_to_db(self):
        # type: () -> None
        """
        Saves all changes of the well marker to the database

        :return: Nothing

        :raises IntegrityError: raises IntegrityError if the commit to the database fails and rolls all changes back
        """
        self.__session.add(self)
        try:
            self.__session.commit()
        except IntegrityError as e:
            # Failure during database processing? -> rollback changes and raise error again
            self.__session.rollback()
            raise IntegrityError(
                    'Cannot commit changes in geopoints table, Integrity Error (double unique values?) -- {} -- ' +
                    'Rolling back changes...'.format(e.statement), e.params, e.orig, e.connection_invalidated)

    # load points from db
    @classmethod
    def load_all_from_db(cls, session):
        # type: (Session) -> List[WellMarker]
        """
        Returns all well marker in the database connected to the SQLAlchemy Session session

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session

        :return: a list of well marker representing the result of the database query
        :rtype: List[WellMarker]
        """
        result = session.query(cls)
        result = result.order_by(cls.id).all()
        for marker in result:
            marker.session = session
        return result