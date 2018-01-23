# -*- coding: UTF-8 -*-
"""
This module provides a class for storing properties of points (and therefore also for lines). Properties for points are
the same as logs, except there is only one value, not a list of values. They are both derived from the AbstractLogClass.

.. todo:: - reformat docstrings, espacially of setter and getter functions
          - check exception types
"""

import sqlalchemy as sq

from GeologicalToolbox.AbstractLog import AbstractLogClass
from GeologicalToolbox.DBHandler import Base, AbstractDBObject


class Property(Base, AbstractLogClass):
    """
    This class represents logging information for wells
    """
    # define db table name and columns
    __tablename__ = 'properties'

    id = sq.Column(sq.INTEGER, sq.Sequence('properties_id_seq'), primary_key=True)
    point_id = sq.Column(sq.INTEGER, sq.ForeignKey('geopoints.id'), default=-1)
    prop_value = sq.Column(sq.FLOAT, default=0)

    def __init__(self, *args, **kwargs):
        # type: (*object, **object) -> None
        """
        Initialise the class

        :param args: parameters for AbstractLogClass initialisation
        :type args: List()

        :param kwargs: parameters for AbstractLogClass initialisation
        :type kwargs: Dict()
        """
        AbstractLogClass.__init__(self, *args, **kwargs)

    def __repr__(self):
        text = "<Property(value={})>\n".format(self.value)
        text += AbstractLogClass.__repr__(self)
        return text

    def __str__(self):
        text = "{} [{}]: {} - ".format(self.property_name, self.property_unit, self.value)
        text += AbstractDBObject.__str__(self)
        return text

    @property
    def value(self):
        # type: () -> float
        """
        Returns the value of the property

        :return: Returns the value of the property
        """
        return float(self.prop_value)

    @value.setter
    def value(self, prop_value):
        # type: (float) -> None
        """
        Sets a new value for the property

        :param prop_value: new value
        :type prop_value: float

        :return: Nothing
        :raises ValueError: Raises ValueError if prop_value is not type float or cannot be converted to it
        """
        self.prop_value = float(prop_value)
