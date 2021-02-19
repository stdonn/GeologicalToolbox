# -*- coding: UTF-8 -*-
"""
This module provides classes for storage of drilling data in a database.
"""

import sqlalchemy as sq
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from typing import List

from geological_toolbox.exceptions import DatabaseException, WellMarkerDepthException
from geological_toolbox.geo_object import AbstractGeoObject
from geological_toolbox.geometries import GeoPoint
from geological_toolbox.well_logs import WellLog
from geological_toolbox.db_handler import Base, AbstractDBObject
from geological_toolbox.stratigraphy import StratigraphicObject


class WellMarker(Base, AbstractDBObject):
    """
    Represents single markers in a drilled well

    :param depth: depth below Kelly Bushing
    :param horizon: stratigraphic object
    :raises TypeError: if one of the committed parameters cannot be converted to the expected type
    """
    __tablename__ = "well_marker"

    id = sq.Column(sq.INTEGER, sq.Sequence("well_marker_id_seq"), primary_key=True)
    drill_depth = sq.Column(sq.FLOAT)

    # define relationship to stratigraphic table
    horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey("stratigraphy.id"))
    hor = relationship("StratigraphicObject")

    well_id = sq.Column(sq.INTEGER, sq.ForeignKey("wells.id"), default=-1)

    def __init__(self, depth: float, horizon: StratigraphicObject, *args, **kwargs) -> None:
        """
        initialize the class
        """
        AbstractDBObject.__init__(self, *args, **kwargs)

        self.depth = float(depth)
        self.horizon = horizon

    def __repr__(self) -> str:
        return "<WellMarker(id='{}', depth='{}', horizon='{}'\nAbstractObject: {}". \
            format(self.id, self.depth, self.horizon, AbstractDBObject.__repr__(self))

    def __str__(self) -> str:
        return "[{}] {}: {} - {}".format(self.id, self.depth, self.horizon, AbstractDBObject.__str__(self))

    @property
    def depth(self) -> float:
        """
        depth of the well marker

        :return: depth of the well marker.
        :raises ValueError: if value if not of type float or cannot be converted to float
        """
        return float(self.drill_depth)

    @depth.setter
    def depth(self, value: float) -> None:
        """
        see getter
        """
        self.drill_depth = float(value)

    @property
    def horizon(self) -> StratigraphicObject:
        """
        stratigraphic object of the point

        :return: stratigraphic object of the point
        :raises TypeError: if value is not of type StratigraphicObject
        """
        return self.hor

    @horizon.setter
    def horizon(self, value: StratigraphicObject) -> None:
        """
        see getter
        """
        if (value is not None) and (type(value) is not StratigraphicObject):
            raise TypeError("type of committed value ({}) is not StratigraphicObject!".format(type(value)))

        if value is None:
            self.hor = None
            self.horizon_id = -1
        else:
            self.hor = value

    def to_geopoint(self) -> GeoPoint:
        """
        Returns the current well marker as GeoPoint

        :return: the current well marker as GeoPoint
        """
        easting = self.well.easting
        northing = self.well.northing
        altitude = self.well.altitude - self.depth
        return GeoPoint(self.horizon, True, self.well.reference_system, easting, northing, altitude, self.session,
                        self.well.well_name, self.comment)

    @classmethod
    def load_in_extent_from_db(cls, session: Session, min_easting: float, max_easting: float, min_northing: float,
                               max_northing: float) -> List["WellMarker"]:
        """
        Returns all well marker within the given extent in the database connected to the SQLAlchemy Session session

        :param min_easting: minimal easting of extent
        :param max_easting: maximal easting of extent
        :param min_northing: minimal northing of extent
        :param max_northing: maximal northing of extent
        :param session: represents the database connection as SQLAlchemy Session
        :return: a list of WellMarker representing the result of the database query
        """
        result = session.query(cls, Well). \
            filter(Well.id == cls.well_id). \
            filter(sq.between(Well.east, min_easting, max_easting)). \
            filter(sq.between(Well.north, min_northing, max_northing)). \
            order_by(cls.id).all()
        for marker in result:
            marker.session = session
        return result

    @classmethod
    def load_all_by_stratigraphy_from_db(cls, horizon: StratigraphicObject, session: Session) -> List["WellMarker"]:
        """
        Returns all WellMarker in the database which are related to the StratigraphicObject "horizon"

        :param horizon: stratigraphic object for the database query
        :param session: represents the database connection as SQLAlchemy Session
        :return: a list of WellMarker
        """
        return session.query(cls).filter(WellMarker.horizon_id == horizon.id)

    @classmethod
    def load_all_by_stratigraphy_in_extent_from_db(cls, horizon: StratigraphicObject, min_easting: float,
                                                   max_easting: float, min_northing: float, max_northing: float,
                                                   session: Session) -> List["WellMarker"]:
        """
        Returns all WellMarker in the database which are related to the StratigraphicObject "horizon" and are located
        within the given extent

        :param horizon: stratigraphic object for the database query
        :param min_easting: minimal easting of extent
        :param max_easting: maximal easting of extent
        :param min_northing: minimal northing of extent
        :param max_northing: maximal northing of extent
        :param session: represents the database connection as SQLAlchemy Session
        :return: a list of WellMarker
        """
        result = session.query(cls, Well). \
            filter(cls.horizon_id == horizon.id). \
            filter(Well.id == cls.well_id). \
            filter(sq.between(Well.east, min_easting, max_easting)). \
            filter(sq.between(Well.north, min_northing, max_northing)). \
            order_by(cls.id).all()
        for marker in result:
            marker.session = session
        return result


