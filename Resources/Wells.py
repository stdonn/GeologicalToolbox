# -*- coding: UTF-8 -*-
"""
This module provides classes for storing drilling data in a database.
"""

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from typing import List

from Exceptions import DatabaseException
from Resources.DBHandler import Base
from Resources.Stratigraphy import Stratigraphy


class WellMarker(Base):
    """
    Class WellMarker

    Represents single markers in a drilled well
    """
    # define db table name and columns
    __tablename__ = 'well_marker'

    id = sq.Column(sq.INTEGER, sq.Sequence('well_id_seq'), primary_key=True)
    drill_depth = sq.Column(sq.FLOAT(10, 4))
    comment_col = sq.Column(sq.TEXT(100), default="")

    # define relationship to stratigraphic table
    horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey('stratigraphy.id'))
    hor = relationship("Stratigraphy")

    well_id = sq.Column(sq.INTEGER, sq.ForeignKey('wells.id'), default=-1)

    def __init__(self, depth, horizon, session, comment=''):
        # type: (float, Stratigraphy, Session, str) -> None
        """
        Creates a new well marker

        :param depth: depth below Kelly Bushing
        :type depth: float

        :param horizon: stratigraphy object
        :type horizon: Stratigraphy

        :param session: session object create by SQLAlchemy sessionmaker
        :type session: Session

        :param comment: additional comment
        :type comment: str

        :returns: Nothing
        :raises ValueError: Raises ValueError if one of the committed parameters cannot be converted to the expected
                            type
        """
        if not isinstance(session, Session):
            raise ValueError("'session' value is not of type SQLAlchemy Session!")
        if (type(horizon) is not Stratigraphy) and (horizon is not None):
            raise ValueError("'horizon' value is not of type Stratigraphy!")

        self.depth = float(depth)
        self.horizon = horizon
        self.__session = session
        self.comment = comment

    def __repr__(self):
        # type: () -> str
        """
        Returns a text-representation of the well marker

        :return: Returns a text-representation of the well marker
        :rtype: str
        """
        return "<Well(id='{}', depth='{}', horizon='{}', comment='{}')>".format(self.id, self.depth, self.horizon,
                                                                                self.comment)

    def __str__(self):
        # type: () -> str
        """
        Returns a text-representation of the well

        :return: Returns a text-representation of the well
        :rtype: str
        """
        return "[{}] {}: {} - {}".format(self.id, self.depth, self.horizon, self.comment)

    @property
    def comment(self):
        # type: () -> str
        """
        Returns the additional comments for the well marker.

        :return: Returns the additional comments for the well marker.
        :rtype: str
        """
        return self.comment_col

    @comment.setter
    def comment(self, comment):
        # type: (str) -> None
        """
        Sets an additional comments for the well marker

        :param comment: additional comment
        :type comment: str

        :return: Nothing
        :raises ValueError: Raises ValueError if comment is not of type str or cannot be converted to str
        """
        self.comment_col = str(comment)

    @property
    def depth(self):
        # type: () -> float
        """
        Returns the depth of the well marker below Kelly Bushing.

        :return: Returns the depth of the well marker below Kelly Bushing.
        :rtype: float
        """
        return self.drill_depth

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
        # type: () -> Stratigraphy
        """
        Returns the stratigraphy of the point

        :return: Returns the current Stratigraphy
        :rtype: Stratigraphy
        """
        return self.hor

    @horizon.setter
    def horizon(self, stratigraphy):
        # type: (Stratigraphy) -> None
        """
        sets a new stratigraphy

        :param stratigraphy: new stratigraphy
        :type stratigraphy: Stratigraphy or None

        :return: Nothing

        :raises DatabaseException: raises DatabaseException if more than one horizon with the stratigraphy.name exists
                in the database (name column should be unique)
        """
        # check if horizon exists in db -> if true take the db version, don't create a new one
        if stratigraphy is None:
            self.hor = None
            self.horizon_id = -1
            return

        self.hor = stratigraphy

    @property
    def session(self):
        # type: () -> Session
        """
        Return the current Session object

        :return: returns the current Session object, which represents the connection to a database
        :rtype: Session
        """
        return self.__session

    @session.setter
    def session(self, session):
        # type: (Session) -> None
        """
        Sets a new session, which represents the connection to a database

        :param session: session object create by SQLAlchemy sessionmaker
        :type session: Session

        :return: Nothing

        :raises TypeError: Raises TypeError if session is not of an instance of Session
        """

        if not isinstance(session, Session):
            raise TypeError("Value is not of type {} (it is {})!".format(Session, type(session)))
        self.__session = session

    # save point to db / update point
    def save_to_db(self):
        # type: () -> None
        """
        Saves all changes of the well marker to the database

        :return: Nothing

        :raises IntegrityError: raises IntegrityError if the commit to the database fails and rolls all changes back
        """
        self.__session.add(self)
        try:
            self.__session.commit()
        except IntegrityError as e:
            # Failure during database processing? -> rollback changes and raise error again
            self.__session.rollback()
            raise IntegrityError(
                    'Cannot commit changes in geopoints table, Integrity Error (double unique values?) -- {} -- ' +
                    'Rolling back changes...'.format(e.statement), e.params, e.orig, e.connection_invalidated)


