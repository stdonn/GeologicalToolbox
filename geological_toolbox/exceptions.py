# -*- coding: UTF-8 -*-
"""
Module providing package wide Exceptions
"""


class ArgumentError(Exception):
    """
    Should be raised, if a wrong number of arguments are submitted or an other failure inside the arguments are
    recognised.

    :param msg: detailed error message
    """

    def __init__(self, msg: str) -> None:
        self.message = str(msg)

    def __str__(self) -> str:
        return self.message


class DatabaseException(Exception):
    """
    Should be raised, if an unresolved database issue occurred (e.g. more than one value in a unique column)

    :param msg: detailed error message
    """

    def __init__(self, msg: str) -> None:
        self.message = str(msg)

    def __str__(self) -> str:
        return self.message


class DatabaseRequestException(Exception):
    """
    Should be raised, if an error occurs during a database request (e.g. not the expected result)

    :param msg: detailed error message
    """

    def __init__(self, msg: str) -> None:
        self.message = str(msg)

    def __str__(self) -> str:
        return self.message


class FaultException(Exception):
    """
    Should be raised, if a fault marker causes an interruption

    :param msg: detailed error message
    """

    def __init__(self, msg: str) -> None:
        self.message = str(msg)

    def __str__(self) -> str:
        return self.message


class ListOrderException(Exception):
    """
    Should be raised, if the ordering of a list is wrong (e.g. min values in an extent list after max...)

    :param msg: detailed error message
    """

    def __init__(self, msg: str) -> None:
        self.message = str(msg)

    def __str__(self) -> str:
        return self.message


class WellMarkerDepthException(Exception):
    """
    Should be raised, if a new well marker should be located deeper than the depth of the well

    :param msg: detailed error message
    """

    def __init__(self, msg: str) -> None:
        self.message = str(msg)

    def __str__(self) -> str:
        return self.message
