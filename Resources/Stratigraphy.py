# -*- coding: UTF-8 -*-
"""
This module provides a class for storing stratigraphical information in database.
"""

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from typing import List

from Exceptions import DatabaseException
from Resources.DBHandler import Base


class Stratigraphy(Base):
	"""
	A class for storing stratigraphical information in database.
	"""
	# define db table name and columns
	__tablename__ = 'stratigraphy'

	id = sq.Column(sq.INTEGER, sq.Sequence('strat_id_seq'), primary_key=True)
	name = sq.Column(sq.TEXT(50), unique=True)
	age = sq.Column(sq.INTEGER(), default=-1)

	def __init__(self, session, name, age=-1):
		# type: (Session, str, int) -> None
		"""
		Initialize a stratigraphic unit
		:param session: SQLAlchemy session, which includes the database connection
		:type session: Session

		:param name: Name of the stratigraphic unit
		:type name: str

		:param age: age of the stratigraphic unit (-1 if none)
		:type age: int

		:return: nothing
		"""
		try:
			age = int(age)
		except ValueError as e:
			raise ValueError("Cannot convert age to int:\n{}".format(str(e)))

		self.__session = session
		self.name = name
		self.age = age if (age > -1) else -1

	def __repr__(self):
		# type: () -> str
		"""
		Returns a text-representation of the line

		:return: Returns a text-representation of the line
		:rtype: str
		"""
		return "<StratigraphicHorizon(id='{}', name='{}', age='{}')>".format(self.id, self.name, self.age)

	def __str__(self):
		# type: () -> str
		"""
		Returns a text-representation of the line

		:return: Returns a text-representation of the line
		:rtype: str
		"""
		return "horizon [{}]: name='{}', age='{}'".format(self.id, self.name, self.age)

	# define setter and getter for columns and local data
	@property
	def horizon_age(self):
		# type: () -> int
		"""
		Return the age of the stratigraphic unit

		:return: age of the stratigraphic unit
		:rtype: int
		"""
		return self.age

	@horizon_age.setter
	def horizon_age(self, value):
		# type: (int) -> None
		"""
		Set a new age of the stratigraphic unit

		:param value: new age of the stratigraphic unit
		:type value: int

		:return: Nothing

		:raises ValueError: Raises ValueError if value is convertible to type int
		"""
		try:
			value = int(value)
		except ValueError:
			raise ValueError("Cannot convert value ({}) to type int.".format(str(value)))

		if value <= -1:
			self.age = -1
		else:
			self.age = value

	@property
	def unit(self):
		# type: () -> str
		"""
		Returns the name of the stratigraphic unit

		:return: Returns the name of the stratigraphic unit
		:rtype: str
		"""
		return self.name

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
	def session(self, value):
		# type: (Session) -> None
		"""
		Sets a new session, which represents the connection to a database

		:param value: session object create by SQLAlchemy sessionmaker
		:type value: Session

		:return: Nothing

		:raises TypeError: Raises TypeError if value is not of an instance of Session
		"""

		if not isinstance(value, Session):
			raise TypeError("Value is not of type {} (it is {})!".format(Session, type(value)))
		self.__session = value

	def save_to_db(self):
		# type: () -> None
		"""
		Saves all changes of the line or the line itself to the connected database

		:return: Nothing

		:raises IntegrityError: raises IntegrityError if the commit to the database fails and rolls all changes back
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
		# type: (Session, str, int, bool) -> cls
		"""
		Initialize a stratigraphic unit. Create a new one if unit doesn't exists in the database, else use the existing.

		:param session: SQLAlchemy session, which includes the database connection
		:type session: Session

		:param name: Name of the stratigraphic unit
		:type name: str

		:param age: age of the stratigraphic unit (-1 if none)
		:type age: int

		:param update: update age if stratigraphic unit exists
		:type update: bool
		"""

		try:
			age = int(age)
		except ValueError as e:
			raise ValueError("Cannot convert age to int:\n{}".format(str(e)))

		if age < -1:
			age = -1

		# check if horizon exists (unique name)
		result = session.query(Stratigraphy).filter(Stratigraphy.name == name)
		if result.count() == 0:  # no result found -> create new stratigraphic unit
			return cls(session, name, age)
		if result.count() == 1:  # one result found -> stratigraphic unit exists in database -> return and possibly update
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
		# type: (Session) -> List[Stratigraphy]
		"""
		Returns all stratigraphic units stored in the database connected to the SQLAlchemy Session session

		:param session: represents the database connection as SQLAlchemy Session
		:type session: Session

		:return: a list of stratigraphic units representing the result of the database query
		:rtype: List[Stratigraphy]
		"""
		return session.query(cls).all()

	@classmethod
	def load_by_name_from_db(cls, name, session):
		# type: (str, Session) -> Stratigraphy
		"""
		Returns the stratigraphic unit with the given name in the database connected to the SQLAlchemy Session session

		:param name: The name of the requested stratigraphic unit
		:type name: str

		:param session: represents the database connection as SQLAlchemy Session
		:type session: Session

		:return: As the name is a unique value, only one result can be returned or None
		:rtype: Stratigraphy or None

		:raises DatabaseException: Raises DatabaseException if more than one result was found (name is an unique value)
		"""
		result = session.query(cls).filter(cls.name == name)
		if result.count() == 0:
			return None
		if result.count() == 1:
			return result.one()

		raise DatabaseException('More than one ({}) horizon with the same name: {}! Database error!'. \
		                        format(result.count(), name))

	@classmethod
	def load_by_age_from_db(cls, min_age, max_age, session):
		# type: (int, int, Session) -> List[Stratigraphy]
		"""
		Returns a list of stratigraphic units with an age between min_age and max_age from the database connected to
		the SQLAlchemy Session session. If no result was found, this function returns an empty list.

		:param min_age: Minimal age of the stratigraphic units
		:type min_age: int

		:param max_age: Maximal age of the stratigraphic units
		:type max_age: int

		:param session: represents the database connection as SQLAlchemy Session
		:type session: Session

		:return: Returns a list of stratigraphic units with an age between min_age and max_age.
		:rtype: List[Stratigraphy]
		"""
		return session.query(cls).filter(sq.between(cls.age, min_age, max_age)).all()
