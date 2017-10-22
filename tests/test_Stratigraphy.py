# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.Stratigraphy.Stratigraphy class using unittest
"""

import unittest

from Resources.DBHandler import DBHandler
from Resources.Stratigraphy import Stratigraphy


class TestStratigraphyClass(unittest.TestCase):
	def setUp(self):
		# type: () -> None
		"""
		Initialise a temporary database connection for all test cases and fill the database with test data

		:return: None
		"""
		# initialise a in-memory sqlite database
		self.handler = DBHandler(connection='sqlite://', debug=False)
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
			new_unit = Stratigraphy.init_stratigraphy(self.session, unit['name'], unit['age'], unit['update'])
			new_unit.save_to_db()

	def test_init(self):
		pass

	def tearDown(self):
		# type: () -> None
		"""
		Empty function, nothing to shutdown after the testing process

		:return: Nothing
		"""
		pass


if __name__ == '__main__':
	unittest.main()
