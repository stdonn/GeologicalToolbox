# -*- coding: UTF-8 -*-
"""
This module provides classes for storing drilling data in a database.
"""

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from typing import List

from Exceptions import DatabaseException
from Resources.DBHandler import Base
from Resources.constants import float_precision


class WellMarker(Base):
	"""
	Class WellMarer

	Represents single markers in a drilled well
	"""
	# define db table name and columns
	__tablename__ = 'well_marker'

	id = sq.Column(sq.INTEGER, sq.Sequence('well_id_seq'), primary_key=True)
	drill_depth = sq.Column(sq.FLOAT(10, 4))
	comment = sq.Column(sq.TEXT(100), default="")

	# define relationship to stratigraphic table
	horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey('stratigraphy.id'))
	hor = relationship("Stratigraphy")

	well_id = sq.Column(sq.INTEGER, sq.ForeignKey('wells.id'), default=-1)


class Well(Base):
	"""
	Class Well

	Represents a well for storage of geoscientific data.
	"""
	# define db table name and columns
	__tablename__ = 'wells'

	id = sq.Column(sq.INTEGER, sq.Sequence('well_id_seq'), primary_key=True)
	east = sq.Column(sq.FLOAT(10, 4))
	north = sq.Column(sq.FLOAT(10, 4))
	alt = sq.Column(sq.FLOAT(10, 4))
	drill_depth = sq.Column(sq.FLOAT(10, 4))
	well_name = sq.Column(sq.TEXT(100), unique=True)
	short_well_name = sq.Column(sq.TEXT(100), default="")

	# define markers relationship
	marker = relationship("WellMarker", order_by=WellMarker.depth, collection_class=ordering_list('depth'),
	                      backref="well", primaryjoin='Well.id==WellMarker.well_id',
	                      cascade="all, delete, delete-orphan")

	def __init__(self, session, easting, northing, altitude, depth, name, short_name=""):
		# type: (Session, float, float, float, float, str, str) -> None
		"""
		Creates a new Well

		:param session: SQLAlchemy session, which includes the database connection
		:type session: Session

		:param easting: easting coordinate of the well
		:type easting: float

		:param northing: northing coordinate of the well
		:type northing: float

		:param altitude: height above sea level of the well
		:type altitude: float

		:param depth: drilled depth of the well
		:type depth: float

		:param name: well name
		:type name: str

		:param short_name: well name
		:type short_name: str

		:return: Nothing
		:raises ValueError: Raises ValueError if one of the types cannot be converted
		"""
		if type(session) is not Session:
			raise ValueError("'session' value is not of type SQLAlchemy Session!")

		self.__session = session
		self.easting = float(easting)
		self.northing = float(northing)
		self.altitude = float(altitude)
		self.depth = float(depth)
		self.name = str(name)
		self.short_name = str(short_name)

	def __repr__(self):
		# type: () -> str
		"""
		Returns a text-representation of the well

		:return: Returns a text-representation of the well
		:rtype: str
		"""
		return "<Well(id='{}', name='{}', short_name='{}', east='{}', north='{}', alt='{}', depth='{}')>" \
			.format(self.id, self.name, self.short_name, self.easting, self.northing, self.altitude, self.depth)

	def __str__(self):
		# type: () -> str
		"""
		Returns a text-representation of the well

		:return: Returns a text-representation of the well
		:rtype: str
		"""
		return "[{}] {} ({}):\n{} - {} - {} - {}" \
			.format(self.id, self.name, self.short_name, self.easting, self.northing, self.altitude, self.depth)

	# define setter and getter for columns and local data
	@property
	def easting(self):
		# type: () -> float
		"""
		Returns the easting value of the well.

		:return: Returns the easting value of the well.
		:rtype: float
		"""
		return self.east

	@easting.setter
	def easting(self, value):
		# type: (float) -> None
		"""
		Sets a new easting value

		:param value: new easting value
		:type value: float

		:return: Nothing
		:raises ValueError: Raises ValueError if value if not of type float or cannot be converted to float
		"""
		self.east = float(value)

	@property
	def northing(self):
		# type: () -> float
		"""
		Returns the northing value of the well.

		:return: Returns the northing value of the well.
		:rtype: float
		"""
		return self.north

	@northing.setter
	def northing(self, value):
		# type: (float) -> None
		"""
		Sets a new northing value

		:param value: new northing value
		:type value: float

		:return: Nothing
		:raises ValueError: Raises ValueError if value if not of type float or cannot be converted to float
		"""
		self.north = float(value)

	@property
	def altitude(self):
		# type: () -> float
		"""
		Returns the height above sea level of the well.

		:return: Returns the height above sea level of the well.
		:rtype: float
		"""
		return self.alt

	@altitude.setter
	def altitude(self, value):
		# type: (float) -> None
		"""
		Sets a new height above sea level

		:param value: New height above sea level
		:type value: float

		:return: Nothing
		:raises ValueError: Raises ValueError if value if not of type float or cannot be converted to float
		"""
		self.alt = float(value)

	@property
	def depth(self):
		# type: () -> float
		"""
		Returns the drilled depth of the well

		:return: Returns the drilled depth of the well
		:rtype: float
		"""
		return self.drill_depth

	@depth.setter
	def depth(self, value):
		# type: (float) -> None
		"""
		sets a drilled depth of the well

		:param value: drilled depth
		:type value: float

		:return: Nothing
		:raises ValueError: Raises ValueError if the committed value cannot be converted to float
		"""
		self.drill_depth = float(value)

	@property
	def name(self):
		# type: () -> str
		"""
		Returns the name of the well

		:return: Returns the name of the well
		:rtype: str
		"""
		return self.well_name

	@name.setter
	def name(self, value):
		# type: (str) -> None
		"""
		Sets a new name for the well with a maximum of 100 characters

		:param value: well name
		:type value: str

		:return: Nothing
		"""

		string = str(value)
		if len(string) > 100:
			string = string[:100]
		self.well_name = string

	@property
	def short_name(self):
		# type: () -> str
		"""
		Returns the short name of the well

		:return: Returns the short name of the well
		:rtype: str
		"""
		return self.short_well_name

	@short_name.setter
	def short_name(self, value):
		# type: (str) -> None
		"""
		Sets a new short name for the well with a maximum of 20 characters

		:param value: well name
		:type value: str

		:return: Nothing
		"""

		string = str(value)
		if len(string) > 20:
			string = string[:20]
		self.short_well_name = string

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

	# save point to db / update point
	def save_to_db(self):
		# type: () -> None
		"""
		Saves all changes of the well to the database

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
					'Cannot commit changes in geopoints table, Integrity Error (double unique values?) -- {} -- Rolling back changes...'.format(
							e.statement), e.params, e.orig, e.connection_invalidated)

	# load points from db
	@classmethod
	def load_all_from_db(cls, session):
		# type: (Session) -> List[Well]
		"""
		Returns all wells in the database connected to the SQLAlchemy Session session

		:param session: represents the database connection as SQLAlchemy Session
		:type session: Session

		:return: a list of wells representing the result of the database query
		:rtype: List[Well]
		"""
		result = session.query(cls)
		result = result.order_by(cls.id).all()
		for well in result:
			well.session = session
		return result

	@classmethod
	def load_by_name_from_db(cls, name, session):
		# type: (str, Session) -> Well
		"""
		Returns the well with the given name in the database connected to the SQLAlchemy Session session

		:param name: Only the well with this name will be returned
		:type name: str

		:param session: represents the database connection as SQLAlchemy Session
		:type session: Session

		:return: As the name is a unique value, only one result can be returned or None
		:rtype: Well or None

		:raises DatabaseException: Raises DatabaseException if more than one result was found (name is an unique value)
		"""
		result = session.query(cls).filter(cls.well_name == name)
		if result.count() == 0:
			return None
		if result.count() == 1:
			result = result.one()
			result.session = session
			return result

		raise DatabaseException('More than one ({}) well with the same name: {}! Database error!'. \
		                        format(result.count(), name))

	@classmethod
	def load_in_extent_from_db(cls, session, min_easting, max_easting, min_northing, max_northing):
		# type: (Session, float, float, float, float) -> List[Well]
		"""
		Returns all wells inside the given extent in the database connected to the SQLAlchemy Session session

		:param min_easting: minimal easting of extent
		:type min_easting: float

		:param max_easting: maximal easting of extent
		:type max_easting: float

		:param min_northing: minimal northing of extent
		:type min_northing: float

		:param max_northing: maximal northing of extent
		:type max_northing: float

		:param session: represents the database connection as SQLAlchemy Session
		:type session: Session

		:return: a list of wells representing the result of the database query
		:rtype: List[Well]
		"""
		result = session.query(cls).filter(sq.between(cls.east, min_easting, max_easting)). \
			filter(sq.between(cls.north, min_northing, max_northing))
		result = result.order_by(cls.id).all()
		for well in result:
			well.session = session
		return result
