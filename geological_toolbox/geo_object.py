# -*- coding: UTF-8 -*-
"""
This module hosts the basic AbstractGeoObject class. In declares all basic functions for a GeoObjects
"""

import sqlalchemy as sq
from sqlalchemy.orm.session import Session
from typing import List

from geological_toolbox.db_handler import AbstractDBObject


class AbstractGeoObject(AbstractDBObject):
    """
    This is a base class which stores central GeoObject data. This class should be treated as abstract, no object
    should be created directly!

    :param reference_system: Stores the spatial reference information in a string format (e.g. WKT). This parameter will
           not be verified!
    :param easting: easting coordinate of the object
    :param northing: northing coordinate of the object
    :param altitude: height above sea level of the object or None
    :param args: parameters for AbstractDBObject initialisation
    :param kwargs: parameters for AbstractDBObject initialisation
    :return: nothing
    """

    east = sq.Column(sq.FLOAT)
    north = sq.Column(sq.FLOAT)
    alt = sq.Column(sq.FLOAT)
    reference = sq.Column(sq.TEXT, default="")

    def __init__(self, reference_system: str, easting: float, northing: float, altitude: float,
                 *args, **kwargs) -> None:
        """
        Initialise the AbstractGeoObject
        """

        self.reference_system = reference_system
        self.easting = easting
        self.northing = northing
        self.altitude = altitude

        # call constructor of base class
        AbstractDBObject.__init__(self, *args, **kwargs)

    def __repr__(self) -> str:
        text = "<AbstractGeoObject(east='{}', north='{}', alt='{}')>\n".format(self.easting, self.northing,
                                                                               self.altitude)
        text += AbstractDBObject.__repr__(self)
        return text

    def __str__(self) -> str:
        text = "{} - {} - {} - ".format(self.easting, self.northing, self.altitude)
        text += AbstractDBObject.__str__(self)
        return text

    # define setter and getter for columns and local data
    @property
    def easting(self) -> float:
        """
        The easting value of the object

        :raises ValueError: if value is not compatible to type float
        """
        return float(self.east)

    @easting.setter
    def easting(self, value: float) -> None:
        """
        see getter
        """
        self.east = float(value)

    @property
    def northing(self) -> float:
        """
        The northing value of the object

        :raises ValueError: if value is not compatible to type float
        """
        return float(self.north)

    @northing.setter
    def northing(self, value: float) -> None:
        """
        see getter
        """
        self.north = float(value)

    @property
    def altitude(self) -> float:
        """
        The height above sea level of the object

        :raises ValueError: if value is not compatible to type float
        """
        return float(self.alt)

    @altitude.setter
    def altitude(self, value: float) -> None:
        """
        see getter
        """
        self.alt = float(value)

    @property
    def reference_system(self) -> str:
        """
        The reference system in string format (e.g. WKT)
        ATTENTION: The reference system won't be verified

        :return: Returns the current reference system
        """
        return self.reference

    @reference_system.setter
    def reference_system(self, reference: str) -> None:
        """
        see getter
        """
        self.reference = str(reference)

    @classmethod
    def load_in_extent_from_db(cls, session: Session, min_easting: float, max_easting: float, min_northing: float,
                               max_northing: float) -> List["AbstractGeoObject"]:
        """
        Returns all objects inside the given extent in the database connected to the SQLAlchemy Session session.

        :param session: represents the database connection as SQLAlchemy Session
        :param min_easting: minimal easting of extent
        :param max_easting: maximal easting of extent
        :param min_northing: minimal northing of extent
        :param max_northing: maximal northing of extent
        :return: a list of objects representing the result of the database query
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
