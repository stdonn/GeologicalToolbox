# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.PropertyLogs-Module classes using unittests
"""

import unittest

from Exceptions import WellMarkerException
from Resources.DBHandler import DBHandler
from Resources.PropertyLogs import WellLogValue, WellLogging
from Resources.Wells import WellMarker, Well


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
        self.handler = DBHandler(connection='sqlite://', debug=False)
        self.session = self.handler.get_session()

        # add test data to the database
        self.log_values = [
            {
                'depth' : 200,
                'value' : 123,
                'name': 'log name',
                'comment': 'unknown'
            }, {
                'depth' : 200.324,
                'value' : 12.5455,
                'name': 'log name 2',
                'comment': 'unknown'
            }, {
                'depth' : '2345.54',
                'value' : '641.54',
                'name': '',
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
