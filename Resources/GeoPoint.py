# -*- coding: UTF-8 -*-

from Resources.DBHandler import Base


class GeoPoint(Base):
	def __init__ ( self ):
		self.__easting = 0
		"""@AttributeType float"""
		self.__northing = 0
		"""@AttributeType float"""
		self.__altitude = 0
		"""@AttributeType float"""
		self.__pointID = -1
		"""@AttributeType float"""
		self.__horizon = ""
		"""@AttributeType string"""
		self.__lastErrorMessage = ""
		"""@AttributeType string"""

	def getAltitude ( self ):
		"""@ReturnType float"""
		return self.__altitude

	def getEasting ( self ):
		"""@ReturnType float"""
		return self.__easting

	def getHorizon ( self ):
		"""@ReturnType string"""
		return self.__horizon

	def getNorthing ( self ):
		"""@ReturnType float"""
		return self.__northing

	def getPointID ( self ):
		"""@ReturnType int"""
		self.__pointID

	def setAltitude ( self, alt ):
		"""@ParamType alt float"""
		try:
			self.__altitude = float( alt )
			return True
		except ValueError:
			self.__lastErrorMessage = 'Cannot convert value to float: ' + str( alt )
			raise ValueError(self.__lastErrorMessage)

	def setEasting ( self, east ):
		"""@ParamType east float"""
		try:
			self.__altitude = float( east )
			return True
		except ValueError:
			self.__lastErrorMessage = 'Cannot convert value to float: ' + str( east )
			raise ValueError(self.__lastErrorMessage)

	def setHorizon ( self, hor ):
		"""@ParamType hor string"""
		try:
			self.__altitude = str( hor )
			return True
		except ValueError:
			self.__lastErrorMessage = 'Cannot set horizon string: ' + str( hor )
			raise ValueError(self.__lastErrorMessage)

	def setNorthing ( self, north ):
		"""@ParamType north double"""
		try:
			self.__altitude = float( north )
			return True
		except ValueError:
			self.__lastErrorMessage = 'Cannot convert value to float: ' + str( north )
			raise ValueError(self.__lastErrorMessage)

	def setPointID ( self, ID ):
		"""@ParamType ID int"""
		try:
			self.__altitude = int( ID )
			return True
		except ValueError:
			self.__lastErrorMessage = 'Cannot convert value to ID (integer): ' + str( ID )
			raise ValueError(self.__lastErrorMessage)

	def savePointToDB ( self, handler ):
		"""@ParamType handler DBHandler"""
		handler.insertPoint(self)

	def getLastErrorMessage ( self ):
		"""@ReturnType string"""
		return self.__lastErrorMessage;
