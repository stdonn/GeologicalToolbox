# -*- coding: UTF-8 -*-
"""
This module provides an abstract base class for storing logging or property information.

.. todo:: - reformat docstrings, espacially of setter and getter functions
          - check exception types
"""

import sqlalchemy as sq
import sys

from GeologicalToolbox.DBHandler import AbstractDBObject


class AbstractLogClass(AbstractDBObject):
    """
    This class is the base for storing logging information or properties. This class should be treated as abstract, no
    object should be created directly!
    """

    # define table_columns
    prop_name = sq.Column(sq.VARCHAR(50), default='')
    prop_unit = sq.Column(sq.VARCHAR(100), default='')

    def __init__(self, property_name, property_unit, *args, **kwargs):
        # type: (str, str, *object, **object) -> None
        """
        Initialises the class

        :param property_name: name of the log or property
        :type property_name: str

        :param property_unit: unit of the log values or properties
        :type property_unit: str

        :returns: Nothing
        """

        self.property_name = property_name
        self.property_unit = property_unit

        AbstractDBObject.__init__(self, *args, **kwargs)

    def __repr__(self):
        text = "<AbstractLogClass property_name={}, property_unit={}\n".\
            format(self.property_name, self.property_unit)
        text += AbstractDBObject.__repr__(self)
        return text

    def __str__(self):
        text = "{} [{}]\n".format(self.property_name, self.property_unit)
        text += AbstractDBObject.__str__(self)
        return text

    @property
    def property_name(self):
        # type: () -> str
        """
        Returns the name of the property

        :return: Returns the name of the property
        """
        return str(self.prop_name)

    @property_name.setter
    def property_name(self, name):
        # type: (str) -> None
        """
        Set a new property name with a maximum length of 50 characters

        :param name: new property name
        :type name: str

        :return: Nothing
        """
        name = str(name)
        if len(name) > 100:
            name = name[:100]
        self.prop_name = name

    @property
    def property_unit(self):
        # type: () -> unicode
        """
        Returns the unit of the property

        :return: Returns the unit of the property
        """
        if sys.version_info[0] == 2:
            return unicode(self.prop_unit)
        else:
            return self.prop_unit

    @property_unit.setter
    def property_unit(self, unit):
        # type: (str) -> None
        """
        Set a new unit for the property with a maximum length of 100 characters

        :param unit: new unit for the property
        :type unit: str

        :return: Nothing
        """
        if sys.version_info[0] == 2:
            unit = unicode(unit)

        if len(unit) > 100:
            unit = unit[:100]
        self.prop_unit = unit


