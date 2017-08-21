# -*- coding: UTF-8 -*-

class DatabaseException(Exception):
	def __init__(self, msg):
		self.__msg = msg

	def __str__(self):
		return self.__msg
