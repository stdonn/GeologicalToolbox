# -*- coding: UTF-8 -*-

import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class DBHandler:
	def __init__(self, connection='sqlite:///:memory:', debug=False):
		# type: (str, bool) -> None
		"""
		:rtype: None

		"""
		engine = sq.create_engine(connection, echo=debug)
		Base.metadata.create_all(engine)
		self.__Session = sessionmaker(bind=engine)

	def get_session(self):
		# type: () -> sessionmaker
		return self.__Session()