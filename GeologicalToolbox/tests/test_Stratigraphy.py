# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.StratigraphicObject.StratigraphicObject class using unittest
"""

import unittest

from GeologicalToolbox.DBHandler import DBHandler
from GeologicalToolbox.Stratigraphy import StratigraphicObject


class TestStratigraphyClass(unittest.TestCase):
    def setUp(self):
        # type: () -> None
        """
        Initialise a temporary database connection for all test cases and fill the database with test data

        :return: None
        """
        # initialise a in-memory sqlite database
        self.handler = DBHandler(connection='sqlite://', echo=False)
        self.session = self.handler.get_session()

        units = [
            {
                'name'  : 'mo',
                'age'   : 1,
                'update': False
            },
            {
                'name'  : 'mm',
                'age'   : 2,
                'update': True
            },
            {
                'name'  : 'mu',
                'age'   : 25,
                'update': False
            },
            {
                'name'  : 'so',
                'age'   : 4,
                'update': False
            },
            {
                'name'  : 'mu',
                'age'   : 3,
                'update': True
            },
            {
                'name'  : 'so',
                'age'   : 5,
                'update': False
            }
        ]

        for unit in units:
            new_unit = StratigraphicObject.init_stratigraphy(self.session, unit['name'], unit['age'], unit['update'])
            new_unit.save_to_db()

    def test_init(self):
        # type: () -> None
        """
        Test the initialisation

        :return: Nothing

        :raises AssertionError: Raises AssertionError if a test fails
        """
        result = self.session.query(StratigraphicObject).all()
        self.assertEqual(len(result), 4, "Wrong number of entries ({}). Should be {}.".format(len(result), 4))

    def test_loading(self):
        # type: () -> None
        """
        Test the loading functions of the stratigraphy class

        /1/ load all from database
        /2/ load by name from database
        /3/ load in age range from database

        :return: Nothing

        :raises AssertionError: Raises AssertionError if a test fails
        """

        # /1/ load all from database
        # additionally update value is tested for mu / so unit
        result = {unit.name: unit for unit in StratigraphicObject.load_all_from_db(self.session)}
        self.assertEqual(len(result), 4, "Wrong number of entries ({}). Should be {}.".format(len(result), 4))
        self.assertEqual(result['mu'].age, 3, "Wrong age for mu ({}). Should be {}".format(result['mu'].age, 3))
        self.assertEqual(result['so'].age, 4, "Wrong age for so ({}). Should be {}".format(result['so'].age, 4))

        del result

        # /2/ load by name from database
        result = StratigraphicObject.load_by_name_from_db('mo', self.session)
        self.assertEqual(result.age, 1, "Wrong age for mo ({}). Should be {}".format(result.age, 3))
        del result

        result = StratigraphicObject.load_by_name_from_db('sm', self.session)
        self.assertIsNone(result, 'Result for sm is not None, but should be: {}'.format(str(result)))
        del result

        # /3/ load in age range from database
        result = StratigraphicObject.load_by_age_from_db(2, 3, self.session)
        self.assertEqual(len(result), 2, "Wrong number of query results ({}). Should be {}.".format(len(result), 2))
        self.assertEqual(result[0].name, 'mm',
                         "Wrong name of first horizon ({}). Should be {}.".format(result[0], 'mm'))
        self.assertEqual(result[1].name, 'mu',
                         "Wrong name of second horizon ({}). Should be {}.".format(result[1], 'mu'))
        self.assertEqual(result[1].age, 3, "Wrong age for second horizon ({}). Should be {}.".format(result[1].age, 3))
        del result

        result = StratigraphicObject.load_by_age_from_db(4, 4, self.session)
        self.assertEqual(len(result), 1, "Wrong number of query results ({}). Should be {}.".format(len(result), 1))
        self.assertEqual(result[0].name, 'so',
                         "Wrong name of first horizon ({}). Should be {}.".format(result[0], 'so'))
        del result

        result = StratigraphicObject.load_by_age_from_db(5, 10, self.session)
        self.assertEqual(len(result), 0, "Wrong number of query results ({}). Should be {}.".format(len(result), 0))

    def test_setter_and_getter(self):
        # type: () -> None
        """
        Test setter and getters of class StratigraphicObject

        :return: Nothing

        :raises AssertionError: Raises AssertionError if a test fails
        """
        result = StratigraphicObject.load_by_name_from_db('mo', self.session)
        result.age = 10
        result.save_to_db()
        del result

        result = StratigraphicObject.load_by_name_from_db('mo', self.session)
        self.assertEqual(result.age, 10, "Wrong age for horizon 'mo' ({}). Should be {}.".format(result.age, 10))

        result.name = 'Blubb'
        result.save_to_db()
        del result

        result = StratigraphicObject.load_by_age_from_db(10, 10, self.session)
        self.assertEqual(len(result), 1, "Wrong number of query results ({}). Should be {}.".format(len(result), 1))
        self.assertEqual(result[0].name, 'Blubb',
                         "Wrong name of stratigraphic unit ({}). Should be {}".format(result[0].name, 'Blubb'))

    def tearDown(self):
        # type: () -> None
        """
        Empty function, nothing to shutdown after the testing process

        :return: Nothing
        """
        pass


if __name__ == '__main__':
    unittest.main()
