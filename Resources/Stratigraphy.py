# -*- coding: UTF-8 -*-

from Resources.DBHandler import Base
import sqlalchemy as sq


class Stratigraphy(Base):
	__tablename__ = 'stratigraphy'

	id = sq.Column(sq.INTEGER, sq.Sequence('horizons_id_seq'), primary_key=True)
	name = sq.Column(sq.TEXT(50), unique=True)
	age = sq.Column(sq.INTEGER())

	def __init__(self, name, age=-1):
		self.name = name
		self.age = age

	def __repr__(self):
		return "<StratigraphicHorizon(id='{}', name='{}', age='{}')>".format(self.id, self.name, self.age)

	def __str__(self):
		return "horizon [{}]: name='{}', age='{}'".format(self.id, self.name, self.age)
