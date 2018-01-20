# -*- coding: UTF-8 -*-
"""
A module controlling the import of point data into a database.
:raises ArgumentError: if number of Arguments is wrong (at least three)
"""

from sqlalchemy.orm.session import Session

from ModellingToolbox.Exceptions import ArgumentError
from ModellingToolbox.Resources.DBHandler import DBHandler
from ModellingToolbox.Resources.Geometries import GeoPoint
from ModellingToolbox.Resources.Stratigraphy import StratigraphicObject

from arcpy import AddWarning

import os
import sys


class PointImport:
    """
    the base class for importing point data
    """

    def __init__(self, sessionobject):
        # type: (Session) -> None
        """
        Initialisation of the class to save the global SQLAlchemy session

        :param sessionobject: Current SQLAlchemy session
        :type sessionobject: Session
        """
        self.session = sessionobject

    def import_from_file(self, *args):
        # type: (*str) -> None
        """
        Imports point data from a text file.

        :param args: necessary arguments submitted from the ArcGIS toolbox
        :param args: *str
        :return: nothing
        :raises ArgumentError: if the number of arguments is wrong
        """
        if len(args) < 9:
            arguments = "data file path and following column numbers (starting with 1):\n"
            arguments += "easting, northing, altitude, stratigraphy, stratigraphic age, point set name, comment\n"
            arguments += "column separator inside the data file"
            raise ArgumentError('Missing arguments. Should be:\n{}'.format(arguments))

        point_data = args[0]
        separator = args[8]
        columns = {
            'easting'  : int(args[1]) - 1,
            'northing' : int(args[2]) - 1,
            'altitude' : int(args[3]) - 1,
            'strat'    : int(args[4]) - 1,
            'age'      : int(args[5]) - 1,
            'point_set': int(args[6]) - 1,
            'comment'  : int(args[7]) - 1
        }

        for key in columns:
            if columns[key] < -1:
                columns[key] = 1

        if -1 in (columns['easting'], columns['northing']):
            raise ArgumentError('You have to specify a column for easting, northing and altitude values!')

        point_file = open(point_data, "r")

        for line in point_file:
            line = line.rstrip()
            line = line.split(separator)

            result = dict()
            for col in columns:
                if col != -1:
                    result[col] = line[columns[col]]
                else:
                    result[col] = None

            strat = None
            try:
                if result['strat'] is not None:
                    strat = StratigraphicObject.init_stratigraphy(self.session, result['strat'], result['age'], False)
                point = GeoPoint(strat, result['altitude'] is not None, '', result['easting'], result['northing'],
                                 result['altitude'], self.session, result['point_set'], result['comment'])

                point.save_to_db()
            except ValueError:
                AddWarning('Cannot convert line:\n{}'.format(str(line)))
                for key in result:
                    AddWarning("result['{}']:\t{}".format(key, result[key]))

        point_file.close()


if __name__ == '__main__':
    """
    main function of the module
    """
    if len(sys.argv) < 3:
        raise ArgumentError(
                "Too less arguments. You need at least the method name and the connection / path of a database!")

    method = sys.argv[1]
    db = os.path.normpath(sys.argv[2])
    handler = DBHandler(connection='sqlite:///' + db + '.sqlite', echo=False)
    session = handler.get_session()
    # noinspection PyTypeChecker
    point_data = PointImport(session)

    if method == 'import_from_file':
        point_data.import_from_file(sys.argv[4:])
