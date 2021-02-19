# -*- coding: UTF-8 -*-
"""
Module providing basic geometries (points and lines) for storing geological data in a database.
"""

from typing import List

import sqlalchemy as sq
from geological_toolbox.constants import float_precision
from geological_toolbox.db_handler import Base, AbstractDBObject
from geological_toolbox.geo_object import AbstractGeoObject
from geological_toolbox.properties import Property
from geological_toolbox.stratigraphy import StratigraphicObject
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session


class GeoPoint(Base, AbstractGeoObject):
    """
    Represents a geological point feature, e.g. for storing line nodes or geological outcrops in a database.

    :param horizon: stratigraphic object of the point feature
    :param has_z: Is altitude stored as z value?
    :param args: parameters for AbstractGeoObject initialisation
    :param kwargs: parameters for AbstractGeoObject initialisation
    :return: Nothing
    :raises ValueError: if has_z is not compatible to type bool
    """
    # define db table name and columns
    __tablename__ = "geopoints"

    id = sq.Column(sq.INTEGER, sq.Sequence("geopoints_id_seq"), primary_key=True)
    has_z = sq.Column(sq.BOOLEAN, default=False)
    horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey("stratigraphy.id"), default=-1)

    # define relationship to stratigraphic table
    hor: StratigraphicObject = relationship("StratigraphicObject")

    line_id = sq.Column(sq.INTEGER, sq.ForeignKey("lines.id"), default=None, nullable=True)
    line_pos = sq.Column(sq.INTEGER, default=-1)

    # make the points unique -> coordinates + horizon + belongs to one line?
    sq.UniqueConstraint(AbstractGeoObject.east, AbstractGeoObject.north, AbstractGeoObject.alt, horizon_id,
                        AbstractGeoObject.name_col, line_id, line_pos, name="u_point_constraint")
    sq.Index("geopoint_coordinate_index", AbstractGeoObject.east, AbstractGeoObject.north)

    # add Property relation
    # order by property name
    properties: List[Property] = relationship("Property", order_by=Property.prop_name, backref="point",
                                              primaryjoin="GeoPoint.id==Property.point_id",
                                              cascade="all, delete, delete-orphan")

    def __init__(self, horizon: StratigraphicObject or None, has_z: bool, *args, **kwargs) -> None:
        """
        Creates a new GeoPoint
        """
        self.has_z = bool(has_z)
        self.horizon = horizon

        # call base class constructor
        AbstractGeoObject.__init__(self, *args, **kwargs)

    def __repr__(self) -> str:
        text = "<GeoPoint(id='{}', horizon='{}', line={}, line-position={})>\n". \
            format(self.id, str(self.horizon), self.line_id, self.line_pos)
        text += AbstractGeoObject.__repr__(self)
        text += "Properties: {}".format(self.properties)
        return text

    def __str__(self) -> str:
        text = "[{}] {} - {} - {}\n".format(self.id, str(self.horizon), self.line_id, self.line_pos)
        text += "AbstractGeoObject: {}\n".format(AbstractGeoObject.__str__(self))
        text += "Properties"
        # noinspection PyTypeChecker
        if len(self.properties) == 0:
            text += "\n  --- None ---"
        else:
            # noinspection PyTypeChecker
            for prop in self.properties:
                text += "\n  " + str(prop)

        return text

    @property
    def horizon(self) -> StratigraphicObject:
        """
        stratigraphic object of the point feature

        :raises TypeError: if value is not of type StratigraphicObject or None
        """
        return self.hor

    @horizon.setter
    def horizon(self, value: StratigraphicObject or None) -> None:
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

    # delete z-dimension and information from point
    def del_z(self) -> None:
        """
        removes the z-value from the point, :attr:`~GeoObject.AbstractGeoObject.altitude` value will be set to 0

        :return: Nothing
        """
        self.alt = 0
        self.has_z = False

    def use_z(self) -> None:
        """
        uses the altitude value as z coordinate. Attention: please set the :attr:`ÃbstractGeoObject.altitude` property,
        if not it defaults to 0.

        :return: Nothing
        """
        self.has_z = True

    # add and remove property information form point
    def add_property(self, prop: Property) -> None:
        """
        Adds a new property to the point

        :param prop: new point property
        :return: Nothing
        :raises TypeError: if log is not of type Property
        """
        if type(prop) is not Property:
            raise TypeError("property {} is not of type Property!".format(str(prop)))

        self.properties.append(prop)

    def delete_property(self, prop: Property) -> None:
        """
        Deletes a property from the point

        :param prop: property to delete
        :return: Nothing
        :raises TypeError: if log is not of type Property
        :raises ValueError: if log is not part of self.properties
        """
        if type(prop) is not Property:
            raise TypeError("property {} is not of type Property!".format(str(prop)))

        try:
            self.properties.remove(prop)
        except ValueError as e:
            raise ValueError(str(e) + "\nProperty with ID " + str(prop.id) + " not found in list!")

    def has_property(self, property_name: str) -> bool:
        """
        Returns True, if a property with the name property_name exists for the GeoPoint, else False

        :param property_name: name of the requested property
        :return: True, if a property with the name property_name exists for the GeoPoint, else False
        """
        # noinspection PyTypeChecker
        for prop in self.properties:
            if prop.property_name == property_name:
                return True
        return False

    def get_property(self, property_name: str) -> Property:
        """
        Returns requested property, if the property with the name property_name exists for the GeoPoint

        :param property_name: name of the requested property
        :return: Returns the property
        :raises ValueError: if no property with the name exists
        """
        property_name = str(property_name)
        # noinspection PyTypeChecker
        for prop in self.properties:
            if prop.property_name == property_name:
                return prop
        raise ValueError("No property with the name '{}' exists!".format(property_name))

    # overwrite loading method
    @classmethod
    def load_all_without_lines_from_db(cls, session: Session) -> List["GeoPoint"]:
        """
        Returns all points in the database connected to the SQLAlchemy Session session, which are not part of a line.
        This function is similar the
        :meth:`AbstractDBObject.load_all_from_db()<geological_toolbox.db_handler.AbstractDBObject.load_all_from_db>`
        function.

        :param session: represents the database connection as SQLAlchemy Session
        :return: a list of points representing the result of the database query
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        # filter((GeoPoint.line_id is None) or (GeoPoint.line_id == -1) or (GeoPoint.line_id == "")). \
        result = session.query(GeoPoint). \
            filter(sq.or_(GeoPoint.line_id == None, GeoPoint.line_id == -1)). \
            order_by(cls.id).all()
        for point in result:
            point.session = session
        return result

    @classmethod
    def load_by_name_without_lines_from_db(cls, name: str, session: Session) -> List["GeoPoint"]:
        """
        Returns all GeoPoints with the given name in the database connected to the SQLAlchemy Session session, which
        are not part of a line. This function is similar the
        :meth:`AbstractDBObject.load_by_name_from_db()<geological_toolbox.db_handler.AbstractDBObject.load_by_name_from_db>`
        function.

        :param name: Only GeoPoints with this name will be returned
        :param session: represents the database connection as SQLAlchemy Session
        :return: a list of GeoPoints representing the result of the database query
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        result = session.query(GeoPoint). \
            filter(sq.or_(GeoPoint.line_id == None, GeoPoint.line_id == -1)). \
            filter(cls.name_col == name). \
            order_by(cls.id).all()
        for obj in result:
            obj.session = session
        return result

    @classmethod
    def load_in_extent_without_lines_from_db(cls, session: Session, min_easting: float, max_easting: float,
                                             min_northing: float, max_northing: float) -> List["GeoPoint"]:
        """
        Returns all points inside the given extent in the database connected to the SQLAlchemy Session session, which
        are not part of a line. This function is similar the
        :meth:`AbstractGeoObject.load_in_extent_from_db()<geological_toolbox.geo_object.AbstractGeoObject.load_in_extent_from_db>`
        function.

        :param min_easting: minimal easting of extent
        :param max_easting: maximal easting of extent
        :param min_northing: minimal northing of extent
        :param max_northing: maximal northing of extent
        :param session: represents the database connection as SQLAlchemy Session
        :return: a list of points representing the result of the database query
        :raises ValueError: if one of the extension values is not compatible to type float
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        min_easting = float(min_easting)
        max_easting = float(max_easting)
        min_northing = float(min_northing)
        max_northing = float(max_northing)

        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

        result = session.query(GeoPoint).filter(sq.between(GeoPoint.east, min_easting, max_easting)). \
            filter(sq.between(GeoPoint.north, min_northing, max_northing)). \
            filter(sq.or_(GeoPoint.line_id == None, GeoPoint.line_id == -1)). \
            order_by(cls.id).all()
        for point in result:
            point.session = session
        return result


class Line(Base, AbstractDBObject):
    """
    Class Line

    Represents a geological line feature, e.g. for storing faults or horizon surface expressions.

    :param closed: True if the line should be closed, else False
    :param horizon: StratigraphicObject
    :param points: list of points which represents the lines nodes
    :param args: parameters for AbstractDBObject initialisation
    :param kwargs: parameters for AbstractDBObject initialisation
    :return: Nothing
    :raises ValueError: Raises ValueError if one of the types cannot be converted
    """

    # define db table name and columns
    __tablename__ = "lines"

    id = sq.Column(sq.INTEGER, sq.Sequence("lines_id_seq"), primary_key=True)
    closed = sq.Column(sq.BOOLEAN)

    # set stratigraphy of the line
    horizon_id = sq.Column(sq.INTEGER, sq.ForeignKey("stratigraphy.id"))
    hor: StratigraphicObject = relationship("StratigraphicObject")

    # add GeoPoint relation, important is the ordering by line_pos value
    # collection_class function automatically reorders this value in case of insertion or deletion of points
    points: List[GeoPoint] = relationship("GeoPoint", order_by=GeoPoint.line_pos,
                                          collection_class=ordering_list("line_pos"),
                                          backref="line", primaryjoin="Line.id==GeoPoint.line_id",
                                          cascade="all, delete, delete-orphan")

    def __init__(self, closed: bool, horizon: StratigraphicObject, points: List[GeoPoint], *args, **kwargs) -> None:
        """
        Create a new line.
        """
        for pnt in points:
            if type(pnt) is not GeoPoint:
                raise ValueError("At least on point in points is not of type GeoPoint!")

        self.is_closed = bool(closed)
        self.horizon = horizon
        self.points = points

        # check doubled values and stratigraphy in the line
        self.__remove_doubled_points()
        self.__check_line()

        # call base class constructor
        AbstractDBObject.__init__(self, *args, **kwargs)

        if self.name_col == "":
            self.name_col = "line_{}".format(self.id)

    def __repr__(self) -> str:
        text = "<Line(id='{}', closed='{}', horizon='{}'\n)>".format(self.id, self.closed, str(self.horizon))
        text += AbstractDBObject.__repr__(self)
        text += "\npoints=\n" + str(self.points)
        return text

    def __str__(self) -> str:
        text = "[{}] {} - {}\n".format(self.id, "closed" if self.closed else "not closed", str(self.horizon))
        text += AbstractDBObject.__str__(self)
        text += "\npoints:\n"

        for point in self.points:
            text += "\n{}".format(str(point))

        return text

    @property
    def is_closed(self) -> bool:
        """
        True if the line is closed else False

        :raises ValueError: if value is not compatible to type bool
        """
        return self.closed

    @is_closed.setter
    def is_closed(self, value: bool) -> None:
        """
        see getter
        """
        value = bool(value)
        self.closed = bool(value)

    @property
    def horizon(self) -> StratigraphicObject:
        """
        The stratigraphy of the line object

        :raises TypeError: Raises TypeError if value is not of type Stratigraphy
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

        # check stratigraphy
        self.__check_line()

    def insert_point(self, point: GeoPoint, position: int) -> None:
        """
        Insert a point at the committed index.

        :param point: point to be inserted in the line
        :param position: Index, where points should be inserted in the line (starting with 0)
        :return: Nothing
        :raises TypeError: Raises TypeError if point is not of type GeoPoint
        :raises ValueError: Raises ValueError if position is not of type int or cannot be converted to int
        """
        position = int(position)
        if type(point) is not GeoPoint:
            raise TypeError("point {} is not of type GeoPoint!".format(str(point)))
        else:
            self.points.insert(position, point)

        # check doubled values and stratigraphy in the line
        self.__remove_doubled_points()
        self.__check_line()

    def insert_points(self, points: List[GeoPoint], position: int) -> None:
        """
        Insert a list of points at the committed index.

        :param points: List of points
        :param position: Index, where points should be inserted
        :return: Nothing
        :raises TypeError: Raises TypeError if one of the points is not of type GeoPoint
        :raises ValueError: Raises ValueError if position is not of type int or cannot be converted to int
        """
        position = int(position)

        for pnt in points:
            if type(pnt) is not GeoPoint:
                raise TypeError("At least on point in points is not of type GeoPoint!")

        # use slicing for points insert
        if len(self.points) <= position:
            self.points[-1:-1] = points
        else:
            self.points[position:position] = points

        # check doubled values and stratigraphy in the line
        self.__remove_doubled_points()
        self.__check_line()

    def get_point_index(self, point: GeoPoint) -> int:
        """
        Returns the index of the given point in the line

        :param point: point which has to be looked up
        :return: Index in the line
        :raises ValueError: Raises ValueError if committed point is not part of the line
        """
        return self.points.index(point)

    def delete_point(self, point: GeoPoint) -> None:
        """
        Deletes the point from the line

        :param point: GeoPoint object which should be deleted
        :return: Nothing
        :raises TypeError: Raises TypeError if point is not of type GeoPoint
        :raises ValueError: Raises ValueError the point is not part of the line
        """
        if type(point) is not GeoPoint:
            raise TypeError("point {} is not of type GeoPoint!".format(str(point)))

        try:
            self.points.remove(point)
        except ValueError as e:
            raise ValueError(str(e) + "\nGeoPoint with ID " + str(point.id) + " not found in list!")

        # check doubled values and stratigraphy in the line
        self.__remove_doubled_points()
        self.__check_line()

    def delete_point_by_coordinates(self, easting: float, northing: float, altitude: float = 0) -> None:
        """
        Deletes a point with the given coordinates from the line

        :param easting: easting value of the point to be deleted
        :param northing: northing value of the point to be deleted
        :param altitude: altitude value of the point to be deleted (only necessary if point has z-values!)
        :return: Nothing
        :raises ValueError: Raises ValueError if one parameter is not compatible to type float or no point can be found
        """
        try:
            easting = float(easting)
            northing = float(northing)
            altitude = float(altitude)
        except ValueError:
            raise ValueError("On of the input coordinates is not of type float!")

        # iterate over a copy of the list to avoid iteration issues caused by the deletion of values
        for pnt in self.points[:]:
            if (abs(float(pnt.easting) - easting) < float_precision) and (
                    abs(float(pnt.northing) - northing) < float_precision) and (
                    (abs(float(pnt.altitude) - altitude) < float_precision) or not pnt.has_z):
                self.points.remove(pnt)
                # check doubled values in a line
                self.__remove_doubled_points()
                self.__check_line()
                return

        raise ValueError("Point not found with coordinates {0}/{1}/{2}".format(easting, northing, altitude))

    def __check_line(self) -> None:
        """
        Checks the line for inconsistencies.
        Current checks:
        - stratigraphy check for all points

        :return: Nothing
        """
        for point in self.points:
            point.horizon = self.horizon

    def __remove_doubled_points(self) -> None:
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

        # reorder to ensure right position value without reloading from database
        self.points.reorder()

    @classmethod
    def load_in_extent_from_db(cls, session: Session, min_easting: float, max_easting: float, min_northing: float,
                               max_northing: float) -> List["Line"]:
        """
        Returns all lines with at least on point inside the given extent in the database connected to the SQLAlchemy
        Session session. Overloads the
        :meth:`AbstractGeoObject.load_in_extent_from_db()<geological_toolbox.geo_object.AbstractGeoObject.load_in_extent_from_db>`
        function.

        :param min_easting: minimal easting of extent
        :param max_easting: maximal easting of extent
        :param min_northing: minimal northing of extent
        :param max_northing: maximal northing of extent
        :param session: represents the database connection as SQLAlchemy Session
        :return: a list of lines representing the result of the database query
        :raises ValueError: if one of the extension values is not compatible to type float
        :raises TypeError: if session is not of type SQLAlchemy Session
        """
        min_easting = float(min_easting)
        max_easting = float(max_easting)
        min_northing = float(min_northing)
        max_northing = float(max_northing)

        if not isinstance(session, Session):
            raise TypeError("'session' is not of type SQLAlchemy Session!")

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
