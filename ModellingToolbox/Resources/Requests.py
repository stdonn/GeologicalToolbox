"""
This module hosts the class Requests, which provides functionality for special (geo-)database requests.

.. todo:: - reformat docstrings, especially of setter and getter functions
          - check exception types
"""

import sqlalchemy as sq
from sqlalchemy.orm.session import Session
from typing import List

from Exceptions import ListOrderException
from Resources.Geometries import GeoPoint
from Resources.Stratigraphy import StratigraphicObject
from Resources.Wells import Well, WellMarker


class Requests:
    """
    The class Requests, which provides functionality for special (geo-)database requests.
    """

    def __init__(self):
        # type: () -> None
        """
        Initialise the class

        -> Currently nothing to do...
        """
        pass

    @staticmethod
    def check_extent(extent):
        # type: (List[float, float, float, float]) -> None
        """
        checks, if the given extent has the right format

        :param extent: value to be checked
        :type extent:
        :return: Nothing
        :raises TypeError: if extent is not a list
        :raises ValueError: if on list element is not compatible to float or number of elements is not 4
        :raises ListOrderException: if the ordering of the extent list [min_easting, max_easting, min_northing,
                max_northing] is wrong.
        """
        if not isinstance(extent, List):
            raise TypeError("extent is not an instance of List()!")
        if len(extent) != 4:
            raise ValueError("Number of extension list elements is not 4!")
        for i in range(len(extent)):
            try:
                extent[i] = float(extent[i])
            except ValueError as e:
                raise ValueError('At least on extent element cannot be converted to float!\n' + e.message)
        if extent[0] > extent[1]:
            raise ListOrderException("min easting > max easting")
        if extent[2] > extent[3]:
            raise ListOrderException("min northing > max northing")

    @staticmethod
    def well_markers_to_thickness(session, marker_1, marker_2, *args, **kwargs):
        # type: (Session, WellMarker, WellMarker, *object, **object) -> List[GeoPoint]
        """
        This static method generates a point set including a thickness property derived from the committed well marker

        .. todo:: - Finalise the well_markers_to_thickness(...) function

        :param session: The SQLAlchemy session connected to the database storing the geodata
        :type session: Session
        :param marker_1: First WellMarker
        :type marker_1: WellMarker
        :param marker_2: Second WellMarker
        :type marker_2: WellMarker
        :param summarise_multiple: Summarise multiple occurrences of marker_1 and marker_2 to a maximum thickness. If this parameter is False (default value) create multiple points.
        :type summarise_multiple: bool
        :param extent: List of an extension rectangle which borders the well distribution. The list has the following order: [min easting, max easting, min northing, max northing]
        :type extent: [float, float, float, float]
        :return: A list of GeoPoints each with a thickness property
        :rtype: [GeoPoint]
        :raises ValueError: if a parameter is not compatible with the required type
        :raises TypeError: if session is not an instance of SQLAlchemy session

        for further raises see :meth:`Requests.check_extent`

        Query for selecting markers:

        .. code-block:: sql
            :linenos:

            SELECT wm1.* FROM well_marker wm1
            JOIN stratigraphy st1
            ON wm1.horizon_id = st1.id
            WHERE st1.unit_name IN ("mu", "so")
            AND EXISTS
            (
                SELECT 1 FROM well_marker wm2
                JOIN stratigraphy st2
                ON wm2.horizon_id = st2.id
                WHERE st2.unit_name IN ("mu", "so")
                AND wm1.well_id = wm2.well_id
                AND st1.unit_name <> st2.unit_name
            )
        """
        if not isinstance(session, Session):
            raise TypeError("session is not of type SQLAlchemy Session")

        summarise = True
        extent = None
        for i in range(len(args)):
            if i == 0:
                summarise = bool(args[i])
            elif i == 1:
                Requests.check_extent(args[i])
                extent = args[i]

        for key in kwargs:
            if key == 'summarise_multiple':
                summarise = bool(kwargs[key])
            elif key == 'extent':
                Requests.check_extent(kwargs[key])
                extent = kwargs[key]

        statement = sq.text("SELECT wm1.* FROM well_marker wm1 JOIN stratigraphy st1 ON wm1.horizon_id = st1.id " +
                            "WHERE st1.unit_name IN (:marker1, :marker2) AND EXISTS " +
                            "( SELECT 1 FROM well_marker wm2 JOIN stratigraphy st2 ON wm2.horizon_id = st2.id " +
                            "WHERE st2.unit_name IN (:marker1, :marker2) AND wm1.well_id = wm2.well_id " +
                            "AND st1.unit_name <> st2.unit_name)")
        result = session.query(WellMarker).from_statement(statement).params(marker1=marker_1, marker2=marker_2).all()

        return result

    @staticmethod
    def interpolate_geopoints(points, property_name, method):
        # type: (List[GeoPoint], str, str) -> None
        """
        Interpolate the property values of the given GeoPoints using the interpolation method 'method'

        .. todo:: - Integrate functionality
                  - define interpolation methods
                  - define return statement

        :param points: List of GeoPoints as interpolation base
        :type points: List[GeoPoint]

        :param property_name: Name of the property to interpolate
        :type property_name: str

        :param method: Interpolation method
        :type method: str

        :return: Currently Nothing
        :raises TypeError: if on of the points is not of type GeoPoint

        possible values for interpolation **method** are:

        - **nearest** (Nearest Neighbour interpolation)
        - **ide** (Inverse Distance interpolation)
        - **spline** (Thin-Plate-Spline interpolation)
        """
