# -*- coding: UTF-8 -*-

import Resources.GeoPoint as GeoPoint
from Resources.DBHandler import Base


class Line(Base):
	def __init__ ( self ):
		self.__lineID = -1
		"""@AttributeType int"""
		self.__closed = False
		"""@AttributeType bool"""
		self.__lastErrorMessage = ""
		"""@AttributeType string"""
		self.__points = [ ]

	# @AssociationType GeoPoint
	# @AssociationMultiplicity 2..*

	def getLineID ( self ):
		"""@ReturnType int"""
		return self.__lineID

	def getPoints ( self ):
		"""@ReturnType GeoPoint []"""
		return self.__points

	def isClosed ( self ):
		"""@ReturnType bool"""
		return self.__closed

	def setLineID ( self, ID ):
		"""@ParamType ID int
		@ReturnType bool"""
		# if type(ID) != int or cannot be converted, then raise a ValueError
		try:
			ID = int( ID )
		except ValueError as e:
			self.__lastErrorMessage = 'Cannot convert new lineID to an integer value!'
			raise ValueError( e )

		self.__lineID = ID
		return True

	def insertPoint ( self, point, position ):
		"""@ParamType point GeoPoint
		@ParamType position int
		@ReturnType bool"""
		if type( point ) is GeoPoint:
			self.__points.insert( position, point )
			return True
		else:
			self.__lastErrorMessage = 'point is not of type GeoPoint!'
			raise TypeError( 'point is not of type GeoPoint!' )

	def insertPoints ( self, points, position ):
		"""@ParamType points GeoPoint[]
		@ParamType position int
		@ReturnType bool"""

		if type( position ) is int:
			self.__lastErrorMessage( 'Position is not of type int!' )
			raise TypeError( 'Position is not of type int!' )

		for pnt in points:
			if type( pnt ) is not GeoPoint:
				self.__lastErrorMessage( 'At least on point in points is not of type GeoPoint!' )
				raise TypeError( 'At least on point in points is not of type GeoPoint!' )
		# use slicing for points insert
		self.__points[ position:position ] = points
		return True

	# for point in points: self.__points.insert( position + points.index( point ), point )

	def getPointIndex ( self, point ):
		"""@ParamType point GeoPoint
		@ReturnType int"""
		return self.__points.index( point )

	def deletePoint ( self, pointID ):
		"""@ParamType pointID int"""
		pointID = int( pointID )

		for i in range( len( self.__points ) ):
			if self.__points[ i ].getPointID() == pointID:
				self.__points.pop( i )
				return True

		self.__lastErrorMessage = 'Geopoint with ID ' + str( pointID ) + ' not found!'
		raise ValueError( self.__lastErrorMessage )

	def deletePoint ( self, easting, northing, altitude ):
		"""@ParamType east float
		@ParamType north float
		@ParamType alt float"""
		try:
			easting = float( easting )
			northing = float( northing )
			altitude = float( altitude )
		except ValueError:
			self.__lastErrorMessage = 'On of the input coordinates is not of type float!'
			raise ValueError( self.__lastErrorMessage )

		for i in range( len( self.__points ) ):
			pnt = self.__points[ i ]
			if (pnt.getEasting() == easting) and (pnt.getNorthing() == northing) and (pnt.getAltitude() == altitude):
				self.__points.pop( i )
				return True

		self.__lastErrorMessage = 'Point not found with coordinates {0}/{1}/{2}'.format( easting, northing, altitude )
		raise ValueError( self.__lastErrorMessage )

	def deleteGeoPoint ( self, point ):
		"""@ParamType point GeoPoint
		@ReturnType bool"""
		pass

	def saveLineToDB ( self, handler ):
		"""@ParamType handler DBHandler"""
		pass

	def getLastErrorMessage ( self ):
		"""@ReturnType string"""
		pass

	def setClosed ( self, val ):
		"""@ParamType val bool
		@ReturnType bool"""
		pass
