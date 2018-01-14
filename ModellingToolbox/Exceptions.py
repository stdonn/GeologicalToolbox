# -*- coding: UTF-8 -*-

class ArgumentError(Exception):
    """
    This exception should be raised, if a wrong number of arguments are submitted or an other failure inside the
    arguments are recognised.
    """
    def __init__(self, msg):
        self.message = str(msg)

    def __str__(self):
        return self.message


class DatabaseException(Exception):
    """
    This exception should be raised, if an unresolved database issue occurred (e.g. more than one value in a unique
    column
    """

    def __init__(self, msg):
        self.message = str(msg)

    def __str__(self):
        return self.message


class DatabaseRequestException(Exception):
    """
    This exception should be raised, if an error occurs during a database request (e.g. not the expected result)
    """

    def __init__(self, msg):
        self.message = str(msg)

    def __str__(self):
        return self.message


class FaultException(Exception):
    """
    Will be raised, if a fault marker causes an interruption
    """

    def __init__(self, msg):
        self.message = str(msg)

    def __str__(self):
        return self.message


class ListOrderException(Exception):
    """
    Will be raised, if the ordering of a list is wrong (e.g. min values in an extent list after max...)
    """

    def __init__(self, msg):
        self.message = str(msg)

    def __str__(self):
        return self.message


class WellMarkerDepthException(Exception):
    """
    Will be raised, if a new well marker should be located deeper than the depth of the well
    """

    def __init__(self, msg):
        self.message = str(msg)

    def __str__(self):
        return self.message
