# -*- coding: UTF-8 -*-
"""
This module provides classes for storing drilling data in a database.

.. todo:: - reformat docstrings, especially of setter and getter functions
          - check exception types
"""

import sqlalchemy as sq
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from typing import List

from GeologicalToolbox.Exceptions import DatabaseException, WellMarkerDepthException
from GeologicalToolbox.GeoObject import AbstractGeoObject
from GeologicalToolbox.Geometries import GeoPoint
from GeologicalToolbox.WellLogs import WellLog
from GeologicalToolbox.DBHandler import Base, AbstractDBObject
from GeologicalToolbox.Stratigraphy import StratigraphicObject


class WellMarker(Base, AbstractDBObject):
    """
    Class WellMarker

    Represents single markers in a drilled well
    """
    # define db table name and columns
    __tablename__ = 'well_marker'

    id = sq.Column(sq.INTEGER, sq.Sequence('wellmarker_id_seq'), primary_key=True)
    drill_depth = sq.Column(sq.FLOAT)

    # define relationship to stratigraphic table
    horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey('stratigraphy.id'))
    hor = relationship("StratigraphicObject")

    well_id = sq.Column(sq.INTEGER, sq.ForeignKey('wells.id'), default=-1)

    def __init__(self, depth, horizon, *args, **kwargs):
        # type: (float, StratigraphicObject, *object, **object) -> None
        """
        Creates a new well marker

        :param depth: depth below Kelly Bushing
        :type depth: float

        :param horizon: stratigraphy object
        :type horizon: StratigraphicObject

        :param args: parameters for AbstractDBObject initialisation
        :type args: List()

        :param kwargs: parameters for AbstractDBObject initialisation
        :type kwargs: Dict()

        :returns: Nothing
        :raises ValueError: Raises ValueError if one of the committed parameters cannot be converted to the expected type
        """
        AbstractDBObject.__init__(self, *args, **kwargs)
        if (type(horizon) is not StratigraphicObject) and (horizon is not None):
            raise ValueError("'horizon' value is not of type StratigraphicObject!")

        self.depth = float(depth)
        self.horizon = horizon

    def __repr__(self):
        # type: () -> str
        """
        Returns a text-representation of the well marker

        :return: Returns a text-representation of the well marker
        :rtype: str
        """
        return "<WellMarker(id='{}', depth='{}', horizon='{}'\nAbstractObject: {}". \
            format(self.id, self.depth, self.horizon, AbstractDBObject.__repr__(self))

    def __str__(self):
        # type: () -> str
        """
        Returns a text-representation of the well

        :return: Returns a text-representation of the well
        :rtype: str
        """
        return "[{}] {}: {} - {}".format(self.id, self.depth, self.horizon, AbstractDBObject.__str__(self))

    @property
    def depth(self):
        # type: () -> float
        """
        Returns the depth of the well marker below Kelly Bushing.

        :return: Returns the depth of the well marker below Kelly Bushing.
        :rtype: float
        """
        return float(self.drill_depth)

    @depth.setter
    def depth(self, value):
        # type: (float) -> None
        """
        Sets a new depth below Kelly Bushing for the well marker

        :param value: depth below Kelly Bushing
        :type value: float

        :return: Nothing
        :raises ValueError: Raises ValueError if value if not of type float or cannot be converted to float
        """
        self.drill_depth = float(value)

    @property
    def horizon(self):
        # type: () -> StratigraphicObject
        """
        Returns the stratigraphy of the point

        :return: Returns the current Stratigraphy
        :rtype: StratigraphicObject
        """
        return self.hor

    @horizon.setter
    def horizon(self, value):
        # type: (StratigraphicObject) -> None
        """
        sets a new stratigraphy

        :param value: new stratigraphy
        :type value: StratigraphicObject or None

        :return: Nothing

        :raises TypeError: Raises TypeError if value is not of type Stratigraphy
        """
        if (value is not None) and (type(value) is not StratigraphicObject):
            raise TypeError('type of commited value ({}) is not StratigraphicObject!'.format(type(value)))

        if value is None:
            self.hor = None
            self.horizon_id = -1
        else:
            self.hor = value

    def to_geopoint(self):
        # type: () -> GeoPoint
        """
        Returns the current well marker as GeoPoint

        :return: Returns the current well marker as GeoPoint
        :rtype: GeoPoint
        """
        easting = self.well.easting
        northing = self.well.northing
        altitude = self.well.altitude - self.depth
        return GeoPoint(self.horizon, True, self.well.reference_system, easting, northing, altitude, self.session,
                        self.well.well_name, self.comment)

    # load points from db
    @classmethod
    def load_in_extent_from_db(cls, session, min_easting, max_easting, min_northing, max_northing):
        # type: (Session, float, float, float, float) -> List[WellMarker]
        """
        Returns all well marker with committed horizon inside the given extent in the database connected to the
        SQLAlchemy Session session

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

        :return: a list of wells representing the result of the database query
        :rtype: List[WellMarker]
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
    def load_all_by_stratigraphy_from_db(cls, horizon, session):
        # type: (StratigraphicObject) -> List[WellMarker]
        """
        Returns all WellMarker in the database which are connected to the horizon 'horizon'

        :param horizon: stratigraphy for the database query
        :type horizon: StratigraphicObject

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session

        :return: a list of WellMarker
        :rtype: List[WellMarker]
        """
        return session.query(cls).filter(WellMarker.horizon_id == horizon.id)

    @classmethod
    def load_all_by_stratigraphy_in_extent_from_db(cls, horizon, min_easting, max_easting, min_northing, max_northing,
                                                   session):
        # type: (StratigraphicObject) -> List[WellMarker]
        """
        Returns all WellMarker in the database which are connected to the horizon 'horizon'

        :param horizon: stratigraphy for the database query
        :type horizon: StratigraphicObject

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

        :return: a list of WellMarker
        :rtype: List[WellMarker]
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
    Class Well

    Represents a well for storage of geoscientific data.
    """
    # define db table name and columns
    __tablename__ = 'wells'

    id = sq.Column(sq.INTEGER, sq.Sequence('well_id_seq'), primary_key=True)
    drill_depth = sq.Column(sq.FLOAT)
    wellname = sq.Column(sq.VARCHAR(100), unique=True)
    shortwellname = sq.Column(sq.VARCHAR(100), default="")

    # define markers relationship
    marker = relationship("WellMarker", order_by=WellMarker.drill_depth,
                          backref="well", primaryjoin='Well.id == WellMarker.well_id',
                          cascade="all, delete, delete-orphan")

    logs = relationship("WellLog", order_by=WellLog.id,
                        backref="well", primaryjoin='Well.id == WellLog.well_id',
                        cascade="all, delete, delete-orphan")

    sq.Index('coordinate_index', AbstractGeoObject.east, AbstractGeoObject.north)

    def __init__(self, well_name, short_name, depth, *args, **kwargs):
        # type: (str, str, float, *object, **object) -> None
        """
        Creates a new Well

        :param session: SQLAlchemy session, which includes the database connection
        :type session: Session

        :param well_name: well name
        :type well_name: str

        :param short_name: shortened well name
        :type short_name: str

        :param depth: drilled depth of the well
        :type depth: float

        :param args: parameters for AbstractGeoObject initialisation
        :type args: List()

        :param kwargs: parameters for AbstractGeoObject initialisation
        :type kwargs: Dict()

        :return: Nothing
        :raises ValueError: Raises ValueError if one of the types cannot be converted
        """

        self.depth = depth
        self.well_name = well_name
        self.short_name = short_name

        # call base class constructor
        AbstractGeoObject.__init__(self, *args, **kwargs)

    def __repr__(self):
        # type: () -> str
        """
        Returns a text-representation of the well

        :return: Returns a text-representation of the well
        :rtype: str
        """
        return "<Well(id='{}', name='{}', short_name='{}', depth='{}', marker='{}', logs='{}' +" \
               "'comment='{}', marker='{}')>".format(self.id, self.name, self.short_name, self.easting, self.northing,
                                                     self.altitude, self.depth, self.comment, repr(self.marker))

    def __str__(self):
        # type: () -> str
        """
        Returns a text-representation of the well

        :return: Returns a text-representation of the well
        :rtype: str
        """
        text = "[{}] {} ({}):\n{} - {} - {} - {} - {}" \
            .format(self.id, self.name, self.short_name, self.easting, self.northing, self.altitude, self.depth,
                    self.comment)

        for marker in self.marker:
            text += "\n" + str(marker)

        return text

    @property
    def depth(self):
        # type: () -> float
        """
        Returns the drilling depth of the well

        :return: Returns the drilling depth of the well
        :rtype: float
        """
        return float(self.drill_depth)

    @depth.setter
    def depth(self, dep):
        # type: (float) -> None
        """
        Sets a new drilling depth for the well

        :param dep: New drilling depth
        :type dep: float

        :return: Nothing
        :raises ValueError: Raises ValueError if dep is not of type float or cannot be converted to float or when
                            depth is < 0
        """
        dep = float(dep)
        if dep < 0:
            raise ValueError('Depth is below 0! ({})'.format(dep))
        if (len(self.marker) > 0) and (dep < self.marker[-1].depth):
            raise WellMarkerDepthException(
                    'New depth ({}) lower than depth of last marker {}'.format(dep, self.marker[-1].depth))
        self.drill_depth = dep

    @property
    def well_name(self):
        # type: () -> str
        """
        Returns the name of the well

        :return: Returns the name of the well
        :rtype: str
        """
        return self.wellname

    @well_name.setter
    def well_name(self, name):
        # type: (str) -> None
        """
        Sets a new name for the well with a maximum of 100 characters

        :param name: well name
        :type name: str

        :return: Nothing
        """
        name = str(name)
        if len(name) > 100:
            name = name[:100]
        self.wellname = name

    @property
    def short_name(self):
        # type: () -> str
        """
        Returns the short name of the well

        :return: Returns the short name of the well
        :rtype: str
        """
        return self.shortwellname

    @short_name.setter
    def short_name(self, short_name):
        # type: (str) -> None
        """
        Sets a new short name for the well with a maximum of 20 characters

        :param short_name: well name
        :type short_name: str

        :return: Nothing
        """
        short_name = str(short_name)
        if len(short_name) > 20:
            short_name = short_name[:20]
        self.shortwellname = short_name

    def insert_marker(self, marker):
        # type: (WellMarker) -> None
        """
        Insert a new WellMarker in the well
        ATTENTION: If you insert a marker, the well will be automatically stored in the database!

        :param marker: WellMarker to be inserted
        :type marker: WellMarker

        :return: Nothing

        :raises TypeError: Raises TypeError if marker is not of type WellMarker
        :raises ValueError: Raises ValueError if the depth of the marker is larger than the drilled depth of the well
        """
        if type(marker) is not WellMarker:
            raise TypeError('marker {} is not of type WellMarker!'.format(str(marker)))
        if marker.depth > self.depth:
            raise ValueError('Marker depth ({}) is larger than final well depth ({})!'.format(marker.depth, self.depth))
        self.marker.append(marker)

        # new sorting to ensure correct order without storage and reloading from the database
        self.marker.sort(key=lambda x: x.depth)

    def insert_multiple_marker(self, marker):
        # type: (List[WellMarker]) -> None
        """
        Insert the multiple marker in the well
        ATTENTION: If you insert marker, the well will be automatically stored in the database!

        :param marker: List of marker to be inserted
        :type marker: List[WellMarker]

        :return: Nothing

        :raises TypeError: Raises TypeError if one of the marker is not of type WellMarker
        :raises ValueError: Raises ValueError if the depth of a marker is larger than the drilled depth of the well
        """
        for mark in marker:
            if type(mark) is not WellMarker:
                raise TypeError(
                        'At least on marker is not of type WellMarker ({}: {})!'.format(str(mark), str(type(mark))))
            if mark.depth > self.depth:
                raise ValueError('Marker depth ({}) is larger than final well depth ({})!'.
                                 format(mark.depth, self.depth))

        self.marker += marker

        # new sorting to ensure correct order without storage and reloading from the database
        self.marker.sort(key=lambda x: x.depth)

    def get_marker_by_depth(self, depth):
        # type: (float) -> WellMarker or None
        """
        Returns the marker at depth 'depth'

        :param depth: depth of the requested marker
        :type depth: float

        :return: Returns the marker at depth 'depth'
        :rtype: WellMarker

        :raises ValueError: Raises ValueError if no marker was found for the committed depth or depth is
                            not compatible to float
        """
        depth = float(depth)
        for marker in self.marker:
            if marker.depth == depth:
                return marker
        raise ValueError('No marker found at depth {}'.format(depth))

    def delete_marker(self, marker):
        # type: (WellMarker) -> None
        """
        Deletes the marker from the well

        :param marker: WellMarker object which should be deleted
        :type marker: WellMarker

        :return: Nothing

        :raises TypeError: Raises TypeError if marker is not of type WellMarker
        :raises ValueError: Raises ValueError the marker is not part of the well
        """
        if type(marker) is not WellMarker:
            raise TypeError('marker {} is not of type WellMarker!'.format(str(marker)))

        try:
            self.marker.remove(marker)
        except ValueError as e:
            raise ValueError(str(e) + '\nWellMarker with ID ' + str(marker.id) + ' not found in list!')

    def add_log(self, log):
        # type: (WellLog) -> None
        """
        Adds a new log to the well

        :param log: new well log
        :type log: WellLog

        :return: Nothing
        :raises TypeError: Raises TypeError if log is not of type WellLog
        """
        if type(log) is not WellLog:
            raise TypeError('log {} is not of type WellLog!'.format(str(log)))

        self.logs.append(log)

    def delete_log(self, log):
        # type: (WellLog) -> None
        """
        Deletes a log from the well

        :param log: log to delete
        :type log: WellLog

        :return: Nothing
        :raises TypeError: Raises TypeError if log is not of type WellLog
        :raises ValueError: Raises ValueError if log is not part of self.logs
        """
        if type(log) is not WellLog:
            raise TypeError('log {} is not of type WellLog!'.format(str(log)))

        try:
            self.logs.remove(log)
        except ValueError as e:
            raise ValueError(str(e) + '\nWellLog with ID ' + str(log.id) + ' not found in list!')

    @classmethod
    def load_by_wellname_from_db(cls, name, session):
        # type: (str, Session) -> Well
        """
        Returns the well with the given name in the database connected to the SQLAlchemy Session session

        :param name: Only the well with this name will be returned
        :type name: str

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session

        :return: As the name is a unique value, only one result can be returned or None
        :rtype: Well or None

        :raises DatabaseException: Raises DatabaseException if more than one result was found (name is an unique value)
        """
        result = session.query(cls).filter(cls.wellname == name)
        if result.count() == 0:
            return None
        if result.count() == 1:
            result = result.one()
            result.session = session
            return result

        raise DatabaseException('More than one ({}) well with the same name: {}! Database error!'.
                                format(result.count(), name))

    @classmethod
    def load_deeper_than_value_from_db(cls, session, min_depth):
        # type: (Session, float) -> List[Well]
        """
        Returns all wells with a drilled depth below the min_depth in the database connected to the SQLAlchemy Session
        session

        :param min_depth: minimal drilled depth
        :type min_depth: float

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session

        :return: a list of wells representing the result of the database query
        :rtype: List[Well]
        """
        result = session.query(cls).filter(cls.drill_depth >= min_depth)
        result = result.order_by(cls.id).all()
        for well in result:
            well.session = session
        return result
