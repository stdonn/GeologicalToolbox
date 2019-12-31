"""
This module hosts the class Requests, which provides functionality for special (geo-)database requests.
"""

import sqlalchemy as sq
from sqlalchemy.orm.session import Session
from typing import List, Tuple

from geological_toolbox.exceptions import DatabaseException, DatabaseRequestException, FaultException, \
    ListOrderException
from geological_toolbox.geometries import GeoPoint
from geological_toolbox.properties import Property, PropertyTypes
from geological_toolbox.stratigraphy import StratigraphicObject
from geological_toolbox.wells import WellMarker


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
    def check_extent(extent: List[float]) -> None:
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
        if extent is None:
            return

        if not isinstance(extent, List):
            raise TypeError("extent is not an instance of List()!")
        if len(extent) != 4:
            raise ValueError("Number of extension list elements is not 4!")
        for i in range(len(extent)):
            try:
                extent[i] = float(extent[i])
            except ValueError as e:
                raise ValueError("At least on extent element cannot be converted to float!\n{}".format(e))
        if extent[0] > extent[1]:
            raise ListOrderException("min easting > max easting")
        if extent[2] > extent[3]:
            raise ListOrderException("min northing > max northing")

    @staticmethod
    def create_thickness_point(sorted_dict: dict, well_id: int, marker_1: int, marker_2: int, session: Session,
                               use_faulted: bool = False, fault_name: str = "",
                               add_properties: Tuple = tuple()) -> GeoPoint:
        """
        Generate a new GeoPoint with thickness property from 2 well marker

        :param sorted_dict: dictionary containing well_id / WellMarker data
        :param well_id: current well_id
        :param marker_1: id of marker 1
        :param marker_2: id of marker 2
        :param session: current SQLAlchemy session
        :param use_faulted: should faulted sequence be included?
        :param fault_name: name of fault stratigraphic unit (default: "Fault")
        :param add_properties: Adds the properties to the GeoPoint. Format for each property: (value, type, name, unit)
        :return: new GeoPoint Object
        :raises FaultException: if a fault is inside the section and use_faulted is False
        :raises ValueError: if a property in the add_property tuple has less than 3 entries
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

        point = sorted_dict[well_id][marker_1].to_geopoint()
        thickness = Property(max_depth - min_depth, PropertyTypes.FLOAT, "thickness", "m", session)
        point.add_property(thickness)
        if use_faulted:
            faulted = Property(faults.count(), PropertyTypes.INT, "faulted", "count", session)
            point.add_property(faulted)
        for prop in add_properties:
            if len(prop) < 4:
                raise ValueError("property tuple has less than 4 entries!")
            new_property = Property(prop[0], PropertyTypes[prop[1]], prop[2], prop[3], session)
            point.add_property(new_property)
        return point

    @staticmethod
    def well_markers_to_thickness(session: Session, marker_1: str, marker_2: str, summarise_multiple: bool = False,
                                  extent: Tuple[int, int, int, int] or None = None, use_faulted: bool = False,
                                  fault_name: str = "Fault") -> List[GeoPoint]:
        """
        Static method for generating a point set including a thickness property derived from the committed well marker

        :param session: The SQLAlchemy session connected to the database storing the geodata
        :param marker_1: First WellMarker unit name
        :param marker_2: Second WellMarker unit name
        :param summarise_multiple: Summarise multiple occurrences of marker_1 and marker_2 to a maximum thickness.
               If this parameter is False (default value) create multiple points.
        :param extent: extension rectangle as list which borders the well distribution. The list has the following
               order: (min easting, max easting, min northing, max northing)
        :param use_faulted: if True, also sections with faults between marker_1 and marker_2 are returned
        :param fault_name: unit name of fault marker (default: "Fault")
        :return: A list of GeoPoints each with a thickness property
        :raises AttributeError: if marker_1 and marker_2 are equal
        :raises DatabaseException: if the database query results in less than 2 marker of a well_id
        :raises DatabaseRequestException: if an unexpected query result occurs
        :raises TypeError: if session is not an instance of SQLAlchemy session
        :raises ValueError: if a parameter is not compatible with the required type

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

        if marker_1 == marker_2:
            raise AttributeError("marker_1 and marker_2 cannot be equal!")

        if extent is not None:
            Requests.check_extent(extent)

        result = session.query(WellMarker)
        if extent is None:
            statement = sq.text("SELECT wm1.* FROM well_marker wm1 " +
                                "JOIN stratigraphy st1 ON wm1.horizon_id = st1.id " +
                                "WHERE st1.unit_name IN (:marker1, :marker2) " +
                                "AND EXISTS " +
                                "( SELECT 1 FROM well_marker wm2 JOIN stratigraphy st2 ON wm2.horizon_id = st2.id " +
                                "WHERE st2.unit_name IN (:marker1, :marker2) AND wm1.well_id = wm2.well_id " +
                                "AND st1.unit_name <> st2.unit_name) ORDER BY wm1.well_id,wm1.drill_depth")
            result = result.from_statement(statement). \
                params(marker1=marker_1, marker2=marker_2). \
                all()
        else:
            statement = sq.text("SELECT wm1.* FROM well_marker wm1 " +
                                "JOIN wells ON wm1.well_id = wells.id " +
                                "JOIN stratigraphy st1 ON wm1.horizon_id = st1.id " +
                                "WHERE wells.east BETWEEN :east_min AND :east_max " +
                                "AND wells.north BETWEEN :north_min AND :north_max " +
                                "AND st1.unit_name IN (:marker1, :marker2)" +
                                "AND EXISTS " +
                                "( SELECT 1 FROM well_marker wm2 JOIN stratigraphy st2 ON wm2.horizon_id = st2.id " +
                                "WHERE st2.unit_name IN (:marker1, :marker2) AND wm1.well_id = wm2.well_id " +
                                "AND st1.unit_name <> st2.unit_name) ORDER BY wm1.well_id,wm1.drill_depth")
            result = result.from_statement(statement). \
                params(marker1=marker_1, marker2=marker_2, east_min=extent[0], east_max=extent[1], north_min=extent[2],
                       north_max=extent[3]). \
                all()

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
            if len(sorted_dict[well_id]) < 2:
                raise DatabaseException("Not enough well marker in dictionary")
            if len(sorted_dict[well_id]) == 2:
                sorted_dict[well_id][0].session = session
                try:
                    if summarise_multiple:
                        point = Requests.create_thickness_point(
                            sorted_dict, well_id, 0, 1, session, use_faulted, fault_name,
                            ((0, "INT", "summarised", "bool"),))
                        geopoints.append(point)
                    else:
                        point = Requests.create_thickness_point(
                            sorted_dict, well_id, 0, 1, session, use_faulted, fault_name,
                            ((0, "INT", "multiple marker", "bool"),))
                        geopoints.append(point)
                # FaultException -> do nothing except catching the exception
                except FaultException:
                    continue
                # don't test anything else for this well_id
                continue

            # last case: more than 2 values found:
            if summarise_multiple:
                first_index = -1
                last_index = -1
                for i in range(len(sorted_dict[well_id])):
                    if sorted_dict[well_id][i].horizon.unit_name == marker_1:
                        first_index = i
                        break
                for j in reversed(range(len(sorted_dict[well_id]))):
                    if sorted_dict[well_id][j].horizon.unit_name == marker_2:
                        last_index = j
                        break

                if (first_index == -1) or (last_index == -1):
                    raise DatabaseRequestException("Didn't find two different markers. Shouldn't be possible. " +
                                                   "Please excuse this error and forward it to me.")

                # wrong order -> nothing to do...
                if last_index < first_index:
                    continue

                try:
                    sorted_dict[well_id][first_index].session = session
                    point = Requests.create_thickness_point(
                        sorted_dict, well_id, first_index, last_index, session, use_faulted, fault_name,
                        ((1, "INT", "summarised", "bool"),))
                    geopoints.append(point)
                # FaultException -> do nothing except catching the exception
                except FaultException:
                    continue

                # finished summarise section -> continue to avoid second round without summarise
                continue
            # don't summarise
            first_index = -1
            for index in range(len(sorted_dict[well_id])):
                if sorted_dict[well_id][index].horizon.unit_name == marker_1:
                    first_index = index
                elif (first_index != -1) and (sorted_dict[well_id][index].horizon.unit_name == marker_2):
                    try:
                        sorted_dict[well_id][first_index].session = session
                        point = Requests.create_thickness_point(
                            sorted_dict, well_id, first_index, index, session, use_faulted, fault_name,
                            ((1, "INT", "multiple marker", "bool"),))
                        geopoints.append(point)
                    # FaultException -> do nothing except catching the exception
                    except FaultException:
                        continue
                    finally:
                        first_index = -1

        return geopoints

    @staticmethod
    def interpolate_geopoints(points: GeoPoint, property_name: str, method: str) -> None:
        """
        Interpolate the property values of the given GeoPoints using the interpolation method "method"

        .. todo:: - Integrate functionality
                  - define interpolation methods
                  - define return statement

        :param points: List of GeoPoints as interpolation base
        :param property_name: Name of the property to interpolate
        :param method: Interpolation method
        :return: Currently Nothing
        :raises TypeError: if on of the points is not of type GeoPoint

        possible values for interpolation **method** are:

        - **nearest** (Nearest Neighbour interpolation)
        - **ide** (Inverse Distance interpolation)
        - **spline** (Thin-Plate-Spline interpolation)
        """
