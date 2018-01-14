# -*- coding: UTF-8 -*-
"""
This module provides miscellaneous functions and tools, which are not related to one of the others or to multiple of the
other modules.
"""

from Exceptions import ArgumentError
from Resources.DBHandler import DBHandler
from sqlalchemy.orm.session import Session

# import arcpy
import os
import sys


class Miscellaneous:
    """
    miscellaneous functions, which are not related to one of the others or to multiple of the other classes.
    """

    def __init__(self, sessionobject):
        # type: (Session) -> None
        """
        Initialisation of the class to save the global SQLAlchemy session

        :param sessionobject: Current SQLAlchemy session
        :type sessionobject: Session
        """
        self.session = sessionobject


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise ArgumentError(
            "Too less arguments. You need at least the method name and the connection / path of a database!")

    method = sys.argv[1]
    db = os.path.normpath(sys.argv[2])
    handler = DBHandler(connection='sqlite:///' + db, echo=False)

    if method == 'createDB':
        # we have a handler, so database file is created, enough for ArcGIS -> Exit
        sys.exit()

    session = handler.get_session()
    # noinspection PyTypeChecker
    misc = Miscellaneous(session)
