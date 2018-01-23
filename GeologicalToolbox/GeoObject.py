# -*- coding: UTF-8 -*-
"""
This module hosts the basic AbstractGeoObject class. This class inherits all basic function for GeoObjects
"""

import sqlalchemy as sq
from sqlalchemy.orm.session import Session
from typing import List

from GeologicalToolbox.DBHandler import AbstractDBObject


class AbstractGeoObject(AbstractDBObject):
    """
    This is a base class which stores central GeoObject data. This class should be treated as abstract, no object
    should be created directly!
    """

    east = sq.Column(sq.FLOAT)
    north = sq.Column(sq.FLOAT)
    alt = sq.Column(sq.FLOAT)
    reference = sq.Column(sq.TEXT(1000), default='')

    def __init__(self, reference_system, easting, northing, altitude, *args, **kwargs):
        # type: (str, float, float, float, *object, **object) -> None
        """
        Initialise the AbstractGeoObject

        :param reference_system: Stores the spatial reference information in WKT format. This parameter is not checked
                                 for correctness!
        :type reference_system: str
        :param easting: easting coordinate of the object
        :type easting: float
        :param northing: northing coordinate of the object
        :type northing: float
        :param altitude: height above sea level of the object or None
        :type altitude: float or None
        :param args: parameters for AbstractDBObject initialisation
        :type args: List()
        :param kwargs: parameters for AbstractDBObject initialisation
        :type kwargs: Dict()
        :return: nothing
        """

        self.reference_system = reference_system
        self.easting = easting
        self.northing = northing
        self.altitude = altitude

        # call constructor of base class
        AbstractDBObject.__init__(self, *args, **kwargs)

    def __repr__(self):
        # type: () -> str
        """
        Returns a string representation of the AbstractGeoObject

        :return: Returns a string representation of the AbstractGeoObject
        :rtype: str
        """
        text = "<AbstractGeoObject(east='{}', north='{}', alt='{}')>\n".format(self.easting, self.northing, self.altitude)
        text += AbstractDBObject.__repr__(self)
        return text

    def __str__(self):
        # type: () -> str
        """
        Returns a string representation of the AbstractGeoObject

        :return: Returns a string representation of the AbstractGeoObject
        :rtype: str
        """
        text = "{} - {} - {} - ".format(self.easting, self.northing, self.altitude)
        text += AbstractDBObject.__str__(self)
        return text

    # define setter and getter for columns and local data
    @property
    def easting(self):
        # type: () -> float
        """
        The easting value of the object

        :type: float
        :raises ValueError: if value is not compatible to type float
        """
        return float(self.east)

    @easting.setter
    def easting(self, value):
        # type: (float) -> None
        """
        see getter
        """
        self.east = float(value)

    @property
    def northing(self):
        # type: () -> float
        """
        The northing value of the object

        :type: float
        :raises ValueError: if value is not compatible to type float
        """
        return float(self.north)

    @northing.setter
    def northing(self, value):
        # type: (float) -> None
        """
        see getter
        """
        self.north = float(value)

    @property
    def altitude(self):
        # type: () -> float
        """
        The height above sea level of the object

        :type: float
        :raises ValueError: if value is not compatible to type float
        """
        return float(self.alt)

    @altitude.setter
    def altitude(self, value):
        # type: (float) -> None
        """
        see getter
        """
        self.alt = float(value)

    @property
    def reference_system(self):
        # type: () -> str
        """
        The reference system in WKT format
        ATTENTION: The reference system is not checked!

        :return: Returns the current reference system
        :type: str
        """
        return self.reference

    @reference_system.setter
    def reference_system(self, reference):
        # type: (str) -> None
        """
        see getter
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
        :raises ValueError: if one of the extension values is not compatible to type float
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        min_easting = float(min_easting)
        max_easting = float(max_easting)
        min_northing = float(min_northing)
        max_northing = float(max_northing)

        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        result = session.query(cls).filter(sq.between(cls.east, min_easting, max_easting)). \
            filter(sq.between(cls.north, min_northing, max_northing))
        result = result.order_by(cls.id).all()
        for obj in result:
            obj.session = session
        return result
