# -*- coding: UTF-8 -*-
"""
This module provides a class for storing stratigraphical information in database.
"""

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

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

	def __init__(self, session, name, age=-1, update=False):
		# type: (Session, str, int, bool) -> None
		"""
		Initialize a stratigraphic unit
		:param session: SQLAlchemy session, which includes the database connection
		:type session: Session

		:param name: Name of the stratigraphic unit
		:type name: str

		:param age: age of the stratigraphic unit (-1 if none)
		:type age: int

		:param update: update age if stratigraphic unit exists
		:type update: bool
		"""
		self.__session = session
		self.unit = name
		if update or (self.age is None):
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

	@unit.setter
	def unit(self, value):
		# type: (str) -> None
		"""
		Set a new name for the stratigraphic unit.
		Update from the database if the unit exist, else create a new one.

		:param value: New name of the stratigraphic unit
		:type value: str

		:return: Nothing
		"""
		# check if horizon exists (unique name)
		result = self.__session.query(Stratigraphy).filter(Stratigraphy.name == value)
		if result.count() == 0:
			self.name = value
			self.age = None
		elif result.count() == 1:
			self.name = result.one().unit
			self.age = result.one().age
			self.id = result.one().id
		else:  # more than one result? => heavy failure, name should be unique => DatabaseException
			for res in result.all():
				print(res)
			raise DatabaseException(
				'More than one ({}) horizon with the same name: {}! Database error!'.format(result.count(), value.name))

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
					'Cannot commit changes in stratigraphy table, Integrity Error (double unique values?) -- {} -- Rolling back changes...'.format(
							e.statement), e.params, e.orig, e.connection_invalidated)
