# -*- coding: UTF-8 -*-

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from typing import List

from Exceptions import DatabaseException
from Resources.DBHandler import Base
from Resources.Stratigraphy import Stratigraphy
from Resources.constants import float_precision


class GeoPoint(Base):
	# define db table name and columns
	__tablename__ = 'geopoints'

	id = sq.Column(sq.INTEGER, sq.Sequence('geopoints_id_seq'), primary_key=True)
	east = sq.Column(sq.REAL(10, 4))
	north = sq.Column(sq.REAL(10, 4))
	alt = sq.Column(sq.REAL(10, 4))
	has_z = sq.Column(sq.BOOLEAN, default=False)
	horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey('stratigraphy.id'), default=-1)

	# define relationship to stratigraphic table
	hor = relationship("Stratigraphy")

	line_id = sq.Column(sq.INTEGER, sq.ForeignKey('lines.id'), default=-1)
	line_pos = sq.Column(sq.INTEGER, default=-1)
	name = sq.Column(sq.TEXT(100), default="")

	# make the points unique -> coordinates + horizon + belongs to one line?
	sq.UniqueConstraint(east, north, alt, horizon_id, line_id, line_pos, name='u_point_constraint')

	def __init__(self, easting, northing, altitude, horizon, session, name=""):
		self.easting = easting
		self.northing = northing
		if altitude is None:
			self.altitude = 0
			self.has_z = False
		else:
			self.altitude = altitude
			self.has_z = True
		self.__session = session
		self.horizon = horizon
		self.point_name = name

	def __repr__(self):
		return "<GeoPoint(id='{}', east='{}', north='{}', alt='{}', horizon='{}', line={}, line-position={})>" \
			.format(self.id, self.easting, self.northing, self.altitude, str(self.horizon), self.line_id, self.line_pos)

	def __str__(self):
		return "[{}] {} - {} - {} : {} - {} - {}" \
			.format(self.id, self.easting, self.northing, self.altitude, str(self.horizon), self.line_id, self.line_pos)

	# define setter and getter for columns and local data
	@property
	def easting(self):
		return self.east

	@easting.setter
	def easting(self, value):
		self.east = value

	@property
	def northing(self):
		return self.north

	@northing.setter
	def northing(self, value):
		self.north = value

	@property
	def altitude(self):
		return self.alt

	@altitude.setter
	def altitude(self, value):
		self.alt = value
		self.has_z = True

	@property
	def horizon(self):
		return self.hor

	@horizon.setter
	def horizon(self, value):
		# check if horizon exists in db -> if true take the db version, don't create a new one
		if value is None:
			self.hor = None
			self.horizon_id = -1
			return

		result = self.__session.query(Stratigraphy).filter(Stratigraphy.name == value.name)
		if result.count() == 0:  # horizon doesn't exist -> use the committed value
			self.hor = value
		elif result.count() == 1:  # horizon exists in the db -> use the db value
			self.hor = result.one()
			self.hor.session = self.__session
		else:  # more than one horizon with this name in the db => heavy failure, name should be unique => DatabaseException
			raise DatabaseException('More than one ({}) horizon with the same name: {}! Database error!'
			                        .format(result.count(), value.name))

	@property
	def point_name(self):
		return self.name

	@point_name.setter
	def point_name(self, value):
		if len(value) > 100:
			value = value[:100]
		self.name = value

	# delete z-dimension and information from point
	def del_z(self):
		self.alt = 0
		self.has_z = False

	# save point to db / update point
	def save_to_db(self):
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
	def load_all_from_db(cls, session, get_lines=False):
		if get_lines:
			return session.query(cls).all()
		return session.query(cls).filter(GeoPoint.line_id == -1).all()

	@classmethod
	def load_in_extend_from_db(cls, session, min_easting, max_easting, min_northing, max_northing, get_lines=False):
		result = session.query(GeoPoint)
		if not get_lines:
			result.filter(GeoPoint.line_id == -1)

		return result.filter(sq.between(GeoPoint.east, min_easting, max_easting)). \
			filter(sq.between(GeoPoint.north, min_northing, max_northing)).all()