class Well(Base, AbstractGeoObject):
    """
    Represents a well for storage of geoscientific data.

    :param session: SQLAlchemy session, which includes the database connection
    :param well_name: well name
    :param short_name: shortened well name
    :param depth: drilled depth of the well
    :raises ValueError: Raises ValueError if one of the types cannot be converted
    """
    __tablename__ = "wells"

    id = sq.Column(sq.INTEGER, sq.Sequence("wells_id_seq"), primary_key=True)
    drill_depth = sq.Column(sq.FLOAT)
    wellname = sq.Column(sq.VARCHAR(100), unique=True)
    shortwellname = sq.Column(sq.VARCHAR(100), default="")

    # define markers relationship
    marker: List[WellMarker] = relationship("WellMarker", order_by=WellMarker.drill_depth,
                                            backref="well", primaryjoin="Well.id == WellMarker.well_id",
                                            cascade="all, delete, delete-orphan")

    logs: List[WellLog] = relationship("WellLog", order_by=WellLog.id,
                                       backref="well", primaryjoin="Well.id == WellLog.well_id",
                                       cascade="all, delete, delete-orphan")

    sq.Index("coordinate_index", AbstractGeoObject.east, AbstractGeoObject.north)

    def __init__(self, well_name: str, short_name: str, depth: float, *args, **kwargs) -> None:
        """
        initialize the class
        """

        self.depth = depth
        self.well_name = well_name
        self.short_name = short_name

        # call base class constructor
        AbstractGeoObject.__init__(self, *args, **kwargs)

    def __repr__(self) -> str:
        return "<Well(id='{}', well_name='{}', short_name='{}', depth='{}', marker='{}', logs='{}', comment='{}'," + \
               " marker='{}')>".format(self.id, self.well_name, self.short_name, self.easting, self.northing,
                                       self.altitude, self.depth, self.comment, repr(self.marker))

    def __str__(self) -> str:
        text = "[{}] {} ({}):\n{} - {} - {} - {} - {}" \
            .format(self.id, self.well_name, self.short_name, self.easting, self.northing, self.altitude, self.depth,
                    self.comment)

        for marker in self.marker:
            text += "\n" + str(marker)

        return text

    @property
    def depth(self) -> float:
        """
        total drilling depth of the well

        :raises ValueError: Raises ValueError if depth is not of type float, it cannot be converted to float or when
                            depth is < 0
        """
        return float(self.drill_depth)

    @depth.setter
    def depth(self, dep: float) -> None:
        """
        see getter
        """
        dep = float(dep)
        if dep < 0:
            raise ValueError("Depth is below 0! ({})".format(dep))
        if (len(self.marker) > 0) and (dep < self.marker[-1].depth):
            raise WellMarkerDepthException(
                "New depth ({}) lower than depth of last marker {}".format(dep, self.marker[-1].depth))
        self.drill_depth = dep

    @property
    def well_name(self) -> str:
        """
        unique name of the well
        """
        return self.wellname

    @well_name.setter
    def well_name(self, well_name: str) -> None:
        """
        see getter
        """
        well_name = str(well_name)
        if len(well_name) > 100:
            well_name = well_name[:100]
        self.wellname = well_name

    @property
    def short_name(self) -> str:
        """
        shortend name of the well
        """
        return self.shortwellname

    @short_name.setter
    def short_name(self, short_name: str) -> None:
        """
        see getter
        """
        short_name = str(short_name)
        if len(short_name) > 20:
            short_name = short_name[:20]
        self.shortwellname = short_name

    def insert_marker(self, marker: WellMarker) -> None:
        """
        Insert a new WellMarker
        ATTENTION: If you insert a marker, the well will be automatically stored in the database!

        :param marker: WellMarker to be inserted
        :return: Nothing
        :raises TypeError: if marker is not of type WellMarker
        :raises ValueError: if the depth of the marker is larger than the drilled depth of the well
        """
        if type(marker) is not WellMarker:
            raise TypeError("marker {} is not of type WellMarker!".format(str(marker)))
        if marker.depth > self.depth:
            raise ValueError("Marker depth ({}) is larger than final well depth ({})!".format(marker.depth, self.depth))
        self.marker.append(marker)

        # new sorting to ensure correct order without storage and reloading from the database
        self.marker.sort(key=lambda x: x.depth)

    def insert_multiple_marker(self, marker: List[WellMarker]) -> None:
        """
        Insert multiple marker in the well
        ATTENTION: If you insert marker, the well will be automatically stored in the database!

        :param marker: List of marker to be inserted
        :return: Nothing
        :raises TypeError: if one of the marker is not of type WellMarker
        :raises ValueError: if the depth of a marker is larger than the drilled depth of the well
        """
        for mark in marker:
            if type(mark) is not WellMarker:
                raise TypeError(
                    "At least on marker is not of type WellMarker ({}: {})!".format(str(mark), str(type(mark))))
            if mark.depth > self.depth:
                raise ValueError("Marker depth ({}) is larger than final well depth ({})!".
                                 format(mark.depth, self.depth))

        self.marker += marker

        # new sorting to ensure correct order without storage and reloading from the database
        self.marker.sort(key=lambda x: x.depth)

    def get_marker_by_depth(self, depth: float) -> WellMarker or None:
        """
        Returns the marker at depth "depth"

        :param depth: depth of the requested marker
        :return: the marker at depth "depth"
        :raises ValueError: if no marker was found for the committed depth or depth is not compatible to float
        """
        depth = float(depth)
        for marker in self.marker:
            if marker.depth == depth:
                return marker
        raise ValueError("No marker found at depth {}".format(depth))

    def delete_marker(self, marker: WellMarker) -> None:
        """
        Deletes the marker from the well

        :param marker: WellMarker object which should be deleted
        :return: Nothing
        :raises TypeError: if marker is not of type WellMarker
        :raises ValueError: the marker is not part of the well
        """
        if type(marker) is not WellMarker:
            raise TypeError("marker {} is not of type WellMarker!".format(str(marker)))

        try:
            self.marker.remove(marker)
            WellMarker.delete_from_db(marker, self.session)
        except ValueError as e:
            raise ValueError(str(e) + "\nWellMarker with ID " + str(marker.id) + " not found in list!")

    def add_log(self, log: WellLog) -> None:
        """
        Adds a new log to the well

        :param log: new well log
        :return: Nothing
        :raises TypeError: if log is not of type WellLog
        """
        if type(log) is not WellLog:
            raise TypeError("log {} is not of type WellLog!".format(str(log)))

        self.logs.append(log)

    def delete_log(self, log: WellLog) -> None:
        """
        Deletes the log from the well

        :param log: log to delete
        :return: Nothing
        :raises TypeError: if log is not of type WellLog
        :raises ValueError: if log is not part of the well
        """
        if type(log) is not WellLog:
            raise TypeError("log {} is not of type WellLog!".format(str(log)))

        try:
            self.logs.remove(log)
        except ValueError as e:
            raise ValueError(str(e) + "\nWellLog with ID " + str(log.id) + " not found in list!")

    def get_log(self, log_name: str) -> WellLog or None:
        """
        Returns the log with log-name name or none
        :param log_name: log to search
        :return: resulting WellLog object or None
        """
        for log in self.logs:
            if log.property_name == name:
                return log
        return None

    def has_log(self, log_name: str) -> bool:
        """
        Return true if the well has a log with name log_name, else False
        :param log_name: name of the requested log
        :return: true if the well has a log with name log_name, else False
        """
        for log in self.logs:
            if log.property_name == name:
                return True
        return False

    @classmethod
    def load_by_wellname_from_db(cls, name: str, session: Session) -> "Well" or None:
        """
        Returns the well with the given name in the database connected to the SQLAlchemy Session session

        :param name: name of the requested well
        :param session: represents the database connection as SQLAlchemy Session
        :return: As the name is a unique value, only one result can be returned or None
        :raises DatabaseException: if more than one result was found (the well name is an unique value)
        """
        result = session.query(cls).filter(cls.wellname == name)
        if result.count() == 0:
            return None
        if result.count() == 1:
            result = result.one()
            result.session = session
            return result

        raise DatabaseException("More than one ({}) well with the same name: {}! Database error!".
                                format(result.count(), name))

    @classmethod
    def load_deeper_than_value_from_db(cls, session: Session, min_depth: float) -> List["Well"]:
        """
        Returns all wells with a drilled depth larger than min_depth in the database connected to the SQLAlchemy Session
        session

        :param min_depth: minimal drilled depth
        :param session: represents the database connection as SQLAlchemy Session
        :return: a list of wells representing the result of the database query
        """
        result = session.query(cls).filter(cls.drill_depth >= min_depth)
        result = result.order_by(cls.id).all()
        for well in result:
            well.session = session
        return result
