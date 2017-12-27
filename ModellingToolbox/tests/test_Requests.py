# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.Geometries.Well and WellMarker classes using unittest
"""

import unittest

from Resources.DBHandler import DBHandler
from Resources.Requests import Requests
from Resources.Stratigraphy import StratigraphicObject
from Resources.Wells import WellMarker, Well


class TestWellClass(unittest.TestCase):
    """
    a unittest for Well class
    """

    def setUp(self):
        # type: () -> None
        """
        Initialise a temporary database connection for all test cases and fill the database with test data

        :return: None
        """
        # initialise a in-memory sqlite database
        # self.handler = DBHandler(connection='sqlite:///D:\\data.db', echo=False)
        self.handler = DBHandler(connection='sqlite://', echo=False)
        # self.handler = DBHandler(connection='mysql://stdonn:YWBokMUVYHKoSQ1S@localhost:3306/stdonn')
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
                               (15, 'so', 3, 'Comment 1'),
                               (16, 'sm', 2, ''),
                               (17, 'su', 1, 'Comment 2'),
                               (5, 'mm', 5, 'Comment 3'))
            }, {
                'name'      : 'Well_2',
                'short_name': 'W2',
                'comment'   : '',
                'east'      : 1000.23,
                'north'     : 2300.34,
                'altitude'  : 342.23,
                'depth'     : 341,
                'marker'    : ((12, 'mo', 6, ''),
                               (120, 'mm', 5, 'Comment 1'),
                               (300, 'Fault', 0, 'Comment 2'),
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
                               (234, 'so', 3, 'Comment 1'),
                               (345, 'Fault', 0, 'Comment 2'),
                               (635, 'mu', 4, 'Comment 3'))
            }
        ]

        for well in self.wells:
            new_well = Well(well['name'], well['short_name'], well['depth'], 'spatial_reference_unknown', well['east'],
                            well['north'], well['altitude'], self.session, 'well_set', well['comment'])
            new_well.save_to_db()

            for mark in well['marker']:
                new_well.marker.append(WellMarker(mark[0],
                                                  StratigraphicObject.init_stratigraphy(self.session, mark[1], mark[2],
                                                                                        False),
                                                  self.session, well['name'], mark[3]))
                new_well.marker[-1].save_to_db()

    def test_well_markers_to_thickness(self):
        # type: () -> None
        """
        Tests the Requests.well_markers_to_thickness(...) function

        :return: Nothing
        :raises AssertionError: if a test fails
        """
        result = Requests.well_markers_to_thickness(self.session, 'mu', 'so', summarise_multiple=True)
        for point in result:
            print("")
            print(str(point))


if __name__ == '__main__':
    unittest.main()
