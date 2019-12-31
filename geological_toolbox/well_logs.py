# -*- coding: UTF-8 -*-
"""
This module provides a class for storing logging information of wells. The logging class is derived from the
AbstractLogClass.
"""

import sqlalchemy as sq
from sqlalchemy.orm import relationship
from typing import List

from geological_toolbox.abstract_log import AbstractLogClass
from geological_toolbox.db_handler import Base, AbstractDBObject


class WellLogValue(Base, AbstractDBObject):
    """
    This class connects the logging values to their related depth

    :param depth: depth of the log value
    :param value: log value at the specified depth
    :param args: parameters for AbstractDBObject initialisation
    :param kwargs: parameters for AbstractDBObject initialisation
    :return: Nothing
    :raises ValueError: if a parameter has wrong type or cannot be converted to required
    """
    # define db table stratigraphic_name and columns
    __tablename__ = "logging_association"

    id = sq.Column(sq.INTEGER, sq.Sequence("logging_association_id_seq"), primary_key=True)
    log_depth = sq.Column(sq.FLOAT)
    log_value = sq.Column(sq.FLOAT)

    log_id = sq.Column(sq.INTEGER, sq.ForeignKey("well_logs.id"), default=-1)
    sq.Index("welllogdepth_index", log_depth)

    def __init__(self, depth: float, value: float, *args, **kwargs) -> None:
        """
        Initialise the class
        """
        self.depth = depth
        self.value = value

        AbstractDBObject.__init__(self, *args, **kwargs)

    def __repr__(self) -> str:
        text = "<WellLogValue(id='{}', depth='{}', value='{}', log_id='{}'),\n". \
            format(self.id, self.depth, self.value, self.log_id)
        text += "Additional DBObject: {}>".format(AbstractDBObject.__repr__(self))
        return text

    def __str__(self) -> str:
        text = "[{}] {}: {} (well_log.id: {})\n" \
            .format(self.id, self.depth, self.value, self.log_id)
        text += "DBObject: {}".format(AbstractDBObject.__str__(self))
        return text

    @property
    def depth(self) -> float:
        """
        depth of the log value

        :raises ValueError: if log_depth is not type float or cannot be converted to it
        """
        return float(self.log_depth)

    @depth.setter
    def depth(self, log_depth: float) -> None:
        """
        see getter
        """
        self.log_depth = float(log_depth)

    @property
    def value(self) -> float:
        """
        log value

        :raises ValueError: Raises ValueError if log_value is not type float or cannot be converted to it
        """
        return float(self.log_value)

    @value.setter
    def value(self, log_value: float) -> None:
        """
        see getter
        """
        self.log_value = float(log_value)


class WellLog(Base, AbstractLogClass):
    """
    represents logging information for wells
    """
    # define db table well_logs and columns
    __tablename__ = "well_logs"

    id = sq.Column(sq.INTEGER, sq.Sequence("well_logs_id_seq"), primary_key=True)
    well_id = sq.Column(sq.INTEGER, sq.ForeignKey("wells.id"), default=-1)
    # define markers relationship
    log_values = relationship("WellLogValue", order_by=WellLogValue.log_depth,
                              backref="well_log", primaryjoin="WellLog.id==WellLogValue.log_id",
                              cascade="all, delete, delete-orphan")

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialise the class
        """
        AbstractLogClass.__init__(self, *args, **kwargs)

    def __repr__(self) -> str:
        text = "<WellLog(id='{}', well_id='{}', log values='{}')>\n". \
            format(self.id, self.well.id, str(self.log_values))
        text += "Additional DBObject: {}".format(AbstractDBObject.__repr__(self))
        return text

    def __str__(self) -> str:
        text = "[{}] Well ({}: {})\n" \
            .format(self.id, self.well.id, self.well.name)
        text += "DBObject: {}".format(AbstractDBObject.__str__(self))
        for assoc in self.log_values:
            text += "{}".format(str(assoc))
        return text

    def insert_log_value(self, log_value: WellLogValue) -> None:
        """
        Insert a new log value in the log
        ATTENTION: If you insert a log value, the log will be automatically stored in the database!

        :param log_value: WellLogValue to be inserted
        :return: Nothing
        :raises TypeError: if marker is not an instance of WellLogValue
        :raises ValueError: if the depth of the marker is larger than the drilled depth of the well or < 0
        """
        if not isinstance(log_value, WellLogValue):
            raise TypeError("log_value {} is not of type WellLogValue!".format(str(log_value)))
        if log_value.depth < 0:
            raise ValueError("Value depth ({}) < 0!".format(log_value.depth))
        if (not (self.well is None)) and (log_value.depth > self.well.depth):
            raise ValueError("Value depth ({}) is larger than final well depth ({})!".format(log_value.depth,
                                                                                             self.well.depth))
        self.log_values.append(log_value)

        # new sorting to ensure correct order without storage and reloading from the database
        self.log_values.sort(key=lambda x: x.depth)

    def insert_multiple_log_values(self, log_values: List[WellLogValue]) -> None:
        """
        Insert the multiple log values in the log
        ATTENTION: If you insert values, the log will be automatically stored in the database!

        :param log_values: List of marker to be inserted
        :return: Nothing
        :raises TypeError: if one of the marker is not an instance of WellLogValue
        :raises ValueError: if the depth of a value is larger than the drilled depth of the well or < 0
        """
        for value in log_values:
            if not isinstance(value, WellLogValue):
                raise TypeError(
                    "At least on value is not of type WellLogValue ({}: {})!".format(str(value), str(type(value))))
            if value.depth < 0:
                raise ValueError("Value depth ({}) < 0!".format(value.depth))
            if (not (self.well is None)) and (value.depth > self.well.depth):
                raise ValueError("Value depth ({}) is larger than final well depth ({})!".
                                 format(value.depth, self.well.depth))

        self.log_values += log_values

        # new sorting to ensure correct order without storage and reloading from the database
        self.log_values.sort(key=lambda x: x.depth)

    def get_value_by_depth(self, depth: float) -> WellLogValue or None:
        """
        Returns the value at depth "depth"

        :param depth: depth of the requested marker
        :return: Returns the value at depth "depth"
        :raises ValueError: if no marker was found for the committed depth or depth is not compatible to float
        """
        depth = float(depth)
        for value in self.log_values:
            if value.depth == depth:
                return value
        raise ValueError("No value found at depth {}".format(depth))

    def delete_value(self, value: WellLogValue) -> None:
        """
        Deletes the value from the well log

        :param value: WellLogValue object which should be deleted
        :return: Nothing
        :raises TypeError: if value is not of type WellLogValue
        :raises ValueError: if the value is not part of the well log
        """
        if not isinstance(value, WellLogValue):
            raise TypeError("marker {} is not an instance of WellLogValue!".format(str(value)))

        try:
            self.log_values.remove(value)
        except ValueError as e:
            raise ValueError("{}\nWellLogValue with ID {} not found in value list!".format(str(e), value.id))
