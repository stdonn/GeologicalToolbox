# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.Geometries.Well and WellMarker classes using unittest
"""

import math
import unittest

from GeologicalToolbox.Exceptions import WellMarkerDepthException
from GeologicalToolbox.DBHandler import DBHandler
from GeologicalToolbox.Stratigraphy import StratigraphicObject
from GeologicalToolbox.WellLogs import WellLog, WellLogValue
from GeologicalToolbox.Wells import WellMarker, Well
from GeologicalToolbox.Constants import float_precision


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
                                                  StratigraphicObject.init_stratigraphy(self.session, mark[1], mark[2], False),
                                                  self.session, well['name'], mark[3]))
                new_well.marker[-1].save_to_db()

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
        self.assertEqual(result[1].well_name, 'Well_2')
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
        self.assertEqual(wells[0].well_name, 'Well_1')
        self.assertEqual(wells[1].well_name, 'Well_2')
        self.assertEqual(wells[2].well_name, 'Well_3')
        self.assertEqual(len(wells[1].marker), 4)
        self.assertTrue(wells[1].marker[0].horizon == wells[1].marker[3].horizon)
        del wells

        # Part 2: load well by name
        well = Well.load_by_wellname_from_db('Well_2', self.session)
        self.assertEqual(well.well_name, 'Well_2')
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
        self.assertEqual(wells[0].well_name, 'Well_1')
        self.assertEqual(wells[1].well_name, 'Well_2')
        self.assertEqual(len(wells[0].marker), 5)
        self.assertEqual(len(wells[1].marker), 4)
        del wells

        # Part 4: load wells with minimal depth
        wells = Well.load_deeper_than_value_from_db(self.session, 395.23)
        self.assertEqual(len(wells), 2)
        self.assertEqual(wells[0].well_name, 'Well_1')
        self.assertEqual(wells[1].well_name, 'Well_3')
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
        marker_1 = WellMarker(301.43, StratigraphicObject.init_stratigraphy(self.session, "ku"), self.session, 'Comment 1')
        marker_2 = WellMarker(351.65, StratigraphicObject.init_stratigraphy(self.session, "mo"), self.session)
        marker_3 = WellMarker(934.23, StratigraphicObject.init_stratigraphy(self.session, "mm"), self.session, 'Comment 3')

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

    def test_get_marker_by_depth(self):
        # type: () -> None
        """
        Test the Well.get_marker_by_depth function

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        well = Well.load_by_wellname_from_db('Well_1', self.session)
        self.assertEqual(well.get_marker_by_depth(16).horizon.name, 'sm')
        self.assertRaises(ValueError, well.get_marker_by_depth, 100)

    def test_delete_marker(self):
        # type: () -> None
        """
        Test the Well.get_marker_by_depth function

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        well = Well.load_by_wellname_from_db('Well_1', self.session)
        marker = well.get_marker_by_depth(16)
        self.assertEqual(marker.horizon.name, 'sm')
        self.assertRaises(ValueError, well.get_marker_by_depth, 100)
        well.delete_marker(marker)
        self.assertEqual(len(well.marker), 4)
        well.save_to_db()
        del well

        well = Well.load_by_wellname_from_db('Well_1', self.session)
        self.assertEqual(len(well.marker), 4)

        new_marker = WellMarker(23423, StratigraphicObject.init_stratigraphy(self.session, 'so'), self.session, 'Nothing')
        self.assertRaises(ValueError, well.delete_marker, new_marker)
        self.assertRaises(TypeError, well.delete_marker, 'test')

    def test_setter_and_getter(self):
        # type: () -> None
        """
        Test setter and getter functionality

        :return: Nothing
        :raises AssertionError: Raises Assertion Error if a test fails
        """
        # first part: test setter
        wells = Well.load_all_from_db(self.session)
        test_string = "abcdefghijklmnopqrstuvwxyz1234567890"
        wells[0].comment = "new comment set"
        wells[1].comment = 4 * test_string
        wells[0].easting = '-344.3'
        wells[1].easting = -1234.34
        # self.assertRaises(ValueError, setattr, wells[2], 'easting', 'test')
        # python >= 2.7 => not included in all ArcGIS versions...
        with(self.assertRaises(ValueError)):  # python <= 2.6
            wells[2].easting = 'test'
        wells[0].northing = -234.56
        wells[1].northing = '-2345.356'
        with(self.assertRaises(ValueError)):
            wells[2].northing = 'test'
        wells[0].altitude = -343.67
        wells[1].altitude = '-235.34'
        with(self.assertRaises(ValueError)):
            wells[2].altitude = 'test'
        wells[0].depth = 235.65
        wells[1].depth = "3456.14"
        with(self.assertRaises(ValueError)):
            wells[2].depth = 'test'
        with(self.assertRaises(ValueError)):
            wells[2].depth = -123.43
        with(self.assertRaises(WellMarkerDepthException)):
            wells[2].depth = 500
        wells[0].well_name = "new Well Name"
        wells[1].well_name = 4 * test_string
        wells[0].short_name = "NWN"
        wells[1].short_name = test_string

        # changes are stored automatically to the database through SQLAlchemy

        del wells

        # second part: test getters
        wells = Well.load_all_from_db(self.session)
        self.assertEqual(wells[0].comment, "new comment set")
        self.assertEqual(len(wells[1].comment), 100)
        self.assertEqual(wells[0].easting, -344.3)
        self.assertEqual(wells[1].easting, -1234.34)
        self.assertEqual(wells[2].easting, 3454.34)
        self.assertEqual(wells[0].northing, -234.56)
        self.assertEqual(wells[1].northing, -2345.356)
        self.assertEqual(wells[2].northing, 2340.22)
        self.assertEqual(wells[0].altitude, -343.67)
        self.assertEqual(wells[1].altitude, -235.34)
        self.assertEqual(wells[2].altitude, 342.2)
        self.assertEqual(wells[0].depth, 235.65)
        self.assertEqual(wells[1].depth, 3456.14)
        self.assertEqual(wells[2].depth, 645.21)
        self.assertEqual(wells[0].well_name, 'new Well Name')
        self.assertEqual(len(wells[1].well_name), 100)
        self.assertEqual(wells[0].short_name, 'NWN')
        self.assertEqual(len(wells[1].short_name), 20)

        # setter and getter for session
        wells[2].session = wells[1].session

    def test_log_handling(self):
        # type: () -> None
        """
        Tests the log handling functionality

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        log_values = (
            (
                (10, 4, '', ''),
                (15, '45.4', 'name 1', 'Comment 1'),
                (16, 34.3, '', ''),
                (17, 234, '', 'Comment 2'),
                (5, '34.4', '', 'Comment 3')
            ),
            (
                (34.3, 4, '', ''),
                (13, 234, '', 'Comment 2'),
                (34, '34.4', '', 'Comment 3')
            )
        )

        well = Well.load_by_wellname_from_db('Well_2', self.session)
        for i in range(len(log_values)):
            log = WellLog('log {}'.format(i), 'unit name', self.session, '', '')
            log.save_to_db()
            well.add_log(log)

            for value in log_values[i]:
                log.insert_log_value(WellLogValue(value[0], value[1], self.session, value[2], value[3]))
            del log

        del well

        well = Well.load_by_wellname_from_db('Well_2', self.session)
        self.assertEqual(2, len(well.logs))
        self.assertEqual(5, len(well.logs[0].log_values))
        self.assertEqual('log 0', well.logs[0].property_name)
        self.assertEqual(3, len(well.logs[1].log_values))
        self.assertEqual('log 1', well.logs[1].property_name)

        well.delete_log(well.logs[1])

        del well

        well = Well.load_by_wellname_from_db('Well_2', self.session)
        self.assertEqual(1, len(well.logs))
        self.assertEqual(5, len(well.logs[0].log_values))
        self.assertEqual('log 0', well.logs[0].property_name)

        logs = WellLog.load_all_from_db(self.session)
        self.assertEqual(1, len(logs))

    def tearDown(self):
        # type: () -> None
        """
        Empty function, nothing to shutdown after the testing process

        :return: Nothing
        """
        pass


