# -*- coding: UTF-8 -*-
"""
This module hosts the basic GeoObject class. This class inherits all basic function for GeoObjects
"""

import sqlalchemy as sq
from sqlalchemy.orm.session import Session

from Resources.DBHandler import DBObject


class GeoObject(DBObject):
    """
    This is a base class which stores central GeoObject data
    """

    east = sq.Column(sq.REAL(10, 4))
    north = sq.Column(sq.REAL(10, 4))
    alt = sq.Column(sq.REAL(10, 4))

    def __init__(self, reference_system, easting, northing, altitude, session, name="", comment=""):
        # type: (str, float, float, float, Session, str, str) -> None
        """
        Initialise the GeoObject

        :param reference_system: Stores the spatial reference information in WKT format. This parameter is not checked
                                  for correctness!
        :type reference_system: str

        :param easting: easting coordinate of the object
        :type easting: float

        :param northing: northing coordinate of the object
        :type northing: float

        :param altitude: height above sea level of the object or None
        :type altitude: float or None

        :param session: session object create by SQLAlchemy sessionmaker
        :type session: Session

        :param name: name of the line with the aim to have the possibility to group more lines to a line-set
        :type name: str

        :param comment: additional comment
        :type comment: str

        :return: nothing
        """

        self.reference_system = reference_system
        self.easting = easting
        self.northing = northing
        self.altitude = altitude

        # call constructor of base class
        DBObject.__init__(self, session, name, comment)

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

    @property
    def reference_system(self):
        # type: () -> str
        """
        Returns the current reference system in WKT format
        ATTENTION: The reference system is not checked!

        :return: Returns the current reference system
        """
        return self.reference

    @reference_system.setter
    def reference_system(self, reference):
        # type: (str) -> None
        """
        Sets a new reference system in WKT format.
        ATTENTION: The reference system will not be checked!

        :param reference: the new reference system in WKT format
        :type reference: str

        :return: Nothing
        """
        self.reference = str(reference)

    @classmethod
    def load_in_extent_from_db(cls, session, min_easting, max_easting, min_northing, max_northing):
        # type: (Session, float, float, float, float) -> List[cls]
        """
        Returns all points inside the given extent in the database connected to the SQLAlchemy Session session

        :param min_easting: minimal easting of extent
        :type min_easting: float

        :param max_easting: maximal easting of extent
        :type max_easting: float

        :param min_northing: minimal northing of extent
        :type min_northing: float

        :param max_northing: maximal northing of extent
        :type max_northing: float

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session

        :return: a list of points representing the result of the database query
        :rtype: List[cls]
        """
        result = session.query(cls).filter(sq.between(cls.east, min_easting, max_easting)). \
            filter(sq.between(cls.north, min_northing, max_northing))
        result = result.order_by(cls.id).all()
        for obj in result:
            obj.session = session
        return result
