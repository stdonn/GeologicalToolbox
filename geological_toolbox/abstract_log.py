# -*- coding: UTF-8 -*-
"""
This module provides an abstract base class for storing logging or property information.
"""

import sqlalchemy as sq
import sys

from geological_toolbox.db_handler import AbstractDBObject


class AbstractLogClass(AbstractDBObject):
    """
    This class is the base for storing logging information or properties. It should be treated as abstract, no
    object should be created directly!

    :param property_name: name of the log or property
    :param property_unit: unit of the log values or properties
    :return: Nothing
    """

    # define table_columns
    prop_name = sq.Column(sq.VARCHAR(50), default="")
    prop_unit = sq.Column(sq.VARCHAR(100), default="")

    def __init__(self, property_name: str, property_unit: str, *args, **kwargs) -> None:
        """
        Initialises the class
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
    def property_name(self) -> str:
        """
        name of the property

        :return: the name of the property
        """
        return str(self.prop_name)

    @property_name.setter
    def property_name(self, name: str) -> None:
        """
        name of the property

        :param name: new property name
        :return: Nothing
        """
        name = str(name)
        if len(name) > 100:
            name = name[:100]
        self.prop_name = name

    @property
    def property_unit(self) -> str:
        """
        property unit as string

        :return: the unit of the property
        """
        if sys.version_info[0] == 2:
            return self.prop_unit
        else:
            return self.prop_unit

    @property_unit.setter
    def property_unit(self, unit: str) -> None:
        """
        property unit as string

        :param unit: property unit as string
        :return: Nothing
        """
        if sys.version_info[0] == 2:
            unit = unit

        if len(unit) > 100:
            unit = unit[:100]
        self.prop_unit = unit