class Line(Base):
	# define db table name and columns
	__tablename__ = 'lines'

	id = sq.Column(sq.INTEGER, sq.Sequence('line_id_seq'), primary_key=True)
	closed = sq.Column(sq.BOOLEAN)
	name = sq.Column(sq.TEXT(100), default="")

	# set stratigraphy of the line
	horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey('stratigraphy.id'))
	hor = relationship("Stratigraphy")

	# add GeoPoint relation, important is the ordering by line_pos value
	# collection_class function automatically reorders this value in case of insertion or deletion of points
	points = relationship("GeoPoint", order_by=GeoPoint.line_pos, collection_class=ordering_list('line_pos'),
	                      backref="line", primaryjoin='Line.id==GeoPoint.line_id',
	                      cascade="all, delete, delete-orphan")

	def __init__(self, closed, session, horizon, points, name=""):
		self.is_closed = closed
		self.__session = session
		self.horizon = horizon
		self.points = points
		self.line_name = name

		# check doubled values in a line
		self.__remove_doubled_points()

	def __repr__(self):
		return "<Line(id='{}', closed='{}', horizon='{}'\npoints='{}')>" \
			.format(self.id, self.closed, str(self.horizon), str(self.points))

	def __str__(self):
		# return "[{}] {} - {}\n{}".format(self.id, self.closed, str(self.horizon), str(self.points))
		text = "Line: id='{}', closed='{}', horizon='{}', points:" \
			.format(self.id, self.closed, str(self.horizon))

		for point in self.points:
			text += "\n{}".format(str(point))

		return text

	@property
	def is_closed(self):
		return self.closed

	@is_closed.setter
	def is_closed(self, value):
		if type(value) != bool:
			raise TypeError('Value must be of type bool, but is {}'.format(str(type(value))))
		self.closed = bool(value)

	@property
	def horizon(self):
		return self.hor

	@horizon.setter
	def horizon(self, value):
		if value is None:
			self.hor = None
			self.horizon_id = -1
			return

		# check if horizon exists (unique name)
		result = self.__session.query(Stratigraphy).filter(Stratigraphy.name == value.name)
		if result.count() == 0:
			self.hor = value
		elif result.count() == 1:
			self.hor = result.one()
			self.hor.session = self.__session
		else:  # more than one result? => heavy failure, name should be unique => DatabaseException
			raise DatabaseException('More than one ({}) horizon with the same name: {}! Database error!'
			                        .format(result.count(), value.name))

	@property
	def line_name(self):
		return self.name

	@line_name.setter
	def line_name(self, value):
		if len(value) > 100:
			value = value[:100]
		self.name = value

	@property
	def session(self):
		return self.__session

	@session.setter
	def session(self, value):
		if not isinstance(value, Session):
			raise TypeError("Value is not of type {} (it is {})!".format(Session, type(value)))
		self.__session = value

	def insert_point(self, point, position):
		if type(point) is GeoPoint:
			self.points.insert(position, point)
		else:
			raise TypeError('point is not of type GeoPoint!')

		# check doubled values in a line
		self.__remove_doubled_points()

	def insert_points(self, points, position):
		# type: (List[GeoPoint], int) -> None
		"""
		Returns the index of the given point in the line

		:param points: List of points to be inserted in the line
		:type points: List[GeoPoint]

		:param position: Index, where points should be inserted in the line
		:type position: int

		:return: Nothing
		:rtype: None

		:raises TypeError: Raises TypeError if position is not of type int of one of the points is not of type GeoPoint
		"""
		if type(position) is not int:
			raise TypeError('Position is not of type int (is {})!'.format(type(position)))

		for pnt in points:
			if type(pnt) is not GeoPoint:
				raise TypeError('At least on point in points is not of type GeoPoint!')

		# use slicing for points insert
		if len(self.points) <= position:
			self.points[-1:-1] = points
		else:
			self.points[position:position] = points

		# check doubled values in a line
		self.__remove_doubled_points()

	def get_point_index(self, point):
		# type: (GeoPoint) -> int
		"""
		Returns the index of the given point in the line

		:param point: point which has to be looked up
		:type point: GeoPoint

		:return: Index of the ppint in the line
		:rtype: int

		:raises ValueError: Raises ValueError if committed point is not part of the line
		"""
		return self.points.index(point)

	def delete_point(self, point):
		# type: (GeoPoint) -> None
		"""
		Deletes the point from the line

		:param point: GeoPoint object which should be deleted
		:type point: GeoPoint

		:return: Nothing
		:rtype: None

		:raises ValueError: Raises ValueError the point is not part of the line
		"""
		try:
			self.points.remove(point)
		except ValueError as e:
			raise ValueError(str(e) + '\nGeoPoint with ID ' + str(point.id) + ' not found in list!')

		# check doubled values in a line
		self.__remove_doubled_points()

	def delete_point_by_coordinates(self, easting, northing, altitude=0):
		# type: (float, float, float) -> None
		"""
		Deletes a point with the given coordinates from the line

		:param easting: easting value of the point to be deleted
		:type easting: float

		:param northing: northing value of the point to be deleted
		:type northing: float

		:param altitude: altitude value of the point to be deleted (only necessary if point has z-values!)
		:type altitude: float

		:return: Nothing
		:rtype: None

		:raises ValueError: Raises ValueError if on parameter is not compatible to type float or no point can be found
		"""
		try:
			easting = float(easting)
			northing = float(northing)
			altitude = float(altitude)
		except ValueError:
			raise ValueError('On of the input coordinates is not of type float!')

		# iterate over a copy of the list to avoid iteration issues caused by the deletion of values
		for pnt in self.points[:]:
			if (abs(float(pnt.easting) - easting) < float_precision) and (
						abs(float(pnt.northing) - northing) < float_precision) and (
						(abs(float(pnt.altitude) - altitude) < float_precision) or not pnt.has_z):
				self.points.remove(pnt)
				# check doubled values in a line
				self.__remove_doubled_points()
				return

		raise ValueError('Point not found with coordinates {0}/{1}/{2}'.format(easting, northing, altitude))

	def __remove_doubled_points(self):
		# type: () -> None
		"""
		remove points with the same coordinates, if they follow up each other in the points list.

		:return: None
		:rtype: None
		"""

		# create a full copy of the point-list
		tmp_pnts = self.points[:]
		for i in range(len(tmp_pnts) - 1):
			coord_1 = (tmp_pnts[i].easting, tmp_pnts[i].northing, tmp_pnts[i].altitude)
			coord_2 = (tmp_pnts[i + 1].easting, tmp_pnts[i + 1].northing, tmp_pnts[i + 1].altitude)

			# remove doubled points
			if coord_1 == coord_2:
				self.points.remove(tmp_pnts[i + 1])

		# test for first and last point
		# if identical, then remove last point and set closed to True
		coord_1 = (self.points[0].easting, self.points[0].northing, self.points[0].altitude)
		coord_2 = (self.points[-1].easting, self.points[-1].northing, self.points[-1].altitude)

		if coord_1 == coord_2:
			del self.points[-1]
			self.closed = True

	def save_to_db(self):
		# type: () -> None
		"""
		Saves all changes of the line or the line itself to the connected database

		:return: Nothing
		:rtype: None

		:raises IntegrityError: raises IntegrityError if the commit to the database fails and rolls all changes back
		"""
		self.__session.add(self)

		try:
			# first: all points should have the same horizon as the line
			for pnt in self.points:
				pnt.hor = self.horizon  # directly set hor variable, hor still checked...
				pnt.horizon_id = self.horizon_id
			self.__session.commit()
		except IntegrityError as e:
			# Failure during database processing? -> rollback changes and raise error again
			self.__session.rollback()
			raise IntegrityError(
					'Cannot commit changes in lines table, Integrity Error (double unique values?) -- {} -- Rolling back changes...'. \
						format(e.statement), e.params, e.orig, e.connection_invalidated)

	@classmethod
	def load_all_from_db(cls, session):
		# type: (str, Session) -> List[Line]
		"""
		Returns all lines in the database connected to the SQLAlchemy Session session

		:param session: represents the database connection as SQLAlchemy Session
		:type session: Session

		:return: a list of lines representing the result of the database query
		:rtype: List[Line]
		"""
		return session.query(cls).all()

	@classmethod
	def load_by_id_from_db(cls, line_id, session):
		# type: (int, Session) -> Line
		"""
		Returns the line with the given id in the database connected to the SQLAlchemy Session session

		:param line_id: Only the line with this id will be returned (has to be 1, unique value)
		:type line_id: int

		:param session: represents the database connection as SQLAlchemy Session
		:type session: Session

		:return: a single line representing the result of the database query
		:rtype: Line

		:raises NoResultFound: Raises NoResultFound if no line was found with this id
		:raises IntegrityError: Raises IntegrityError if more than one line is found (more than one unique value)
		"""
		return session.query(cls).filter(cls.id == line_id).one()

	@classmethod
	def load_by_name_from_db(cls, name, session):
		# type: (str, Session) -> List[Line]
		"""
		Returns all lines with the given name in the database connected to the SQLAlchemy Session session

		:param name: Only lines with this name will be returned
		:type name: str

		:param session: represents the database connection as SQLAlchemy Session
		:type session: Session

		:return: a list of lines representing the result of the database query
		:rtype: List[Line]
		"""
		return session.query(cls).filter(cls.name == name).all()

	@classmethod
	def load_in_extent_from_db(cls, session, min_easting, max_easting, min_northing, max_northing):
		# type: (Session, float, float, float, float) -> List[Line]
		"""
		Returns all lines with at least on point inside the given extent in the database connected to the SQLAlchemy Session session

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

		:return: a list of lines representing the result of the database query
		:rtype: List[Line]
		"""

		# select the points with a line_id that are located inside the extent
		# -> result will be a list of tuples with only a single line-id value
		# -> convert this list to a set in order to remove doubled values

		points = set(
				[x[0] for x in session.query(GeoPoint.line_id). \
					filter(GeoPoint.line_id != -1). \
					filter(sq.between(GeoPoint.east, min_easting, max_easting)). \
					filter(sq.between(GeoPoint.north, min_northing, max_northing)).all()
				 ])

		# return line with points in extend
		# to speed up the process, test first if points (len > 0) exist in extent
		return [] if (len(points) == 0) else session.query(Line).filter(Line.id.in_(points)).all()
