# -*- coding: UTF-8 -*-
"""
A module controlling the import of point data into a database.
:raises ArgumentError: if number of Arguments is wrong (at least three)
"""

from ModellingToolbox.Exceptions import ArgumentError
from ModellingToolbox.Resources.DBHandler import DBHandler

from sqlalchemy.orm.session import Session

import arcpy
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
        if len(args) < 5:
            raise ArgumentError('Too less arguments ({}). Should be {}.'.format(len(args), 5))


if __name__ == '__main__':
    """
    main function of the module
    """
    if len(sys.argv) < 3:
        raise ArgumentError(
            "Too less arguments. You need at least the method name and the connection / path of a database!")

    method = sys.argv[1]
    db = os.path.normpath(sys.argv[2])
    handler = DBHandler(connection='sqlite:///' + db, echo=False)
    session = handler.get_session()
    # noinspection PyTypeChecker
    misc = PointImport(session)

    if method == 'import_from_file':
        misc.import_from_file(sys.argv[4:])
