# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.PropertyLogs-Module classes using unittests
"""

import unittest

from GeologicalToolbox.DBHandler import DBHandler
from GeologicalToolbox.Geometries import GeoPoint
from GeologicalToolbox.Properties import Property
from GeologicalToolbox.Stratigraphy import StratigraphicObject
from GeologicalToolbox.WellLogs import WellLog, WellLogValue
from GeologicalToolbox.Wells import Well


class TestWellLogValueClass(unittest.TestCase):
    """
    a unittest for WellLogValue class
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
        self.log_values = [
            {
                'depth'  : 200,
                'value'  : 123,
                'name'   : 'log name',
                'comment': 'unknown'
            }, {
                'depth'  : 200.324,
                'value'  : 12.5455,
                'name'   : 'log name 2',
                'comment': 'unknown'
            }, {
                'depth'  : '2345.54',
                'value'  : '641.54',
                'name'   : '',
                'comment': ''
            }
        ]

        for value in self.log_values:
            well_log_value = WellLogValue(value['depth'], value['value'], self.session, value['name'], value['comment'])
            well_log_value.save_to_db()

    def test_WellLogValue_init(self):
        # type: () -> None
        """
        Test the initialisation of the database

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        log_values = self.session.query(WellLogValue).all()
        self.assertEqual(len(log_values), 3)
        self.assertEqual(log_values[0].depth, 200)
        self.assertEqual(log_values[1].value, 12.5455)
        self.assertEqual(log_values[1].name, 'log name 2')
        self.assertEqual(log_values[2].depth, 2345.54)
        self.assertEqual(log_values[2].value, 641.54)
        self.assertEqual(log_values[0].comment, 'unknown')

    def test_setter_and_getter(self):
        # type: () -> None
        """
        Tests the setter and getter functionality of the WellLogValue class

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """

        log_values = WellLogValue.load_all_from_db(self.session)
        self.assertEqual(len(log_values), 3)

        self.assertEqual(log_values[0].depth, 200)
        self.assertEqual(log_values[1].value, 12.5455)

        log_values[2].depth = 123.4
        log_values[0].depth = "54356.45"
        with (self.assertRaises(ValueError)):
            log_values[1].depth = "string"

        log_values[0].value = 4345.4
        log_values[1].value = "3245.4"
        with (self.assertRaises(ValueError)):
            log_values[2].value = "string"

        del log_values

        log_values = WellLogValue.load_all_from_db(self.session)

        self.assertEqual(log_values[0].depth, 54356.45)
        self.assertEqual(log_values[1].depth, 200.324)
        self.assertEqual(log_values[2].depth, 123.4)
        self.assertEqual(log_values[0].value, 4345.4)
        self.assertEqual(log_values[1].value, 3245.4)
        self.assertEqual(log_values[2].value, 641.54)

    def tearDown(self):
        # type: () -> None
        """
        Empty function, nothing to shutdown after the testing process

        :return: Nothing
        """
        pass


class TestWellLogClass(unittest.TestCase):
    """
    a unittest for WellLog class
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
        self.well = {
            'name'      : 'Well_1',
            'short_name': 'W1',
            'reference' : 'none',
            'east'      : 1234.56,
            'north'     : 123.45,
            'altitude'  : 10.5,
            'depth'     : 555,
            'log_values': ((10, 4, '', ''),
                           (15, '45.4', 'name 1', 'Comment 1'),
                           (16, 34.3, '', ''),
                           (17, 234, '', 'Comment 2'),
                           (5, '34.4', '', 'Comment 3'))
        }

        well = Well(self.well['name'], self.well['short_name'], self.well['depth'], self.well['reference'],
                    self.well['east'], self.well['north'], self.well['altitude'], self.session, '', '')
        well.save_to_db()

        logging = WellLog('logging', 'unit name', self.session, '', '')
        logging.save_to_db()

        well.add_log(logging)

        for value in self.well['log_values']:
            logging.insert_log_value(WellLogValue(value[0], value[1], self.session, value[2], value[3]))

    def test_WellLogValue_init(self):
        # type: () -> None
        """
        Test the initialisation of the database

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        logging = self.session.query(WellLog).one()
        self.assertEqual(len(logging.log_values), 5)
        self.assertEqual(logging.log_values[0].depth, 5)
        self.assertEqual(logging.log_values[1].value, 4)
        self.assertEqual(logging.log_values[2].name, 'name 1')
        self.assertEqual(logging.log_values[2].depth, 15)
        self.assertEqual(logging.log_values[2].value, 45.4)
        self.assertEqual(logging.log_values[4].comment, 'Comment 2')

    def test_setter_and_getter(self):
        # type: () -> None
        """
        Tests the setter and getter functionality of the WellLogValue class

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """

        logging = WellLog.load_all_from_db(self.session)
        self.assertEqual(len(logging), 1)
        logging = logging[0]
        self.assertEqual(logging.log_values[0].depth, 5)
        self.assertEqual(logging.log_values[1].value, 4)
        self.assertEqual(logging.log_values[2].name, 'name 1')
        self.assertEqual(logging.log_values[4].comment, 'Comment 2')
        self.assertEqual(logging.property_name, 'logging')
        self.assertEqual(logging.property_unit, 'unit name')

        logging.property_name = 'new log name'
        logging.property_unit = u'km²'

        del logging

        logging = WellLog.load_all_from_db(self.session)[0]
        self.assertEqual(logging.property_name, 'new log name')
        self.assertEqual(logging.property_unit, u'km²')

        longname = 4 * 'abcdefghijklmnopqrstuvwxyz'
        logging.property_name = longname
        logging.property_unit = longname

        del logging

        logging = WellLog.load_all_from_db(self.session)[0]
        self.assertEqual(logging.property_name, longname[:100])
        self.assertEqual(logging.property_unit, longname[:100])

    def test_insert_and_delete_logvalue(self):
        # type: () -> None
        """
        Test insertion and deletion functionality of class WellLog

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        logging = WellLog.load_all_from_db(self.session)[0]
        logging.insert_log_value(WellLogValue(14.3, 1234, self.session, '', ''))
        self.assertRaises(ValueError, logging.insert_log_value, WellLogValue(556, 1234, self.session, '', ''))

        del logging

        logging = WellLog.load_all_from_db(self.session)[0]
        self.assertEqual(6, len(logging.log_values))
        self.assertEqual(14.3, logging.log_values[2].depth)
        self.assertEqual(1234, logging.get_value_by_depth(14.3).value)
        self.assertRaises(ValueError, logging.get_value_by_depth, 13)
        self.assertRaises(ValueError, logging.get_value_by_depth, 'test')
        self.assertRaises(TypeError, logging.insert_log_value, 'abcde')

        logvalues = [
            WellLogValue(123, 4152, self.session, '', ''),
            WellLogValue(156.34, 3456, self.session, '', ''),
            WellLogValue(16.2, 34.43, self.session, '', ''),
            WellLogValue(15.8, '234.2', self.session, '', '')
        ]

        logging.insert_multiple_log_values(logvalues)
        self.assertRaises(TypeError, logging.insert_multiple_log_values, logvalues.append('abcde'))
        logvalues.pop()
        logvalues.append(WellLogValue(1234, 345, self.session, '', ''))
        self.assertRaises(ValueError, logging.insert_multiple_log_values, logvalues)

        del logging

        logging = WellLog.load_all_from_db(self.session)[0]
        self.assertEqual(10, len(logging.log_values))
        self.assertEqual(14.3, logging.log_values[2].depth)
        self.assertEqual(3456, logging.get_value_by_depth(156.34).value)
        self.assertListEqual([5, 10, 14.3, 15, 15.8, 16, 16.2, 17, 123, 156.34], [x.depth for x in logging.log_values])
        self.assertEqual(34.43, logging.log_values[6].value)

        logging.delete_value(logging.get_value_by_depth(16))

        del logging

        logging = WellLog.load_all_from_db(self.session)[0]
        self.assertEqual(9, len(logging.log_values))
        self.assertEqual(14.3, logging.log_values[2].depth)
        self.assertEqual(234, logging.log_values[6].value)
        self.assertRaises(ValueError, logging.get_value_by_depth, 16)
        self.assertListEqual([5, 10, 14.3, 15, 15.8, 16.2, 17, 123, 156.34], [x.depth for x in logging.log_values])

    def tearDown(self):
        # type: () -> None
        """
        Empty function, nothing to shutdown after the testing process

        :return: Nothing
        """
        pass


