# -*- coding: UTF-8 -*-
"""
This module provides basic geometries (points and lines) for storing geological data in database.
"""

import sqlalchemy as sq
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from typing import List

from Resources.DBHandler import Base
from Resources.Stratigraphy import Stratigraphy
from Resources.constants import float_precision


class GeoPoint(Base):
    """
    Class GeoPoint

    Represents a geological point feature, e.g. for storing line nodes or geological outcrops in a database.
    """
    # define db table name and columns
    __tablename__ = 'geopoints'

    id = sq.Column(sq.INTEGER, sq.Sequence('geopoints_id_seq'), primary_key=True)
    east = sq.Column(sq.REAL(10, 4))
    north = sq.Column(sq.REAL(10, 4))
    alt = sq.Column(sq.REAL(10, 4))
    has_z = sq.Column(sq.BOOLEAN, default=False)
    horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey('stratigraphy.id'), default=-1)

    # define relationship to stratigraphic table
    hor = relationship("Stratigraphy")

    line_id = sq.Column(sq.INTEGER, sq.ForeignKey('lines.id'), default=-1)
    line_pos = sq.Column(sq.INTEGER, default=-1)
    name = sq.Column(sq.TEXT(100), default="")

    # make the points unique -> coordinates + horizon + belongs to one line?
    sq.UniqueConstraint(east, north, alt, horizon_id, line_id, line_pos, name='u_point_constraint')

    def __init__(self, easting, northing, altitude, horizon, session, name=""):
        # type: (float, float, float, Stratigraphy, Session, str) -> None
        """
        Creates a new GeoPoint

        :param easting: easting coordinate of the point
        :type easting: float

        :param northing: northing coordinate of the point
        :type northing: float

        :param altitude: height above sea level of the point or None
        :type altitude: float or None

        :param horizon: stratigraphy of the point
        :type horizon: Stratigraphy

        :param session: SQLAlchemy session, which includes the database connection
        :type session: Session

        :param name: name of the line with the aim to have the possibility to group more lines to a line-set
        :type name: str

        :return: Nothing
        :raises ValueError: Raises ValueError if one of the types cannot be converted
        """
        if not isinstance(session, Session):
            raise ValueError("'session' value is not of type SQLAlchemy Session!")
        if (type(horizon) is not Stratigraphy) and (horizon is not None):
            raise ValueError("'horizon' value is not of type Stratigraphy!")

        self.easting = float(easting)
        self.northing = float(northing)
        if altitude is None:
            self.altitude = 0
            self.has_z = False
        else:
            self.altitude = float(altitude)
            self.has_z = True
        self.__session = session
        self.horizon = horizon
        self.point_name = str(name)

    def __repr__(self):
        # type: () -> str
        """
        Returns a text-representation of the line

        :return: Returns a text-representation of the line
        :rtype: str
        """
        return "<GeoPoint(id='{}', east='{}', north='{}', alt='{}', horizon='{}', line={}, line-position={})>" \
            .format(self.id, self.easting, self.northing, self.altitude, str(self.horizon), self.line_id, self.line_pos)

    def __str__(self):
        # type: () -> str
        """
        Returns a text-representation of the line

        :return: Returns a text-representation of the line
        :rtype: str
        """
        return "[{}] {} - {} - {} : {} - {} - {}" \
            .format(self.id, self.easting, self.northing, self.altitude, str(self.horizon), self.line_id, self.line_pos)

    # define setter and getter for columns and local data
    @property
    def easting(self):
        # type: () -> float
        """
        Returns the easting value of the point.

        :return: Returns the easting value of the point.
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
        Returns the northing value of the point.

        :return: Returns the northing value of the point.
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
        Returns the height above sea level of the point.
        If the point has no z-value (check with GeoPoint.has_z()), 0 will be returned.

        :return: Returns the height above sea level of the point.
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
        self.has_z = True

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
    def horizon(self, value):
        # type: (Stratigraphy) -> None
        """
        sets a new stratigraphy

        :param value: new stratigraphy
        :type value: Stratigraphy or None

        :return: Nothing

        :raises DatabaseException: raises DatabaseException if more than one horizon with the value.name exists in the
        database (name column should be unique)
        """
        # check if horizon exists in db -> if true take the db version, don't create a new one
        if value is None:
            self.hor = None
            self.horizon_id = -1
            return

        self.hor = value

    @property
    def point_name(self):
        # type: () -> str
        """
        Returns the name of the point

        :return: Returns the name of the point
        :rtype: str
        """
        return self.name

    @point_name.setter
    def point_name(self, value):
        # type: (str) -> None
        """
        Sets a new name for the point with a maximum of 100 characters

        :param value: point name
        :type value: str

        :return: Nothing
        """

        string = str(value)
        if len(string) > 100:
            string = string[:100]
        self.name = string

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

    # delete z-dimension and information from point
    def del_z(self):
        # type: () -> None
        """
        removes the z-value from the point

        :return: Nothing
        """
        self.alt = 0
        self.has_z = False

    # save point to db / update point
    def save_to_db(self):
        # type: () -> None
        """
        Saves all changes of the point or the point itself to the connected database

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
                    'Cannot commit changes in geopoints table, Integrity Error (double unique values?) -- {} --' +
                    'Rolling back changes...'.format(e.statement), e.params, e.orig, e.connection_invalidated)

    # load points from db
    @classmethod
    def load_all_from_db(cls, session, get_lines=False):
        # type: (Session, bool) -> List[GeoPoint]
        """
        Returns all points in the database connected to the SQLAlchemy Session session

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session

        :param get_lines: If True, also line nodes are returned
        :type get_lines: bool

        :return: a list of lines representing the result of the database query
        :rtype: List[GeoPoint]
        """
        result = session.query(cls)
        if not get_lines:
            result = result.filter(GeoPoint.line_id == -1)
        result = result.order_by(cls.id).all()
        for point in result:
            point.session = session
        return result

    @classmethod
    def load_by_name_from_db(cls, name, session, get_lines=False):
        # type: (str, Session, bool) -> List[GeoPoint]
        """
        Returns all points with the given name in the database connected to the SQLAlchemy Session session

        :param name: Only points with this name will be returned
        :type name: str

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session

        :param get_lines: If True, also line nodes are returned
        :type get_lines: bool

        :return: a list of points representing the result of the database query
        :rtype: List[GeoPoint]
        """
        result = session.query(cls).filter(cls.name == name)
        if not get_lines:
            result = result.filter(GeoPoint.line_id == -1)
        result = result.order_by(cls.id).all()
        for point in result:
            point.session = session
        return result

    @classmethod
    def load_in_extent_from_db(cls, session, min_easting, max_easting, min_northing, max_northing, get_lines=False):
        # type: (Session, float, float, float, float, bool) -> List[Line]
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

        :param get_lines: If True, also line nodes are returned
        :type get_lines: bool

        :return: a list of points representing the result of the database query
        :rtype: List[GeoPoint]
        """
        result = session.query(GeoPoint).filter(sq.between(GeoPoint.east, min_easting, max_easting)). \
            filter(sq.between(GeoPoint.north, min_northing, max_northing))
        if not get_lines:
            result = result.filter(GeoPoint.line_id == -1)
        result = result.order_by(cls.id).all()
        for point in result:
            point.session = session
        return result


class Line(Base):
    """
    Class Line

    Represents a geological line feature, e.g. for storing faults or horizon surface expressions.
    """
    # define db table name and columns
    __tablename__ = 'lines'

    id = sq.Column(sq.INTEGER, sq.Sequence('line_id_seq'), primary_key=True)
    closed = sq.Column(sq.BOOLEAN)
    name = sq.Column(sq.TEXT(100), default="")

    # set stratigraphy of the line
    horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey('stratigraphy.id'))
    hor = relationship("Stratigraphy")

    # add GeoPoint relation, important is the ordering by line_pos value
    # collection_class function automatically reorders this value in case of insertion or deletion of points
    points = relationship("GeoPoint", order_by=GeoPoint.line_pos, collection_class=ordering_list('line_pos'),
                          backref="line", primaryjoin='Line.id==GeoPoint.line_id',
                          cascade="all, delete, delete-orphan")

    def __init__(self, closed, session, horizon, points, name=""):
        # type: (bool, Session, Stratigraphy, List[GeoPoint], str) -> None
        """
        Create a new line.

        :param closed: True if the line should be closed, else False
        :type closed: bool

        :param session: SQLAlchemy session, which includes the database connection
        :type session: Session

        :param horizon: Stratigraphy to which the line belongs
        :type horizon: Stratigraphy

        :param points: list of points which represents the lines nodes
        :type points: List[GeoPoint]

        :param name: name of the line with the aim to have the possibility to group more lines to a line-set
        :type name: str

        :return: Nothing
        :raises ValueError: Raises ValueError if one of the types cannot be converted
        """
        if not isinstance(session, Session):
            raise ValueError("'session' value is not of type SQLAlchemy Session!")
        if (type(horizon) is not Stratigraphy) and (horizon is not None):
            raise ValueError("'horizon' value is not of type Stratigraphy!")

        for pnt in points:
            if type(pnt) is not GeoPoint:
                raise ValueError('At least on point in points is not of type GeoPoint!')

        self.is_closed = bool(closed)
        self.__session = session
        self.horizon = horizon
        self.points = points
        self.line_name = str(name)

        # check doubled values in a line
        self.__remove_doubled_points()

    def __repr__(self):
        # type: () -> str
        """
        Returns a text-representation of the line

        :return: Returns a text-representation of the line
        :rtype: str
        """

        return "<Line(id='{}', closed='{}', horizon='{}'\npoints='{}')>" \
            .format(self.id, self.closed, str(self.horizon), str(self.points))

    def __str__(self):
        # type: () -> str
        """
        Returns a text-representation of the line

        :return: Returns a text-representation of the line
        :rtype: str
        """
        # return "[{}] {} - {}\n{}".format(self.id, self.closed, str(self.horizon), str(self.points))
        text = "Line: id='{}', closed='{}', horizon='{}', points:" \
            .format(self.id, self.closed, str(self.horizon))

        for point in self.points:
            text += "\n{}".format(str(point))

        return text

    @property
    def is_closed(self):
        # type: () -> bool
        """
        Returns True if the line is close else False

        :return: Returns True if the line is close else False
        :rtype: bool
        """
        return self.closed

    @is_closed.setter
    def is_closed(self, value):
        # type: (bool) -> None
        """
        Sets closed value

        :param value: new close value
        :type value: bool

        :return: Nothing

        :raises TypeError: Raises TypeError if value is not of type bool
        """
        if type(value) != bool:
            raise TypeError('Value must be of type bool, but is {}'.format(str(type(value))))
        self.closed = bool(value)

    @property
    def horizon(self):
        # type: () -> Stratigraphy
        """
        Returns the stratigraphy of the line

        :return: Returns the horizon of the line
        :rtype: Stratigraphy
        """
        return self.hor

    @horizon.setter
    def horizon(self, value):
        # type: (Stratigraphy) -> None
        """
        sets a new stratigraphy

        :param value: new stratigraphy
        :type value: Stratigraphy or None

        :return: Nothing

        :raises DatabaseException: raises DatabaseException if more than one horizon with the value.name exists in the
                database (name column should be unique)
        """
        if value is None:
            self.hor = None
            self.horizon_id = -1

        else:
            self.hor = value

    @property
    def line_name(self):
        # type: () -> str
        """
        Return the line name

        :return: returns the line name
        :rtype: str
        """
        return self.name

    @line_name.setter
    def line_name(self, value):
        # type: (str) -> None
        """
        Sets a new name for the line with a maximum of 100 characters

        :param value: line name
        :type value: str

        :return: Nothing
        """
        string = str(value)
        if len(string) > 100:
            string = string[:100]
        self.name = string

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

    def insert_point(self, point, position):
        # type: (GeoPoint, int) -> None
        """
        Insert a point in the line at the committed index.

        :param point: point to be inserted in the line
        :type point: GeoPoint

        :param position: Index, where points should be inserted in the line
        :type position: int

        :return: Nothing

        :raises TypeError: Raises TypeError if point is not of type GeoPoint
        :raises ValueError: Raises ValueError if position is not of type int or cannot be converted to int
        """
        position = int(position)
        if type(point) is not GeoPoint:
            raise TypeError('point {} is not of type GeoPoint!'.format(str(point)))
        else:
            self.points.insert(position, point)

        # check doubled values in a line
        self.__remove_doubled_points()

    def insert_points(self, points, position):
        # type: (List[GeoPoint], int) -> None
        """
        Insert a points in the line at the committed index.

        :param points: List of points to be inserted in the line
        :type points: List[GeoPoint]

        :param position: Index, where points should be inserted in the line
        :type position: int

        :return: Nothing

        :raises TypeError: Raises TypeError if one of the points is not of type GeoPoint
        :raises ValueError: Raises ValueError if position is not of type int or cannot be converted to int
        """
        position = int(position)

        for pnt in points:
            if type(pnt) is not GeoPoint:
                raise TypeError('At least on point in points is not of type GeoPoint!')

        # use slicing for points insert
        if len(self.points) <= position:
            self.points[-1:-1] = points
        else:
            self.points[position:position] = points

        # check doubled values in a line
        self.__remove_doubled_points()

    def get_point_index(self, point):
        # type: (GeoPoint) -> int
        """
        Returns the index of the given point in the line

        :param point: point which has to be looked up
        :type point: GeoPoint

        :return: Index of the point in the line
        :rtype: int

        :raises ValueError: Raises ValueError if committed point is not part of the line
        """
        return self.points.index(point)

    def delete_point(self, point):
        # type: (GeoPoint) -> None
        """
        Deletes the point from the line

        :param point: GeoPoint object which should be deleted
        :type point: GeoPoint

        :return: Nothing

        :raises TypeError: Raises TypeError if point is not of type GeoPoint
        :raises ValueError: Raises ValueError the point is not part of the line
        """
        if type(point) is not GeoPoint:
            raise TypeError('point {} is not of type GeoPoint!'.format(str(point)))

        try:
            self.points.remove(point)
        except ValueError as e:
            raise ValueError(str(e) + '\nGeoPoint with ID ' + str(point.id) + ' not found in list!')

        # check doubled values in a line
        self.__remove_doubled_points()

    def delete_point_by_coordinates(self, easting, northing, altitude=0):
        # type: (float, float, float) -> None
        """
        Deletes a point with the given coordinates from the line

        :param easting: easting value of the point to be deleted
        :type easting: float

        :param northing: northing value of the point to be deleted
        :type northing: float

        :param altitude: altitude value of the point to be deleted (only necessary if point has z-values!)
        :type altitude: float

        :return: Nothing

        :raises ValueError: Raises ValueError if one parameter is not compatible to type float or no point can be found
        """
        try:
            easting = float(easting)
            northing = float(northing)
            altitude = float(altitude)
        except ValueError:
            raise ValueError('On of the input coordinates is not of type float!')

        # iterate over a copy of the list to avoid iteration issues caused by the deletion of values
        for pnt in self.points[:]:
            if (abs(float(pnt.easting) - easting) < float_precision) and (
                        abs(float(pnt.northing) - northing) < float_precision) and (
                        (abs(float(pnt.altitude) - altitude) < float_precision) or not pnt.has_z):
                self.points.remove(pnt)
                # check doubled values in a line
                self.__remove_doubled_points()
                return

        raise ValueError('Point not found with coordinates {0}/{1}/{2}'.format(easting, northing, altitude))

    def __remove_doubled_points(self):
        # type: () -> None
        """
        remove points with the same coordinates, if they follow up each other in the points list.

        :return: None
        """

        # create a full copy of the point-list
        tmp_pnts = self.points[:]
        for i in range(len(tmp_pnts) - 1):
            coord_1 = (tmp_pnts[i].easting, tmp_pnts[i].northing, tmp_pnts[i].altitude)
            coord_2 = (tmp_pnts[i + 1].easting, tmp_pnts[i + 1].northing, tmp_pnts[i + 1].altitude)

            # remove doubled points
            if coord_1 == coord_2:
                self.points.remove(tmp_pnts[i + 1])

        # test for first and last point
        # if identical, then remove last point and set closed to True
        coord_1 = (self.points[0].easting, self.points[0].northing, self.points[0].altitude)
        coord_2 = (self.points[-1].easting, self.points[-1].northing, self.points[-1].altitude)

        if coord_1 == coord_2:
            del self.points[-1]
            self.closed = True

    def save_to_db(self):
        # type: () -> None
        """
        Saves all changes of the line or the line itself to the connected database

        :return: Nothing

        :raises IntegrityError: raises IntegrityError if the commit to the database fails and rolls all changes back
        """
        self.__session.add(self)

        try:
            # first: all points should have the same horizon as the line
            for pnt in self.points:
                pnt.hor = self.horizon  # directly set hor variable, hor still checked...
                pnt.horizon_id = self.horizon_id
            self.__session.commit()
        except IntegrityError as e:
            # Failure during database processing? -> rollback changes and raise error again
            self.__session.rollback()
            raise IntegrityError(
                    'Cannot commit changes in lines table, Integrity Error (double unique values?) --' +
                    '{} -- Rolling back changes...'.format(e.statement), e.params, e.orig, e.connection_invalidated)

    @classmethod
    def load_all_from_db(cls, session):
        # type: (Session) -> List[Line]
        """
        Returns all lines in the database connected to the SQLAlchemy Session session

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session

        :return: a list of lines representing the result of the database query
        :rtype: List[Line]
        """
        result = session.query(cls).order_by(cls.id).all()
        for line in result:
            line.session = session
        return result

    @classmethod
    def load_by_id_from_db(cls, line_id, session):
        # type: (int, Session) -> Line
        """
        Returns the line with the given id in the database connected to the SQLAlchemy Session session

        :param line_id: Only the line with this id will be returned (has to be 1, unique value)
        :type line_id: int

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session

        :return: a single line representing the result of the database query
        :rtype: Line

        :raises NoResultFound: Raises NoResultFound if no line was found with this id
        :raises IntegrityError: Raises IntegrityError if more than one line is found (more than one unique value)
        """
        result = session.query(cls).filter(cls.id == line_id).one()
        result.session = session
        return result

    @classmethod
    def load_by_name_from_db(cls, name, session):
        # type: (str, Session) -> List[Line]
        """
        Returns all lines with the given name in the database connected to the SQLAlchemy Session session

        :param name: Only lines with this name will be returned
        :type name: str

        :param session: represents the database connection as SQLAlchemy Session
        :type session: Session

        :return: a list of lines representing the result of the database query
        :rtype: List[Line]
        """
        result = session.query(cls).filter(cls.name == name).order_by(cls.id).all()
        for line in result:
            line.session = session
        return result

    @classmethod
    def load_in_extent_from_db(cls, session, min_easting, max_easting, min_northing, max_northing):
        # type: (Session, float, float, float, float) -> List[Line]
        """
        Returns all lines with at least on point inside the given extent in the database connected to the SQLAlchemy
        Session session

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

        :return: a list of lines representing the result of the database query
        :rtype: List[Line]
        """

        # select the points with a line_id that are located inside the extent
        # -> result will be a list of tuples with only a single line-id value
        # -> convert this list to a set in order to remove doubled values

        points = set(
                [x[0] for x in session.query(GeoPoint.line_id).
                    filter(GeoPoint.line_id != -1).
                    filter(sq.between(GeoPoint.east, min_easting, max_easting)).
                    filter(sq.between(GeoPoint.north, min_northing, max_northing)).all()
                 ])

        # return line with points in extend
        # to speed up the process, test if points (len > 0) exist in extent first
        if len(points) == 0:
            return []
        result = session.query(Line).filter(Line.id.in_(points)).order_by(cls.id).all()
        for line in result:
            line.session = session
        return result
