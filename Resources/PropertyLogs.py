# -*- coding: UTF-8 -*-
"""
This module provides classes for storing property and log information in wells and points (and therefore also in lines).
Properties for points are the same as logs, except there is only one value, not a list of values.
"""

import sqlalchemy as sq
from sqlalchemy.orm import relationship
from typing import List

from Resources.DBHandler import Base, AbstractDBObject
from Resources.Geometries import GeoPoint, Line


class AbstractLogPropClass(AbstractDBObject):
    """
    This class is the base for storing logging information or properties. This class should be treated as abstract, no
    object should be created directly!
    """

    # define table_columns
    prop_name = sq.Column(sq.VARCHAR(50), default='')
    prop_unit = sq.Column(sq.VARCHAR(100), default='')

    def __init__(self, property_name, property_unit, *args, **kwargs):
        # type: (str, str, *str, **str) -> None
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
        if len(name) > 50:
            name = name[:50]
        self.property_name = name

    @property
    def property_unit(self):
        # type: () -> str
        """
        Returns the unit of the property

        :return: Returns the unit of the property
        """
        return str(self.prop_unit)

    @property_unit.setter
    def property_unit(self, unit):
        # type: (str) -> None
        """
        Set a new unit for the property with a maximum length of 100 characters

        :param unit: new unit for the property
        :type unit: str

        :return: Nothing
        """
        unit = str(unit)
        if len(unit) > 50:
            unit = unit[:50]
        self.property_unit = unit


class WellLogValue(Base, AbstractDBObject):
    """
    This class connects the logging values to their related depth
    """
    # define db table name and columns
    __tablename__ = 'logging_association'

    id = sq.Column(sq.INTEGER, sq.Sequence('loggingassoc_id_seq'), primary_key=True)
    log_depth = sq.Column(sq.FLOAT)
    log_value = sq.Column(sq.FLOAT)

    log_id = sq.Column(sq.INTEGER, sq.ForeignKey('well_logs.id'), default=-1)

    def __init__(self, depth, value, *args, **kwargs):
        # type: (float, float, *str, **str)
        """
        Initialise the class

        :param depth: depth of the log value
        :type depth: float

        :param value: log value at the specified depth
        :type depth: float

        :param args: parameters for AbstractDBObject initialisation
        :type args: List()

        :param kwargs: parameters for AbstractDBObject initialisation
        :type kwargs: Dict()

        :returns: Nothing

        :raises ValueError: Raises ValueError if a parameter has wrong type or cannot be converted to required type
        """
        self.depth = depth
        self.value = value

        AbstractDBObject.__init__(self, *args, **kwargs)

    def __repr__(self):
        # type: () -> str
        """
        Returns a text-representation of the association

        :return: Returns a text-representation of the association
        :rtype: str
        """
        text = "<WellLogValue(id='{}', depth='{}', value='{}', log_id='{}')>\n". \
            format(self.id, self.depth, self.value, self.log_id)
        text += "Additional DBObject: {}".format(AbstractDBObject.__repr__(self))
        return text

    def __str__(self):
        # type: () -> str
        """
        Returns a text-representation of the association

        :return: Returns a text-representation of the association
        :rtype: str
        """
        text = "[{}] {}: {} (well_log.id: {})\n" \
            .format(self.id, self.depth, self.value, self.log_id)
        text += "DBObject: {}".format(AbstractDBObject.__str__(self))
        return text

    @property
    def depth(self):
        # type: () -> float
        """
        Returns the depth of the log value

        :return: Returns the depth of the log value
        """
        return float(self.log_depth)

    @depth.setter
    def depth(self, log_depth):
        # type: (float) -> None
        """
        Sets a new depth for the log value

        :param log_depth: new depth
        :type log_depth: float

        :return: Nothing
        :raises ValueError: Raises ValueError if log_depth is not type float or cannot be converted to it
        """
        self.log_depth = float(log_depth)

    @property
    def value(self):
        # type: () -> float
        """
        Returns the value of the log depth

        :return: Returns the value of the log depth
        """
        return float(self.log_value)

    @value.setter
    def value(self, log_value):
        # type: (float) -> None
        """
        Sets a new value for the log at the current depth

        :param log_value: new value
        :type log_value: float

        :return: Nothing
        :raises ValueError: Raises ValueError if log_value is not type float or cannot be converted to it
        """
        self.log_value = float(log_value)


