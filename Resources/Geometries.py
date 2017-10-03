# -*- coding: UTF-8 -*-

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship, sessionmaker

from Exceptions import DatabaseException
from Resources.DBHandler import Base
from Resources.Stratigraphy import Stratigraphy


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
		if not type(value) == sessionmaker:
			raise TypeError("Value is not of type sessionmaker (is {})!".format(str(type(value))))
		self.__session = value

	def insert_point(self, point, position):
		if type(point) is GeoPoint:
			self.points.insert(position, point)
		else:
			raise TypeError('point is not of type GeoPoint!')

	def insert_points(self, points, position):
		if type(position) is int:
			raise TypeError('Position is not of type int!')

		for pnt in points:
			if type(pnt) is not GeoPoint:
				raise TypeError('At least on point in points is not of type GeoPoint!')

		# use slicing for points insert
		self.points[position:position] = points

	def get_point_index(self, point):
		return self.points.index(point)

	#
	# !!! TO BE CHECKED AND UPDATED !!!
	#
	def delete_point(self, point):
		try:
			self.points.remove(point)
		except ValueError as e:
			raise ValueError(str(e) + '\nGeoPoint with ID ' + str(point.id) + ' not found in list!')

	def delete_point_by_coordinates(self, easting, northing, altitude):
		try:
			easting = float(easting)
			northing = float(northing)
			altitude = float(altitude)
		except ValueError:
			raise ValueError('On of the input coordinates is not of type float!')

		# iterate over a copy of the list to avoid iteration issues caused by the deletion of values
		for pnt in self.points[:]:
			if (pnt.easting == easting) and (pnt.northing == northing) and (pnt.altitude == altitude):
				self.points.remove(pnt)
				return True
		raise ValueError('Point not found with coordinates {0}/{1}/{2}'.format(easting, northing, altitude))

	def save_to_db(self):
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
					'Cannot commit changes in lines table, Integrity Error (double unique values?) -- {} -- Rolling back changes...'.format(
							e.statement), e.params, e.orig, e.connection_invalidated)

	@classmethod
	def load_all_from_db(cls, session):
		return session.query(cls).all()

	@classmethod
	def load_by_id_from_db(cls, line_id, session):
		return session.query(cls).filter(cls.id == line_id).one()

	@classmethod
	def load_in_extent_from_db(cls, session, min_easting, max_easting, min_northing, max_northing):
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
		return session.query(Line).filter(Line.id.in_(points)).all()
