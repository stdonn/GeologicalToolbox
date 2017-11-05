# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.Geometries.Well and WellMarker classes using unittest
"""

import math
import unittest

from Resources.DBHandler import DBHandler
from Resources.Wells import WellMarker, Well
from Resources.Stratigraphy import Stratigraphy
from Resources.constants import float_precision


class TestWellClasses(unittest.TestCase):
    def setUp(self):
        # type: () -> None
        """
        Initialise a temporary database connection for all test cases and fill the database with test data

        :return: None
        """
        # initialise a in-memory sqlite database
        self.handler = DBHandler(connection='sqlite://', debug=False)
        self.session = self.handler.get_session()

        # add test data to the database
        self.wells = [
            {
                'name'      : 'Well_1',
                'short_name': 'W1',
                'comment'   : 'A drilled well',
                'east'      : 1234.56,
                'north'     : 123.45,
                'altitude'  : 10.5,
                'depth'     : 555,
                'marker'    : ((10, 'mu', 4, ''),
                               (15, 'so', 3, ''),
                               (16, 'sm', 2, ''),
                               (17, 'su', 1, ''),
                               (5, 'mm', 5, ''))
            }, {
                'name'      : 'Well_2',
                'short_name': 'W2',
                'comment'   : '',
                'east'      : 1000.23,
                'north'     : 2300.34,
                'altitude'  : 342.23,
                'depth'     : 341,
                'marker'    : ((12, 'mo', 6, ''),
                               (120, 'mm', 5, ''),
                               (300, 'Fault', 0, ''),
                               (320, 'mo', 6, ''))
            }, {
                'name'      : 'Well_3',
                'short_name': 'W3',
                'comment'   : 'A third well',
                'east'      : 3454.34,
                'north'     : 2340.22,
                'altitude'  : 342.20,
                'depth'     : 645.21,
                'marker'    : ((34, 'mu', 4, ''),
                               (234, 'so', 3, ''),
                               (345, 'Fault', 0, ''),
                               (635, 'mu', 4, ''))
            }
        ]

        for well in self.wells:
            new_well = Well(self.session, well['name'], well['east'], well['north'], well['altitude'], well['depth'],
                            well['short_name'], well['comment'])

            for mark in well['marker']:
                new_well.marker.append(WellMarker(mark[0], Stratigraphy.init_stratigraphy(self.session, mark[1],
                                                                                          mark[2], False),
                                                  self.session, mark[3]))

            new_well.save_to_db()
