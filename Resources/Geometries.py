# -*- coding: UTF-8 -*-

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

from Resources.DBHandler import Base

class GeoPoint(Base):
	__tablename__ = 'geopoints'

	id = sq.Column(sq.INTEGER, sq.Sequence('horizons_id_seq'), primary_key=True)
	east = sq.Column(sq.REAL(10, 4))
	north = sq.Column(sq.REAL(10, 4))
	alt = sq.Column(sq.REAL(10, 4))
	age = sq.Column(sq.INTEGER())
	horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey('stratigraphy.id'))
	hor = relationship("Stratigraphy")

	line_id = sq.Column(sq.INTEGER, sq.ForeignKey('lines.id'))

	def __init__(self, easting, northing, altitude, horizon):
		self.easting = easting
		self.northing = northing
		self.altitude = altitude
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
		self.hor = value

	def save_to_db(self, handler):
		"""@ParamType handler DBHandler"""
		session = handler.get_session()
		session.add(self)
		try:
			session.commit()
		except IntegrityError as e:
			print('Cannot commit changes, Integrity Error (double unique values?)')
			print(e)
			session.rollback()

class Line(Base):
	__tablename__ = 'lines'

	id = sq.Column(sq.INTEGER, sq.Sequence('line_id_seq'), primary_key=True)
	closed = sq.Column(sq.BOOLEAN)

	horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey('stratigraphy.id'))
	hor = relationship("Stratigraphy")

	# @AssociationType GeoPoint
	# @AssociationMultiplicity 2..*

	point_ids = sq.Column(sq.INTEGER, sq.ForeignKey('geopoints.id'))
	points = relationship("GeoPoints", order_by=GeoPoint.id)

	def __init__(self, closed, horizon, points):
		self.is_closed = closed
		self.horizon = horizon
		self.points = points

	def __repr__(self):
		return "<Line(id='{}', closed='{}', horizon='{}'\npoints='{}')>" \
			.format(self.id, self.closed, str(self.horizon), str(self.points))

	def __str__(self):
		return "[{}] {} - {}\n{}".format(self.id, self.closed, str(self.horizon), str(self.points))

	@property
	def is_closed(self):
		return self.closed

	@is_closed.setter
	def is_closed(self, value):
		self.closed = value

	@property
	def horizon(self):
		return self.hor

	@horizon.setter
	def horizon(self, value):
		self.hor = value

	def insert_point(self, point, position):
		"""@ParamType point GeoPoint
		@ParamType position int
		@ReturnType bool"""
		if type( point ) is GeoPoint:
			self.points.insert(position, point)
			return True
		else:
			self.__last_error_message = 'point is not of type GeoPoint!'
			raise TypeError(self.__last_error_message)

	def insert_points(self, points, position):
		"""@ParamType points GeoPoint[]
		@ParamType position int
		@ReturnType bool"""

		if type( position ) is int:
			self.__last_error_message = 'Position is not of type int!'
			raise TypeError(self.__last_error_message)

		for pnt in points:
			if type( pnt ) is not GeoPoint:
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
	def deletePoint(self, point):
		"""@ParamType point GeoPoint"""

		try:
			self.points.remove(point)
			return True
		except ValueError as e:
			self.__last_error_message = str(e) + '\nGeoPoint with ID ' + str(point.id) + ' not found in list!'
			raise ValueError(self.__last_error_message)

	def deletePointByCoordinates(self, easting, northing, altitude):
		"""@ParamType easting float
		@ParamType northing float
		@ParamType altitude float"""
		try:
			easting = float( easting )
			northing = float( northing )
			altitude = float( altitude )
		except ValueError:
			self.__last_error_message = 'On of the input coordinates is not of type float!'
			raise ValueError(self.__last_error_message)

		for pnt in self.points[:]:
			if (pnt.easting == easting) and (pnt.northing == northing) and (pnt.altitude == altitude):
				self.points.remove(pnt)
				return True
		self.__last_error_message = 'Point not found with coordinates {0}/{1}/{2}'.format(easting, northing, altitude)
		raise ValueError(self.__last_error_message)

	def save_to_db(self, handler):
		"""@ParamType handler DBHandler"""
		session = handler.get_session()
		session.add(self)
		try:
			session.commit()
		except IntegrityError as e:
			print('Cannot commit changes, Integrity Error (double unique values?)')
			print(e)
			session.rollback()

	def last_error_message(self):
		"""@ReturnType string"""
		return self.__last_error_message
