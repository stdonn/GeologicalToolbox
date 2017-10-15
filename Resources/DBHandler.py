# -*- coding: UTF-8 -*-
"""
This module provides a class for database access through an SQLAlchemy session.
"""

import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
