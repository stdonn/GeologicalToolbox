"""
This module hosts the class Requests, which provides functionality for special (geo-)database requests.

.. todo:: - reformat docstrings, especially of setter and getter functions
          - check exception types
"""
from sqlalchemy.orm.session import Session
from typing import List

from Exceptions import ListOrderException
from Resources.Geometries import GeoPoint
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
    def __check_extent(extent):
        # type: (List[float, float, float, float]) -> None
        """
        checks, if the given extent has the right format

        :param extent: value to be checked
        :type extent:
        :return: Nothing
        :raises TypeError: if extent is not a list
        :raises ValueError: if on list element is not compatible to float or number of elements is not 4
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
        :param summarise_multiple: Summarise multiple occurrences of marker_1 and marker_2 to a maximum thickness. If
        this parameter is False (default value) create multiple points.
        :type summarise_multiple: bool
        :param extent: List of an extension rectangle which borders the well distribution. The list has the following order:
                       [min easting, max easting, min northing, max northing]
        :type extent: [float, float, float, float]
        :return: A list of GeoPoints each with a thickness property
        :rtype: [GeoPoint]
        :raises ValueError: if a parameter is not compatible with the required type
        """
        summarise = True
        extent = None
        for i in range(len(*args)):
            if i == 0:
                summarise = bool(args[i])
            elif i == 1:
                Requests.__check_extent(args[i])
                extent = args[i]

        for key in kwargs:
            if key == 'summarise_multiple':
                summarise = bool(kwargs[key])
            elif key == 'extent':
                Requests.__check_extent(kwargs[key])
                extent = kwargs[key]


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
