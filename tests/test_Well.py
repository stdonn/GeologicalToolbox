# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.Geometries.Well and WellMarker classes using unittest
"""

import math
import unittest

from Resources.DBHandler import DBHandler
from Resources.Stratigraphy import Stratigraphy
from Resources.Wells import WellMarker, Well
from Resources.constants import float_precision


class TestWellClass(unittest.TestCase):
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
            new_well = Well(self.session, well['name'], well['east'], well['north'], well['altitude'], well['depth'],
                            well['short_name'], well['comment'])

            for mark in well['marker']:
                new_well.marker.append(WellMarker(mark[0], Stratigraphy.init_stratigraphy(self.session, mark[1],
                                                                                          mark[2], False),
                                                  self.session, mark[3]))
            new_well.save_to_db()

    def test_init(self):
        # type: () -> None
        """
        Test the initialisation of the database

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        result = self.session.query(Well).all()
        self.assertEqual(len(result), 3, "Wrong number of drill holes ({}). Should be {}".
                         format(len(result), len(self.wells)))
        self.assertEqual(result[1].name, 'Well_2')
        self.assertEqual(result[1].short_name, 'W2')
        self.assertEqual(result[2].comment, 'A third well')
        self.assertTrue(math.fabs(float(result[0].easting) - 1234.56) < float_precision)
        self.assertTrue(math.fabs(float(result[1].northing) - 2300.34) < float_precision)
        self.assertTrue(math.fabs(float(result[0].altitude) - 10.5) < float_precision)
        self.assertTrue(math.fabs(float(result[2].depth) - 645.21) < float_precision)
        self.assertEqual(len(result[1].marker), 4)
        self.assertEqual(result[0].marker[2].horizon.name, 'so')
        self.assertEqual(result[2].marker[2].horizon.name, 'Fault')
        self.assertEqual(result[2].marker[2].horizon.age, 0)
        self.assertEqual(result[2].marker[2].comment, 'Comment 2')
        self.assertEqual(result[0].marker[0].horizon.name, 'mm')
        self.assertEqual(result[0].marker[1].horizon.name, 'mu')
        self.assertEqual(result[0].marker[2].horizon.name, 'so')
        self.assertEqual(result[0].marker[3].horizon.name, 'sm')
        self.assertEqual(result[0].marker[4].horizon.name, 'su')

    def test_loading(self):
        # type: () -> None
        """
        Test the different types of loading of lines from the db.
        Part 1: load all wells from the database
        Part 2: load well by name
        Part 3: load wells in given extent
        Part 4: load wells with minimal depth

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        # Part 1: load all wells from the database
        wells = Well.load_all_from_db(self.session)
        self.assertEqual(len(wells), 3)
        self.assertEqual(wells[0].name, 'Well_1')
        self.assertEqual(wells[1].name, 'Well_2')
        self.assertEqual(wells[2].name, 'Well_3')
        self.assertEqual(len(wells[1].marker), 4)
        self.assertTrue(wells[1].marker[0].horizon == wells[1].marker[3].horizon)
        del wells

        # Part 2: load well by name
        well = Well.load_by_name_from_db('Well_2', self.session)
        self.assertEqual(well.name, 'Well_2')
        self.assertEqual(well.short_name, 'W2')
        self.assertEqual(well.depth, 341)
        self.assertEqual(len(well.marker), 4)
        self.assertEqual(well.marker[1].horizon.name, 'mm')
        self.assertEqual(well.marker[1].depth, 120)
        del well

        # Part 3: load wells in given extent
        # extent x: 500 - 1,300
        # extent y: 0 - 2,400
        # result: 'Well_1' and 'Well_2'
        wells = Well.load_in_extent_from_db(self.session, 500, 1300, 0, 2400)
        self.assertEqual(len(wells), 2)
        self.assertEqual(wells[0].name, 'Well_1')
        self.assertEqual(wells[1].name, 'Well_2')
        self.assertEqual(len(wells[0].marker), 5)
        self.assertEqual(len(wells[1].marker), 4)
        del wells

        # Part 4: load wells with minimal depth
        wells = Well.load_deeper_than_value_from_db(self.session, 395.23)
        self.assertEqual(len(wells), 2)
        self.assertEqual(wells[0].name, 'Well_1')
        self.assertEqual(wells[1].name, 'Well_3')
        self.assertTrue(wells[0].depth >= 395.23)
        self.assertTrue(wells[1].depth >= 395.23)
        del wells

    def test_insertion(self):
        # type: () -> None
        """
        Test the insert functions of class Well

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        wells = Well.load_all_from_db(self.session)
        marker_1 = WellMarker(301.43, Stratigraphy.init_stratigraphy(self.session, "ku"), self.session, 'Comment 1')
        marker_2 = WellMarker(351.65, Stratigraphy.init_stratigraphy(self.session, "mo"), self.session)
        marker_3 = WellMarker(934.23, Stratigraphy.init_stratigraphy(self.session, "mm"), self.session, 'Comment 3')

        wells[0].insert_marker(marker_1)
        self.assertEqual(len(wells[0].marker), 6)
        self.assertEqual(wells[0].marker[5], marker_1)
        self.assertRaises(ValueError, wells[1].insert_marker, marker_3)

        wells[2].insert_multiple_marker([marker_1, marker_2])
        self.assertEqual(len(wells[2].marker), 6)
        self.assertEqual(wells[2].marker[2], marker_1)
        self.assertEqual(wells[2].marker[4], marker_2)
        del wells

        wells = Well.load_all_from_db(self.session)
        self.assertEqual(wells[2].marker[2], marker_1)
        self.assertEqual(wells[2].marker[4], marker_2)
        del wells

        wells = Well.load_all_from_db(self.session)
        self.assertRaises(ValueError, wells[1].insert_multiple_marker, [marker_1, marker_2, marker_3])

    def tearDown(self):
        # type: () -> None
        """
        Empty function, nothing to shutdown after the testing process

        :return: Nothing
        """
        pass


if __name__ == '__main__':
    unittest.main()
