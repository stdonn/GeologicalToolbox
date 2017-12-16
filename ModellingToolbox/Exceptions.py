# -*- coding: UTF-8 -*-


class DatabaseException(Exception):
    """
    This exception should be raised if an unresolved database issue occurred (e.g. more than one value in a unique
    column
    """

    def __init__(self, msg):
        self.message = str(msg)

    def __str__(self):
        return self.message


class WellMarkerDepthException(Exception):
    """
    Will be raised if a new well marker should be located deeper than the depth of the well
    """

    def __init__(self, msg):
        self.message = str(msg)

    def __str__(self):
        return self.message


class ListOrderException(Exception):
    """
    Will be raised if the ordering of a list is wrong (e.g. min values in an extent list after max...)
    """

    def __init__(self, msg):
        self.message = str(msg)

    def __str__(self):
        return self.message
