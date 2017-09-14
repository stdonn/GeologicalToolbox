# -*- coding: UTF-8 -*-

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

from Exceptions import DatabaseException
from Resources.DBHandler import Base
from Resources.Stratigraphy import Stratigraphy


class GeoPoint(Base):
	__tablename__ = 'geopoints'

	id = sq.Column(sq.INTEGER, sq.Sequence('geopoints_id_seq'), primary_key=True)
	east = sq.Column(sq.REAL(10, 4))
	north = sq.Column(sq.REAL(10, 4))
	alt = sq.Column(sq.REAL(10, 4))
	horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey('stratigraphy.id'), default=-1)
	hor = relationship("Stratigraphy")

	line_id = sq.Column(sq.INTEGER, sq.ForeignKey('lines.id'), default=-1)

	# make the points unique -> coordinates + horizon + belongs to one line?
	sq.UniqueConstraint(east, north, alt, horizon_id, line_id, name='u_point_constraint')

	def __init__(self, easting, northing, altitude, horizon, session):
		self.easting = easting
		self.northing = northing
		self.altitude = altitude
		self.__session = session
		self.horizon = horizon

	def __repr__(self):
		return "<GeoPoint(id='{}', east='{}', north='{}', alt='{}', horizon='{}')>" \
			.format(self.id, self.easting, self.northing, self.altitude, str(self.horizon))

	def __str__(self):
		return "[{}] {} - {} - {} : {}".format(self.id, self.easting, self.northing, self.altitude, str(self.horizon))

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

	@property
	def horizon(self):
		return self.hor

	@horizon.setter
	def horizon(self, value):
		if value is None:
			self.hor = None
			self.horizon_id = -1
			return

		result = self.__session.query(Stratigraphy).filter(Stratigraphy.name == value.name)
		if result.count() == 0:
			self.hor = value
		elif result.count() == 1:
			self.hor = result.one()
			self.hor.session = self.__session
		else:
			raise DatabaseException('More than one ({}) horizon with the same name: {}! Database error!'
			                        .format(result.count(), value.name))

	def save_to_db(self):
		self.__session.add(self)
		try:
			self.__session.commit()
		except IntegrityError as e:
			self.__session.rollback()
			raise IntegrityError(
					'Cannot commit changes in geopoints table, Integrity Error (double unique values?) -- {} -- Rolling back changes...'.format(
							e.statement), e.params, e.orig, e.connection_invalidated)

	@classmethod
	def load_all_from_db(cls, session):
		return session.query(cls).all()

	@classmethod
	def load_in_extend_from_db(cls, session, min_easting, max_easting, min_northing, max_northing):
		return session.query(cls).filter(min_easting <= cls.easting, cls.easting <= max_easting,
		                                 min_northing <= cls.northing, cls.northing <= max_northing).all()


