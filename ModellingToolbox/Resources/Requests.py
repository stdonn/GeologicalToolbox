"""
This module hosts the class Requests, which provides functionality for special (geo-)database requests.

.. todo:: - reformat docstrings, especially of setter and getter functions
          - check exception types
"""

import sqlalchemy as sq
from sqlalchemy.orm.session import Session
from typing import List

from Exceptions import ListOrderException, FaultException
from Resources.Geometries import GeoPoint
from Resources.PropertyLogs import Property
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
    def _create_thickness_point(sorted_dict, well_id, marker_1, marker_2, use_faulted, fault_name, session):
        # type: (dict, int, int, int, bool, str, Session) -> GeoPoint
        """
        Generate a new GeoPoint with thickness property from 2 well marker

        :param sorted_dict: dictionary containing well_id / WellMarker data
        :type sorted_dict: dict()
        :param well_id: current well_id
        :type well_id: int
        :param marker_1: id of marker 1
        :type marker_1: int
        :param marker_2: id of marker 2
        :type marker_2: int
        :param use_faulted: should faulted sequence be included?
        :type use_faulted: bool
        :param fault_name: name of fault stratigraphic unit
        :type fault_name: str
        :param session: current SQLAlchemy session
        :type session: Session
        :return: new GeoPoint Object
        :rtype: GeoPoint
        :raises FaultException: if a fault is inside the section and use_faulted is False
        """

        min_depth = sorted_dict[well_id][marker_1].depth
        max_depth = sorted_dict[well_id][marker_2].depth

        faults = session.query(WellMarker).join(StratigraphicObject). \
            filter(WellMarker.horizon_id == StratigraphicObject.id). \
            filter(StratigraphicObject.unit_name == fault_name). \
            filter(WellMarker.well_id == well_id)
        if min_depth > max_depth:
            faults = faults.filter(sq.between(WellMarker.drill_depth, max_depth, min_depth))
        else:
            faults = faults.filter(sq.between(WellMarker.drill_depth, min_depth, max_depth))
        if (faults.count() > 0) and (use_faulted is False):
            raise FaultException("Fault inside section")

        point = sorted_dict[well_id][0].to_geopoint()
        thickness = Property('thickness', 'm', session)
        thickness.value = max_depth - min_depth
        point.add_property(thickness)
        if use_faulted:
            faulted = Property('faulted', '', session)
            if faults.count() > 0:
                faulted.value = 1
            else:
                faulted.value = 1
            point.add_property(faulted)
        return point

    @staticmethod
    def well_markers_to_thickness(session, marker_1, marker_2, *args, **kwargs):
        # type: (Session, str, str, *object, **object) -> List[GeoPoint]
        """
        This static method generates a point set including a thickness property derived from the committed well marker

        .. todo:: - Finalise the well_markers_to_thickness(...) function

        :param session: The SQLAlchemy session connected to the database storing the geodata
        :type session: Session
        :param marker_1: First WellMarker unit name
        :type marker_1: str
        :param marker_2: Second WellMarker unit name
        :type marker_2: str
        :param summarise_multiple: Summarise multiple occurrences of marker_1 and marker_2 to a maximum thickness. If this parameter is False (default value) create multiple points.
        :type summarise_multiple: bool
        :param extent: List of an extension rectangle which borders the well distribution. The list has the following order: [min easting, max easting, min northing, max northing]
        :type extent: [float, float, float, float]
        :param use_faulted: if True, also sections with faults between marker_1 and marker_2 are returned
        :type use_faulted: bool
        :param fault_name: unit name of fault marker (standard: 'Fault')
        :type fault_name: str
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
            ORDER BY wm1.well_id,wm1.drill_depth
        """
        if not isinstance(session, Session):
            raise TypeError("session is not of type SQLAlchemy Session")

        summarise = True
        extent = None
        use_faulted = False
        fault_name = 'Fault'
        for i in range(len(args)):
            if i == 0:
                summarise = bool(args[i])
            elif i == 1:
                Requests.check_extent(args[i])
                extent = args[i]
            elif i == 2:
                use_faulted = bool(args[i])
            elif i == 3:
                fault_name = str(args[i])

        for key in kwargs:
            if key == 'summarise_multiple':
                summarise = bool(kwargs[key])
            elif key == 'extent':
                Requests.check_extent(kwargs[key])
                extent = kwargs[key]
            elif key == 'use_faulted':
                use_faulted = bool(kwargs[key])
            elif key == 'fault_name':
                fault_name = str(kwargs[key])

        statement = sq.text("SELECT wm1.* FROM well_marker wm1 JOIN stratigraphy st1 ON " +
                            "wm1.horizon_id = st1.id WHERE st1.unit_name IN (:marker1, :marker2) AND EXISTS " +
                            "( SELECT 1 FROM well_marker wm2 JOIN stratigraphy st2 ON wm2.horizon_id = st2.id " +
                            "WHERE st2.unit_name IN (:marker1, :marker2) AND wm1.well_id = wm2.well_id " +
                            "AND st1.unit_name <> st2.unit_name) ORDER BY wm1.well_id,wm1.drill_depth")
        result = session.query(WellMarker).from_statement(statement).params(marker1=marker_1, marker2=marker_2).all()

        # first: sort by well_id for simpler multiple marker check
        sorted_dict = dict()
        for i in range(len(result)):
            if result[i].well_id not in sorted_dict:
                sorted_dict[result[i].well_id] = list()
            sorted_dict[result[i].well_id].append(result[i])

        del result

        # generate the resulting list of GeoPoints
        geopoints = list()
        for well_id in sorted_dict:

            if len(sorted_dict[well_id]) == 2:
                sorted_dict[well_id][0].session = session
                try:
                    point = Requests._create_thickness_point(sorted_dict, well_id, 0, 1, use_faulted, fault_name,
                                                             session)
                    geopoints.append(point)
                except FaultException:
                    continue

        return geopoints

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
