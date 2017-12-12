"""
This module hosts the class Requests, which provides functionality for special (geo-)database requests.
"""

from typing import List
from Resources.Geometries import GeoPoint
from Resources.Wells import Well, WellMarker

import sqlalchemy as sq
from sqlalchemy.orm.session import Session


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
    def well_markers_to_thickness(session, marker_1, marker_2, *args, **kwargs):
        # type: (Session, WellMarker, WellMarker, *object, **object) -> List[GeoPoint]
        """
        This static method generates a point set including a thickness property derived from the committed well marker

        :param session: The SQLAlchemy session connected to the database storing the geodata
        :type session: Session

        :param marker_1: First WellMarker
        :type marker_1: WellMarker

        :param marker_2: Second WellMarker
        :type marker_2: WellMarker


        :param summarise_multiple: Summarise multiple occurrences of marker_1 and marker_2 to a maximum thickness. If this parameter is False (default value) create multiple points.
        :type summarise_multiple: bool

        :param extent: List of an extension rectangle which borders the well distribution. The list has the following order:
                       [min easting, max easting, min northing, max northing]
        :type extent: [float, float, float, float]

        :return: A list of GeoPoints each with a thickness property
        :rtype: [GeoPoint]

        :raises TypeError: Raises TypeError if a parameter is not compatible with the required type
        """
        pass