class Line(Base):
	__tablename__ = 'lines'

	id = sq.Column(sq.INTEGER, sq.Sequence('line_id_seq'), primary_key=True)
	closed = sq.Column(sq.BOOLEAN)

	horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey('stratigraphy.id'))
	hor = relationship("Stratigraphy")

	# @AssociationType GeoPoint
	# @AssociationMultiplicity 2..*

	points = relationship("GeoPoint", order_by=GeoPoint.id, backref="line", primaryjoin='Line.id==GeoPoint.line_id',
	                      cascade="all, delete, delete-orphan")

	def __init__(self, closed, session, horizon, points):
		self.is_closed = closed
		self.__session = session
		self.horizon = horizon
		self.points = points
		self.__last_error_message = ''

	def __repr__(self):
		return "<Line(id='{}', closed='{}', horizon='{}'\npoints='{}')>" \
			.format(self.id, self.closed, str(self.horizon), str(self.points))

	def __str__(self):
		#return "[{}] {} - {}\n{}".format(self.id, self.closed, str(self.horizon), str(self.points))
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
		self.closed = value

	@property
	def horizon(self):
		return self.hor

	# @horizon.setter
	# def horizon(self, value):
	#	if (value is not None) and (type(value) != Stratigraphy):
	#		raise TypeError("Wrong type of value. Should be Stratigraphy or None, is {}".format(type(value)))
	#	self.hor = value  # unique check is performed by Stratigraphy class setter horizon

	@horizon.setter
	def horizon(self, value):
		if value is None:
			self.hor = None
			self.horizon_id = -1
			return

		result = self.__session.query(Stratigraphy).filter(Stratigraphy.name == value.name)
		if result.count() == 0:
			self.hor = value
		elif result.count() == 1:
			self.hor = result.one()
			self.hor.session = self.__session
		else:
			raise DatabaseException('More than one ({}) horizon with the same name: {}! Database error!'
			                        .format(result.count(), value.name))

	def insert_point(self, point, position):
		"""@ParamType point GeoPoint
		@ParamType position int
		@ReturnType bool"""
		if type(point) is GeoPoint:
			self.points.insert(position, point)
			return True
		else:
			self.__last_error_message = 'point is not of type GeoPoint!'
			raise TypeError(self.__last_error_message)

	def insert_points(self, points, position):
		"""@ParamType points GeoPoint[]
		@ParamType position int
		@ReturnType bool"""

		if type(position) is int:
			self.__last_error_message = 'Position is not of type int!'
			raise TypeError(self.__last_error_message)

		for pnt in points:
			if type(pnt) is not GeoPoint:
				self.__last_error_message = 'At least on point in points is not of type GeoPoint!'
				raise TypeError(self.__last_error_message)
		# use slicing for points insert
		self.points[position:position] = points
		return True

	# for point in points: self.points.insert( position + points.index( point ), point )

	def get_point_index(self, point):
		"""@ParamType point GeoPoint
		@ReturnType int"""
		return self.points.index(point)

	#
	# to be updated!!!
	#
	def delete_point(self, point):
		"""@ParamType point GeoPoint"""

		try:
			self.points.remove(point)
			return True
		except ValueError as e:
			self.__last_error_message = str(e) + '\nGeoPoint with ID ' + str(point.id) + ' not found in list!'
			raise ValueError(self.__last_error_message)

	def delete_point_by_coordinates(self, easting, northing, altitude):
		"""@ParamType easting float
		@ParamType northing float
		@ParamType altitude float"""
		try:
			easting = float(easting)
			northing = float(northing)
			altitude = float(altitude)
		except ValueError:
			self.__last_error_message = 'On of the input coordinates is not of type float!'
			raise ValueError(self.__last_error_message)

		for pnt in self.points[:]:
			if (pnt.easting == easting) and (pnt.northing == northing) and (pnt.altitude == altitude):
				self.points.remove(pnt)
				return True
		self.__last_error_message = 'Point not found with coordinates {0}/{1}/{2}'.format(easting, northing, altitude)
		raise ValueError(self.__last_error_message)

	def save_to_db(self):
		"""@ParamType handler DBHandler"""
		# self.horizon.save_to_db()
		self.__session.add(self)

		try:
			# first: all points should have the same horizon as the line
			for pnt in self.points:
				pnt.hor = self.horizon  # directly set hor variable, hor still checked...
				pnt.horizon_id = self.horizon_id
			self.__session.commit()
		except IntegrityError as e:
			self.__session.rollback()
			raise IntegrityError(
					'Cannot commit changes in lines table, Integrity Error (double unique values?) -- {} -- Rolling back changes...'.format(
							e.statement), e.params, e.orig, e.connection_invalidated)

	@classmethod
	def load_all_from_db(cls, session):
		return session.query(cls).all()

	@classmethod
	def load_in_extend_from_db(cls, session, min_easting, max_easting, min_northing, max_northing):
		return session.query(cls).filter(min_easting <= cls.easting, cls.easting <= max_easting,
		                                 min_northing <= cls.northing, cls.northing <= max_northing).all()

	def last_error_message(self):
		"""@ReturnType string"""
		return self.__last_error_message
