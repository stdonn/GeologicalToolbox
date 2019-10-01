# -*- coding: UTF-8 -*-
"""
Providing the DBHandler class for database access through a SQLAlchemy session and the AbstractDBObject base class for
all other database related classes.
"""

import inspect
import os
import sqlalchemy as sq

from alembic import command, script
from alembic.config import Config
from alembic.runtime import migration
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from typing import List

from geological_toolbox.exceptions import DatabaseRequestException

Base = declarative_base()


class DBHandler(object):
    """
    A class for database access through an SQLAlchemy session.
    Same initialisation as SQLAlchemy provides. Additional arguments are piped to :meth:`sqlalchemy.create_engine`

    :param connection: Connection uri to a database, format defined by SQLAlchemy
    :return: Nothing
    """

    def __init__(self, connection: str = "sqlite:///:memory:", *args, **kwargs) -> None:
        """
        Initialize a new database connection via SQLAlchemy
        """
        self.__connection = connection
        self.__args = args
        self.__kwargs = kwargs

        self.__engine = sq.create_engine(self.__connection, *self.__args, **self.__kwargs)
        self.__last_session = None
        self.__config = "alembic.ini"

        in_memory = self.__connection in ["sqlite://", "sqlite:///:memory:"]
        if not (in_memory or self.check_current_head()):
            self.start_db_migration()

        if in_memory:
            Base.metadata.create_all(self.__engine)

        self.__sessionmaker = sessionmaker(bind=self.__engine)
        self.create_new_session()

    def check_current_head(self) -> bool:
        """
        Checks if the selected database schema version matches the python source ORM schema version.
        If false please run start_db_migration to update the database.

        :return: True if both version are matching, else False
        """
        local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))  # script directory
        alembic_cfg = Config(os.path.abspath(os.path.join(local_dir, "alembic.ini")))

        # Alembic has problems, when called inside a library,
        # therefore we change the current folder with its absolute path
        alembic_cfg.set_main_option(
            "script_location",
            os.path.abspath(os.path.join(local_dir, alembic_cfg.get_main_option("script_location", "alembic")))
        )

        directory = script.ScriptDirectory.from_config(alembic_cfg)
        with self.__engine.begin() as connection:
            context = migration.MigrationContext.configure(connection)
            return set(context.get_current_heads()) == set(directory.get_heads())

    def start_db_migration(self) -> None:
        """
        Runs alembic to upgrade the selected database to the current conversion head. This ensures that the database
        schema version matches the python ORM version.

        :return: Nothing
        """
        self.close_last_session()

        local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))  # script directory
        alembic_cfg = Config(os.path.abspath(os.path.join(local_dir, "alembic.ini")))

        # Alembic has problems, when called inside a library,
        # therefore we change the current alembic folder with its absolute path
        alembic_cfg.set_main_option(
            "script_location",
            os.path.abspath(os.path.join(local_dir, alembic_cfg.get_main_option("script_location", "alembic")))
        )
        alembic_cfg.set_main_option("sqlalchemy.url", self.__connection)
        command.upgrade(alembic_cfg, "head")

    def create_new_session(self) -> Session:
        """
        Creates and returns a new session object

        :return: returns a newly created session object
        """
        self.__last_session = self.__sessionmaker()
        return self.__last_session

    def get_session(self) -> Session:
        """
        Returns the session object for the current database connection
        returns: Returns the session object for the current database connection
        """
        if self.__last_session is None:
            return self.create_new_session()
        else:
            return self.__last_session

    def close_last_session(self) -> None:
        """
        Close the actual session

        :return: Nothing
        """
        if self.__last_session is not None:
            self.__last_session.close()
            self.__last_session = None