class TestWellMarkerClass(unittest.TestCase):
    """
    a unittest for WellMarker class
    """

    def setUp(self):
        # type: () -> None
        """
        Initialise a temporary database connection for all test cases and fill the database with test data

        :return: None
        """
        # initialise a in-memory sqlite database
        self.handler = DBHandler(connection='sqlite://', echo=False)
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
                new_well.marker.append(WellMarker(mark[0], StratigraphicObject.init_stratigraphy(self.session, mark[1],
                                                                                                 mark[2], False),
                                                  self.session, well['name'], mark[3]))
                new_well.marker[-1].save_to_db()

    def test_WellMarker_init(self):
        # type: () -> None
        """
        Test the initialisation of the database

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        marker = self.session.query(WellMarker).all()
        self.assertEqual(len(marker), 13)
        self.assertEqual(marker[3].horizon.name, 'su')
        self.assertEqual(marker[4].horizon.name, 'mm')

    def test_WellMarker_setter_and_getter(self):
        # type: () -> None
        """
        Test setter and getter functionality

        :return: Nothing
        :raises AssertionError: Raises Assertion Error if a test fails
        """
        marker = WellMarker.load_all_from_db(self.session)
        self.assertEqual(len(marker), 13)
        test_string = "abcdefghijklmnopqrstuvwxyz1234567890"

        # first part: test setter functionality
        marker[0].comment = 'This is a new comment'
        marker[1].comment = 4 * test_string
        marker[2].depth = 123.43
        marker[3].depth = '2345.54'
        with (self.assertRaises(ValueError)):
            marker[4].depth = 'Test'
        marker[4].horizon = StratigraphicObject.init_stratigraphy(self.session, 'z', 50, False)
        with (self.assertRaises(TypeError)):
            marker[5].horizon = 'test'

        # second part: getter functionality
        marker = WellMarker.load_all_from_db(self.session)
        self.assertEqual(marker[0].comment, 'This is a new comment')
        self.assertEqual(len(marker[1].comment), 100)
        self.assertEqual(marker[3].comment, 'Comment 2')
        self.assertEqual(marker[2].depth, 123.43)
        self.assertEqual(marker[1].depth, 15)
        self.assertEqual(marker[4].horizon.name, 'z')
        self.assertEqual(marker[5].horizon.name, 'mo')

    def test_WellMarker_to_GeoPoint(self):
        # type: () -> None
        """
        Test WellMarker.to_GeoPoint functionality

        :return: Nothing
        :raises AssertionError: Raises Assertion Error if a test fails
        """
        marker = WellMarker.load_all_from_db(self.session)[0]
        point = marker.to_geopoint()
        self.assertEqual(point.easting, 1234.56)
        self.assertEqual(point.northing, 123.45)
        self.assertEqual(point.altitude, 0.5)
        self.assertEqual(point.name, 'Well_1')
        self.assertEqual(point.horizon.name, 'mu')

    def tearDown(self):
        # type: () -> None
        """
        Empty function, nothing to shutdown after the testing process

        :return: Nothing
        """
        pass


if __name__ == '__main__':
    unittest.main()
