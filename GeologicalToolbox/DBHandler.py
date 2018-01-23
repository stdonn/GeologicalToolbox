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
from typing import List

Base = declarative_base()


class DBHandler(object):
    """
    A class for database access through an SQLAlchemy session.
    """

    def __init__(self, connection='sqlite:///:memory:', *args, **kwargs):
        # type: (str, *object, **object) -> None
        """
        | Initialize a new database connection via SQLAlchemy
        | Same initialisation as SQLAlchemy provides. Additional arguments are piped to SQLAlchemy.create_engine(...)

        :param connection: Connection uri to a database, format defined by SQLAlchemy
        :type connection: str
        :return: Nothing
        """
        engine = sq.create_engine(connection, *args, **kwargs)
        Base.metadata.create_all(engine)
        self.__Session = sessionmaker(bind=engine)

    def get_session(self):
        # type: () -> sessionmaker
        """
        Returns the session object for the current database connection

        :return: Returns the session object for the current database connection
        """
        return self.__Session()


# class AbstractDBObject(object):
class AbstractDBObject(object):
    """
    This class represents the base class for all database objects. It should be treated as abstract, no object should be
    created directly!
    """

    name_col = sq.Column(sq.VARCHAR(100), default="")
    comment_col = sq.Column(sq.VARCHAR(100), default="")

    def __init__(self, session, name="", comment=""):
        # type: (Session, str, str) -> None
        """
        Initialises the class

        :param session: session object create by SQLAlchemy sessionmaker
        :type session: Session
        :param name: used to group objects by name
        :type name: str
        :param comment: additional comment
        :type comment: str
        :return: Nothing
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        if not isinstance(session, Session):
            raise TypeError("'session' value is not of type SQLAlchemy Session!\n{} - {}".format(str(type(session)),
                                                                                                  str(Session)))

        self.__session = session
        self.comment = comment
        self.name = name

        # ABCMeta.__init__(self)

    def __repr__(self):
        # type: () -> str
        """
        Returns a text-representation of the AbstractDBObject

        :return: Returns a text-representation of the AbstractDBObject
        :rtype: str
        """
        return "<AbstractDBObject(name='{}', comment='{}')>".format(self.name, self.comment)

    def __str__(self):
        # type: () -> str
        """
        Returns a text-representation of the AbstractDBObject

        :return: Returns a text-representation of the AbstractDBObject
        :rtype: str
        """
        return "{} - {}".format(self.name, self.comment)

    @property
    def comment(self):
        # type: () -> str
        """
        The additional comments for the AbstractDBObject

        :type: str
        """
        return self.comment_col

    @comment.setter
    def comment(self, comment):
        # type: (str) -> None
        """
        see getter
        """
        comment = str(comment)
        if len(comment) > 100:
            comment = comment[:100]
        self.comment_col = comment

    @property
    def name(self):
        # type: () -> str
        """
        The name of the AbstractDBObject

        :type: str
        """
        return self.name_col

    @name.setter
    def name(self, new_name):
        # type: (str) -> None
        """
        see getter
        """
        string = str(new_name)
        if len(string) > 100:
            string = string[:100]
        self.name_col = string

    @property
    def session(self):
        # type: () -> Session
        """
        The current Session object

        :type: Session
        :raises TypeError: if session is not of an instance of Session
        """
        return self.__session

    @session.setter
    def session(self, session):
        # type: (Session) -> None
        """
        see getter
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
        finally:
            pass
            # self.__session.close()

    @classmethod
    def delete_from_db(cls, obj, session):
        # type: (object, Session) -> None
        """
        Deletes an object from the database
        :param obj: object to delete
        :type obj; object
        :param session: SQLAlchemy Session handling the connection to the database
        :type session: Session
        :return: Nothing
        """
        session.delete(obj)
        session.commit()
        session.close()

    # load points from db
    @classmethod
    def load_all_from_db(cls, session):
        # type: (Session) -> List[cls]
        """
        Returns all well marker in the database connected to the SQLAlchemy Session session

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session
        :return: a list of well marker representing the result of the database query
        :rtype: List[WellMarker]
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        result = session.query(cls)
        result = result.order_by(cls.id).all()
        for marker in result:
            marker.session = session
        return result

    @classmethod
    def load_by_id_from_db(cls, id, session):
        # type: (int, Session) -> cls
        """
        Returns the line with the given id in the database connected to the SQLAlchemy Session session

        :param id: Only the object with this id will be returned (has to be 1, unique value)
        :type id: int
        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session
        :return: a single line representing the result of the database query
        :rtype: Line
        :raises NoResultFound: Raises NoResultFound if no line was found with this id
        :raises IntegrityError: Raises IntegrityError if more than one line is found (more than one unique value)
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        result = session.query(cls).filter(cls.id == id).one()
        result.session = session
        return result

    @classmethod
    def load_by_name_from_db(cls, name, session):
        # type: (str, Session) -> List[cls]
        """
        Returns all DBObjects with the given name in the database connected to the SQLAlchemy Session session

        :param name: Only DBObjects or derived types with this name will be returned
        :type name: str
        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session
        :return: a list of DBObjects representing the result of the database query
        :rtype: List[cls]
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        result = session.query(cls).filter(cls.name_col == name).order_by(cls.id).all()
        for obj in result:
            obj.session = session
        return result