class WellLogging(Base, AbstractLogPropClass):
    """
    This class represents logging information for wells
    """
    # define db table name and columns
    __tablename__ = 'well_logs'

    id = sq.Column(sq.INTEGER, sq.Sequence('well_logs_id_seq'), primary_key=True)
    well_id = sq.Column(sq.INTEGER, sq.ForeignKey('wells.id'), default=-1)
    # define markers relationship
    log_values = relationship("WellLogValue", order_by=WellLogValue.log_depth,
                              backref="well_log", primaryjoin='WellLogging.id==WellLogValue.log_id',
                              cascade="all, delete, delete-orphan")

    def __init__(self, *args, **kwargs):
        # type: (*str, **str) -> None
        """
        Initialise the class

        :param args: parameters for AbstractLogPropClass initialisation
        :type args: List()

        :param kwargs: parameters for AbstractLogPropClass initialisation
        :type kwargs: Dict()
        """
        AbstractLogPropClass.__init__(self, *args, **kwargs)

    def __repr__(self):
        # type: () -> str
        """
        Returns a text-representation of the log

        :return: Returns a text-representation of the log
        :rtype: str
        """
        text = "<WellLog(id='{}', well_id='{}', log values='{}')>\n". \
            format(self.id, self.well.id, str(self.log_values))
        text += "Additional DBObject: {}".format(AbstractDBObject.__repr__(self))
        return text

    def __str__(self):
        # type: () -> str
        """
        Returns a text-representation of the association

        :return: Returns a text-representation of the association
        :rtype: str
        """
        text = "[{}] Well ({}: {})\n" \
            .format(self.id, self.well.id, self.well.name)
        text += "DBObject: {}".format(AbstractDBObject.__str__(self))
        for assoc in self.log_values:
            text += "{}".format(str(assoc))
        return text

    def insert_log_value(self, log_value):
        # type: (WellLogValue) -> None
        """
        Insert a new log value in the log
        ATTENTION: If you insert a log value, the log will be automatically stored in the database!

        :param log_value: WellLogValue to be inserted
        :type log_value: WellLogValue

        :return: Nothing

        :raises TypeError: Raises TypeError if marker is not an instance of WellLogValue
        :raises ValueError: Raises ValueError if the depth of the marker is larger than the drilled depth of the well
        """
        if isinstance(log_value, WellLogValue):
            raise TypeError('log_value {} is not of type WellLogValue!'.format(str(log_value)))
        if log_value.depth > self.well.depth:
            raise ValueError('Value depth ({}) is larger than final well depth ({})!'.format(log_value.depth,
                                                                                             self.well.depth))
        self.log_values.append(log_value)

        # new sorting to ensure correct order without storage and reloading from the database
        self.log_values.sort(key=lambda x: x.depth)

    def insert_multiple_marker(self, log_values):
        # type: (List[WellLogValue]) -> None
        """
        Insert the multiple log values in the log
        ATTENTION: If you insert value, the log will be automatically stored in the database!

        :param log_values: List of marker to be inserted
        :type log_values: List[WellLogValue]

        :return: Nothing

        :raises TypeError: Raises TypeError if one of the marker is not an instance of WellLogValue
        :raises ValueError: Raises ValueError if the depth of a value is larger than the drilled depth of the well
        """
        for value in log_values:
            if not isinstance(value, WellLogValue):
                raise TypeError(
                        'At least on value is not of type WellLogValue ({}: {})!'.format(str(value), str(type(value))))
            if value.depth > self.well.depth:
                raise ValueError('Value depth ({}) is larger than final well depth ({})!'.
                                 format(value.depth, self.well.depth))

        self.log_values += log_values

        # new sorting to ensure correct order without storage and reloading from the database
        self.log_values.sort(key=lambda x: x.depth)

    def get_value_by_depth(self, depth):
        # type: (float) -> WellLogValue or None
        """
        Returns the value at depth 'depth'

        :param depth: depth of the requested marker
        :type depth: float

        :return: Returns the value at depth 'depth'
        :rtype: WellLogValue

        :raises ValueError: Raises ValueError if no marker was found for the committed depth or depth is
                            not compatible to float
        """
        depth = float(depth)
        for value in self.log_values:
            if value.depth == depth:
                return value
        raise ValueError('No value found at depth {}'.format(depth))

    def delete_value(self, value):
        # type: (WellLogValue) -> None
        """
        Deletes the value from the well log

        :param value: WellLogValue object which should be deleted
        :type value: WellLogValue

        :return: Nothing

        :raises TypeError: Raises TypeError if value is not of type WellLogValue
        :raises ValueError: Raises ValueError the value is not part of the well log
        """
        if not isinstance(value, WellLogValue):
            raise TypeError('marker {} is not an instance of WellLogValue!'.format(str(value)))

        try:
            self.log_values.remove(value)
        except ValueError as e:
            raise ValueError(str(e) + '\nWellLogValue with ID ' + str(value.id) + ' not found in value list!')
