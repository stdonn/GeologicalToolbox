# -*- coding: UTF-8 -*-
"""
This module provides a class for storing properties of points (and therefore also for lines). Properties for points are
the same as logs, except there is only one value, not a list of values. They are both derived from the
:class:`~geological_toolbox.abstract_log.AbstractLogClass`.
"""

import sqlalchemy as sq

from enum import Enum
from geological_toolbox.abstract_log import AbstractLogClass
from geological_toolbox.db_handler import Base, AbstractDBObject


class PropertyTypes(Enum):
    """Enum defining currently handled property types"""
    STRING = 0,
    """Representing a string"""
    INT = 1,
    """Representing an integer"""
    FLOAT = 2
    """Representing a float"""


class Property(Base, AbstractLogClass):
    """
    This class represents logging information for wells.
    For further details see :class:`~geological_toolbox.db_handler.AbstractLogClass`

    :param args: parameters for AbstractLogClass initialisation
    :param kwargs: parameters for AbstractLogClass initialisation
    """
    # define db table name and columns
    __tablename__ = "properties"

    id = sq.Column(sq.INTEGER, sq.Sequence("properties_id_seq"), primary_key=True)
    point_id = sq.Column(sq.INTEGER, sq.ForeignKey("geopoints.id"), default=-1)
    prop_type = sq.Column(sq.VARCHAR(20), default="STRING")
    prop_value = sq.Column(sq.TEXT, default="")

    def __init__(self, value: any, _type: PropertyTypes, *args, **kwargs) -> None:
        """
        Initialise the class
        """
        AbstractLogClass.__init__(self, *args, **kwargs)

        self.property_type = _type
        self.property_value = value

    def __repr__(self) -> str:
        text = "<Property(value={})>\n".format(self.prop_value)
        text += AbstractLogClass.__repr__(self)
        return text

    def __str__(self) -> str:
        text = "{} [{}]: {} - ".format(self.property_name, self.property_unit, self.prop_value)
        text += AbstractDBObject.__str__(self)
        return text

    def __convert_value(self, value: str) -> any or None:
        """
        converts the property value from type string to the specified type
        :return: converted property value
        """

        if self.property_type == PropertyTypes.STRING:
            return str(value)
        try:
            if self.property_type == PropertyTypes.INT:
                return int(value)
            if self.property_type == PropertyTypes.FLOAT:
                return float(value)
        except ValueError:
            return None

    def __check_value(self, value: any) -> bool:
        """
        Test, if the value can be converted to the specified format

        :param value: value to test
        :return: True, if it can be converted, else False
        """
        return self.__convert_value(value) is not None

    @property
    def property_type(self) -> PropertyTypes:
        """
        type of the property value
        :return: type of the property value
        :raises ValueError: if type is not available in PropertyTypes
        """
        return PropertyTypes[self.prop_type]

    @property_type.setter
    def property_type(self, value: PropertyTypes) -> None:
        """
        see getter
        """
        if not isinstance(value, PropertyTypes):
            raise ValueError("{} is not in PropertyTypes".format(value))
        self.prop_type = value.name

    @property
    def property_value(self) -> any or None:
        """
        converted value of the property
        :return: converted value of the property
        :raises ValueError: if prop_value cannot be converted to the specified property_type
        """
        return self.__convert_value(self.prop_value)

    @property_value.setter
    def property_value(self, value: any) -> None:
        """
        see getter
        """
        if self.__check_value(str(value)):
            self.prop_value = str(value)
        else:
            raise ValueError("Cannot convert property values [{}] to specified type {}".
                             format(value, self.property_type.name))