class TestPropertyClass(unittest.TestCase):
    """
    a unittest for Property class
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
        point = GeoPoint(StratigraphicObject.init_stratigraphy(self.session, 'mu', 1), True, '', 1, 2, 3, self.session, 'test',
                         '')
        point.save_to_db()

        prop = Property('test prop', 'test unit', self.session)
        point.add_property(prop)
        prop = Property('test prop 2', 'test unit 2', self.session)
        point.add_property(prop)

    def test_init(self):
        # type: () -> None
        """
        Test the initialisation of the class

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        point = GeoPoint.load_all_from_db(self.session)[0]
        self.assertEqual(2, len(point.properties))
        self.assertEqual('test prop', point.properties[0].property_name)
        self.assertEqual('test prop 2', point.properties[1].property_name)
        self.assertEqual('test unit', point.properties[0].property_unit)
        self.assertEqual('test unit 2', point.properties[1].property_unit)

    def test_setter_and_getter(self):
        # type: () -> None
        """
        Test the setter and getter functionality

        :return: Nothing
        :raises AssertionError: Raises Assertion Error when a test fails
        """
        point = GeoPoint.load_all_from_db(self.session)[0]
        point.properties[0].value = 342.234
        point.properties[1].value = "345.34"
        point.properties[1].name = "some text information"
        point.properties[1].comment = "unused"

        with self.assertRaises(ValueError):
            point.properties[0].value = "string"

        del point

        point = GeoPoint.load_all_from_db(self.session)[0]
        self.assertEqual(342.234, point.properties[0].value)
        self.assertEqual(345.34, point.properties[1].value)
        self.assertEqual('some text information', point.properties[1].name)
        self.assertEqual('unused', point.properties[1].comment)

    def tearDown(self):
        # type: () -> None
        """
        Empty function, nothing to shutdown after the testing process

        :return: Nothing
        """
        pass


if __name__ == '__main__':
    unittest.main()