# class AbstractDBObject(object):
class AbstractDBObject(object):
    """
    This class represents the base for all database objects. It should be treated as abstract, no object should be
    created directly!

    :param session: session object create by SQLAlchemy sessionmaker
    :type session: Session
    :param name: used to group objects by name
    :type name: str
    :param comment: additional comment
    :type comment: str
    :return: Nothing
    :raises TypeError: if session is not of type SQLAlchemy Session
    """

    id = None
    name_col = sq.Column(sq.VARCHAR(100), default="")
    comment_col = sq.Column(sq.VARCHAR(100), default="")

    def __init__(self, session: Session, name: str = "", comment: str = "") -> None:
        """
        Initialises the class
        """

        if not isinstance(session, Session):
            raise TypeError("'session' value is not of type SQLAlchemy Session!\n{} - {}".format(str(type(session)),
                                                                                                 str(Session)))

        self.__session = session
        self.comment = comment
        self.name = name

        # ABCMeta.__init__(self)

    def __repr__(self) -> str:
        return "<AbstractDBObject(name='{}', comment='{}')>".format(self.name, self.comment)

    def __str__(self) -> str:
        return "{} - {}".format(self.name, self.comment)

    @property
    def comment(self) -> str:
        """
        The additional comments for the AbstractDBObject
        """
        return self.comment_col

    @comment.setter
    def comment(self, comment: str) -> None:
        """
        see getter
        """
        comment = str(comment)
        if len(comment) > 100:
            comment = comment[:100]
        self.comment_col = comment

    def get_id(self) -> int or None:
        """
        Returns the database object id or None, if not saved / flushed to the database
        """
        return self.id

    @property
    def name(self) -> str:
        """
        The name of the AbstractDBObject
        """
        return self.name_col

    @name.setter
    def name(self, new_name: str) -> None:
        """
        see getter
        """
        new_name = str(new_name)
        if len(new_name) > 100:
            new_name = new_name[:100]
        self.name_col = new_name

    @property
    def session(self) -> Session:
        """
        The current Session object

        :raises TypeError: if session is not of an instance of Session
        """
        return self.__session

    @session.setter
    def session(self, session: Session) -> None:
        """
        see getter
        """

        if not isinstance(session, Session):
            raise TypeError("Value is not of type {} (it is {})!".format(Session, type(session)))

        self.__session = session

    # save point to db / update point
    def save_to_db(self) -> None:
        """
        Saves all changes of the object to the database

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
                "Cannot commit changes in table, Integrity Error (double unique values?) -- {} -- " +
                "Rolling back changes...".format(e.statement), e.params, e.orig, e.connection_invalidated)
        finally:
            pass
            # self.__session.close()

    @classmethod
    def delete_from_db(cls, obj: "AbstractDBObject", session: Session):
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

    @classmethod
    def load_all_from_db(cls, session: Session) -> List["AbstractDBObject"]:
        """
        Returns all objects in the database connected to the SQLAlchemy Session session

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session
        :return: a list of objects
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
    def load_by_id_from_db(cls, _id: int, session: Session) -> "AbstractDBObject":
        """
        Returns the object with the given id in the database

        :param _id: Only the object with this id will be returned
        :param session: represents the database connection as SQLAlchemy Session
        :return: a single object representing the result of the database query
        :raises DatabaseRequestException: Raises DatabaseRequestException if no object was found with this id
        :raises IntegrityError: Raises IntegrityError if more than one object was found (more than one unique value)
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        try:
            result = session.query(cls).filter(cls.id == _id).one()
            result.session = session
            return result
        except NoResultFound:
            raise DatabaseRequestException("No result found for ID {}".format(_id))

    @classmethod
    def load_by_name_from_db(cls, name: str, session: Session) -> List["AbstractDBObject"]:
        """
        Returns all objects with the given name in the database

        :param name: Only objects or derived types with this name will be returned
        :param session: represents the database connection as SQLAlchemy Session
        :return: a list of objects representing the result of the database query
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        result = session.query(cls).filter(cls.name_col == name).order_by(cls.id).all()
        for obj in result:
            obj.session = session
        return result
