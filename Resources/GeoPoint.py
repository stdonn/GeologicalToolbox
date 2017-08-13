# -*- coding: UTF-8 -*-

import sqlalchemy as sq
from sqlalchemy.orm import relationship

from Resources.DBHandler import Base
# from Resources.Stratigraphy import Stratigraphy


class GeoPoint(Base):
	__tablename__ = 'geopoints'

	id = sq.Column(sq.INTEGER, sq.Sequence('horizons_id_seq'), primary_key=True)
	east = sq.Column(sq.REAL(10, 4))
	north = sq.Column(sq.REAL(10, 4))
	alt = sq.Column(sq.REAL(10, 4))
	age = sq.Column(sq.INTEGER())
	horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey('stratigraphy.id'))

	hor = relationship("Stratigraphy")

	def __init__(self, easting, northing, altitude, horizon):
		self.east = easting
		self.north = northing
		self.alt = altitude
		self.hor = horizon

	def __repr__(self):
		return "<GeoPoint(id='{}', east='{}', north='{}', alt='{}', horizon='{}')>"\
			.format(self.id, self.east, self.north, self.altitude, str(self.horizon))

	def __str__(self):
		return "[{}] {} - {} - {} : {}".format(self.id, self.east, self.north, self.altitude, str(self.horizon))

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
