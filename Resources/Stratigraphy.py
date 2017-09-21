# -*- coding: UTF-8 -*-

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError

from Exceptions import DatabaseException
from Resources.DBHandler import Base


class Stratigraphy(Base):
	__tablename__ = 'stratigraphy'

	id = sq.Column(sq.INTEGER, sq.Sequence('strat_id_seq'), primary_key=True)
	name = sq.Column(sq.TEXT(50), unique=True)
	age = sq.Column(sq.INTEGER(), default=-1)

	def __init__(self, session, name, age=-1, update=False):
		self.__session = session
		self.horizon = name
		if update or (self.age is None):
			self.age = age

	def __repr__(self):
		return "<StratigraphicHorizon(id='{}', name='{}', age='{}')>".format(self.id, self.name, self.age)

	def __str__(self):
		return "horizon [{}]: name='{}', age='{}'".format(self.id, self.name, self.age)

	@property
	def horizon_age(self):
		return self.age

	@horizon_age.setter
	def horizon_age(self, value):
		if value <= -1:
			self.age = -1
		else:
			self.age = value

	@property
	def horizon(self):
		return self.name

	@horizon.setter
	def horizon(self, value):
		result = self.__session.query(Stratigraphy).filter(Stratigraphy.name == value)
		if result.count() == 0:
			self.name = value
			self.age = None
		elif result.count() == 1:
			self.name = result.one().horizon
			self.age = result.one().age
			self.id = result.one().id
			#print("Found horizon in db:")
			#print(str(result.one()))
			#print(str(self))
		else:
			for res in result.all():
				print(res)
			raise DatabaseException('More than one ({}) horizon with the same name: {}! Database error!'
			                        .format(result.count(), value.name))
	@property
	def session(self):
		return self.__session

	@session.setter
	def session(self, value):
		self.__session = value

	def save_to_db(self):
		self.__session.add(self)
		try:
			self.__session.commit()
		except IntegrityError as e:
			print('Cannot commit changes in stratigraphy table, Integrity Error (double unique values?)')
			print(e)
			self.__session.rollback()