class Well(Base):
    """
    Class Well

    Represents a well for storage of geoscientific data.
    """
    # define db table name and columns
    __tablename__ = 'wells'

    id = sq.Column(sq.INTEGER, sq.Sequence('well_id_seq'), primary_key=True)
    east = sq.Column(sq.FLOAT(10, 4))
    north = sq.Column(sq.FLOAT(10, 4))
    alt = sq.Column(sq.FLOAT(10, 4))
    drill_depth = sq.Column(sq.FLOAT(10, 4))
    well_name = sq.Column(sq.TEXT(100), unique=True)
    short_well_name = sq.Column(sq.TEXT(100), default="")
    comment_col = sq.Column(sq.TEXT(100), default="")

    # define markers relationship
    marker = relationship("WellMarker", order_by=WellMarker.drill_depth, collection_class=ordering_list('drill_depth'),
                          backref="well", primaryjoin='Well.id==WellMarker.well_id',
                          cascade="all, delete, delete-orphan")

    def __init__(self, session, name, easting, northing, altitude, depth, short_name='', comment=''):
        # type: (Session, str, float, float, float, float, str, str) -> None
        """
        Creates a new Well

        :param session: SQLAlchemy session, which includes the database connection
        :type session: Session

        :param name: well name
        :type name: str

        :param easting: easting coordinate of the well
        :type easting: float

        :param northing: northing coordinate of the well
        :type northing: float

        :param altitude: height above sea level of the well
        :type altitude: float

        :param depth: drilled depth of the well
        :type depth: float

        :param short_name: well name
        :type short_name: str

        :param comment: additional comment for the well
        :type comment: str

        :return: Nothing
        :raises ValueError: Raises ValueError if one of the types cannot be converted
        """
        if not isinstance(session, Session):
            raise ValueError("'session' value is not of type SQLAlchemy Session!")

        self.__session = session
        self.easting = float(easting)
        self.northing = float(northing)
        self.altitude = float(altitude)
        self.depth = float(depth)
        self.name = str(name)
        self.short_name = str(short_name)
        self.comment = comment

    def __repr__(self):
        # type: () -> str
        """
        Returns a text-representation of the well

        :return: Returns a text-representation of the well
        :rtype: str
        """
        return "<Well(id='{}', name='{}', short_name='{}', east='{}', north='{}', alt='{}', depth='{}',' +" \
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
    def comment(self):
        # type: () -> str
        """
        Returns the additional comments for the well marker.

        :return: Returns the additional comments for the well marker.
        :rtype: str
        """
        return self.comment_col

    @comment.setter
    def comment(self, comment):
        # type: (str) -> None
        """
        Sets an additional comments for the well marker

        :param comment: additional comment
        :type comment: float

        :return: Nothing
        :raises ValueError: Raises ValueError if comment is not of type str or cannot be converted to str
        """
        self.comment_col = str(comment)

    # define setter and getter for columns and local data
    @property
    def easting(self):
        # type: () -> float
        """
        Returns the easting value of the well.

        :return: Returns the easting value of the well.
        :rtype: float
        """
        return self.east

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
        Returns the northing value of the well.

        :return: Returns the northing value of the well.
        :rtype: float
        """
        return self.north

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
        Returns the height above sea level of the well.

        :return: Returns the height above sea level of the well.
        :rtype: float
        """
        return self.alt

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
    def depth(self):
        # type: () -> float
        """
        Returns the drilled depth of the well

        :return: Returns the drilled depth of the well
        :rtype: float
        """
        return self.drill_depth

    @depth.setter
    def depth(self, value):
        # type: (float) -> None
        """
        sets a drilled depth of the well

        :param value: drilled depth
        :type value: float

        :return: Nothing
        :raises ValueError: Raises ValueError if the committed value cannot be converted to float
        """
        self.drill_depth = float(value)

    @property
    def name(self):
        # type: () -> str
        """
        Returns the name of the well

        :return: Returns the name of the well
        :rtype: str
        """
        return self.well_name

    @name.setter
    def name(self, value):
        # type: (str) -> None
        """
        Sets a new name for the well with a maximum of 100 characters

        :param value: well name
        :type value: str

        :return: Nothing
        """

        string = str(value)
        if len(string) > 100:
            string = string[:100]
        self.well_name = string

    @property
    def short_name(self):
        # type: () -> str
        """
        Returns the short name of the well

        :return: Returns the short name of the well
        :rtype: str
        """
        return self.short_well_name

    @short_name.setter
    def short_name(self, value):
        # type: (str) -> None
        """
        Sets a new short name for the well with a maximum of 20 characters

        :param value: well name
        :type value: str

        :return: Nothing
        """

        string = str(value)
        if len(string) > 20:
            string = string[:20]
        self.short_well_name = string

    @property
    def session(self):
        # type: () -> Session
        """
        Return the current Session object

        :return: returns the current Session object, which represents the connection to a database
        :rtype: Session
        """
        return self.__session

    @session.setter
    def session(self, value):
        # type: (Session) -> None
        """
        Sets a new session, which represents the connection to a database

        :param value: session object create by SQLAlchemy sessionmaker
        :type value: Session

        :return: Nothing

        :raises TypeError: Raises TypeError if value is not of an instance of Session
        """

        if not isinstance(value, Session):
            raise TypeError("Value is not of type {} (it is {})!".format(Session, type(value)))
        self.__session = value

    def insert_marker(self, marker):
        # type: (WellMarker) -> None
        """
        Insert a new WellMarker in the well

        :param marker: WellMarker to be inserted
        :type marker: WellMarker

        :return: Nothing

        :raises TypeError: Raises TypeError if marker is not of type WellMarker
        """
        if type(marker) is not WellMarker:
            raise TypeError('marker {} is not of type WellMarker!'.format(str(marker)))
        self.marker.append(marker)

    def insert_multiple_marker(self, marker):
        # type: (List[WellMarker]) -> None
        """
        Insert the multiple marker in the well

        :param marker: List of marker to be inserted
        :type marker: List[WellMarker]

        :return: Nothing

        :raises TypeError: Raises TypeError if one of the marker is not of type WellMarker
        """
        for mark in marker:
            if type(mark) is not WellMarker:
                raise TypeError(
                    'At least on marker is not of type WellMarker ({}: {})!'.format(str(mark), str(type(mark))))

        self.marker += marker

    def get_marker_index(self, marker):
        # type: (WellMarker) -> int
        """
        Returns the index of the given marker in the well

        :param marker: marker which has to be looked up
        :type marker: WellMarker

        :return: Index of the marker in the line
        :rtype: int

        :raises ValueError: Raises ValueError if committed marker is not part of the well
        """
        return self.marker.index(marker)

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

    # save point to db / update point
    def save_to_db(self):
        # type: () -> None
        """
        Saves all changes of the well to the database

        :return: Nothing

        :raises IntegrityError: raises IntegrityError if the commit to the database fails and rolls all changes back
        """
        # first: check that marker with the same stratigraphic name the same object (no doubled unique names)
        marker_strat = dict()
        for marker in self.marker:
            if marker.horizon.name in marker_strat:
                marker.horizon = marker_strat[marker.horizon.name]
            else:
                marker_strat[marker.horizon.name] = marker.horizon

        self.__session.add(self)
        try:
            self.__session.commit()
        except IntegrityError as e:
            # Failure during database processing? -> rollback changes and raise error again
            self.__session.rollback()
            raise IntegrityError(
                    'Cannot commit changes in wells table, Integrity Error (double unique values?) -- {} -- ' +
                    'Rolling back changes...'.format(e.statement), e.params, e.orig, e.connection_invalidated)

    # load points from db
    @classmethod
    def load_all_from_db(cls, session):
        # type: (Session) -> List[Well]
        """
        Returns all wells in the database connected to the SQLAlchemy Session session

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session

        :return: a list of wells representing the result of the database query
        :rtype: List[Well]
        """
        result = session.query(cls)
        result = result.order_by(cls.id).all()
        for well in result:
            well.session = session
        return result

    @classmethod
    def load_by_name_from_db(cls, name, session):
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
        result = session.query(cls).filter(cls.well_name == name)
        if result.count() == 0:
            return None
        if result.count() == 1:
            result = result.one()
            result.session = session
            return result

        raise DatabaseException('More than one ({}) well with the same name: {}! Database error!'.
                                format(result.count(), name))

    @classmethod
    def load_in_extent_from_db(cls, session, min_easting, max_easting, min_northing, max_northing):
        # type: (Session, float, float, float, float) -> List[Well]
        """
        Returns all wells inside the given extent in the database connected to the SQLAlchemy Session session

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
        :rtype: List[Well]
        """
        result = session.query(cls).filter(sq.between(cls.east, min_easting, max_easting)). \
            filter(sq.between(cls.north, min_northing, max_northing))
        result = result.order_by(cls.id).all()
        for well in result:
            well.session = session
        return result
