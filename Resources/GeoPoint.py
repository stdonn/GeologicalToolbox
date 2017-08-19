# -*- coding: UTF-8 -*-

import sqlalchemy as sq
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError

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

	line_id = sq.Column(sq.INTEGER, sq.ForeignKey('lines.id'))
	line = relationship("Line", back_populates="points")

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