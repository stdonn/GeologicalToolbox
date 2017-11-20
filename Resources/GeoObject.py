# -*- coding: UTF-8 -*-
"""
This module hosts the basic GeoObject class. This class inherits all basic function for GeoObjects
"""

import sqlalchemy as sq


class GeoObject:
    """
    This is a base class which stores central GeoObject data
    """

    east = sq.Column(sq.REAL(10, 4))
    north = sq.Column(sq.REAL(10, 4))
    alt = sq.Column(sq.REAL(10, 4))

    def __init__(self, spatial_reference, easting, northing, altitude):
        # type: (str, float, float, float) -> None
        """
        Initialise the
        :param spatial_reference: Stores the spatial reference information in WKT format. This parameter is not checked
                                  for correctness!
        :type spatial_reference: str

        :param easting: easting coordinate of the object
        :type easting: float

        :param northing: northing coordinate of the object
        :type northing: float

        :param altitude: height above sea level of the object or None
        :type altitude: float or None

        :return: nothing

        """

        self.reference = spatial_reference
        self.easting = easting
        self.northing = northing
        self.altitude = altitude

    # define setter and getter for columns and local data
    @property
    def easting(self):
        # type: () -> float
        """
        Returns the easting value of the point.

        :return: Returns the easting value of the point.
        :rtype: float
        """
        return float(self.east)

    @easting.setter
    def easting(self, value):
        # type: (float) -> None
        """
        Sets a new easting value

        :param value: new easting value
        :type value: float

        :return: Nothing
        :raises ValueError: Raises ValueError if value if not of type float or cannot be converted to float
        """
        self.east = float(value)

    @property
    def northing(self):
        # type: () -> float
        """
        Returns the northing value of the point.

        :return: Returns the northing value of the point.
        :rtype: float
        """
        return float(self.north)

    @northing.setter
    def northing(self, value):
        # type: (float) -> None
        """
        Sets a new northing value

        :param value: new northing value
        :type value: float

        :return: Nothing
        :raises ValueError: Raises ValueError if value if not of type float or cannot be converted to float
        """
        self.north = float(value)

    @property
    def altitude(self):
        # type: () -> float
        """
        Returns the height above sea level of the point.
        If the point has no z-value (check with GeoPoint.has_z()), 0 will be returned.

        :return: Returns the height above sea level of the point.
        :rtype: float
        """
        return float(self.alt)

    @altitude.setter
    def altitude(self, value):
        # type: (float) -> None
        """
        Sets a new height above sea level

        :param value: New height above sea level
        :type value: float

        :return: Nothing
        :raises ValueError: Raises ValueError if value if not of type float or cannot be converted to float
        """
        self.alt = float(value)
