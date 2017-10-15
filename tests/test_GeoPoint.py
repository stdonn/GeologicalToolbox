# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.Geometries.GeoPoint class using unittest
"""

import unittest

from Resources.DBHandler import DBHandler
from Resources.Geometries import GeoPoint, Line
from Resources.Stratigraphy import Stratigraphy


class TestGeoPointClass(unittest.TestCase):
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
		self.points = [
			{
				"coords" : (1234134, 5465462, 123),
				"horizon": "mu",
				"age"    : 26,
				"name"   : ""
			},
			{
				"coords" : (1254367, 5443636, 156),
				"horizon": "so",
				"age"    : 26,
				"name"   : ""
			},
			{
				"coords" : (1265469, 5467929, None),
				"horizon": "mu",
				"age"    : 26,
				"name"   : "point set"
			},
			{
				"coords" : (1273456, 5449672, 101),
				"horizon": "mu",
				"age"    : 26,
				"name"   : "point set"
			}
		]

		self.lines = [
			{
				'closed' : False,
				'horizon': 'mu',
				'age'    : 3,
				'update' : False,
				'points' : ((1204067.0548148106, 634617.5980860253),
				            (1204067.0548148106, 620742.1035724243),
				            (1215167.4504256917, 620742.1035724243),
				            (1215167.4504256917, 634617.5980860253),
				            (1204067.0548148106, 634617.5980860253)),
				'name'   : 'Line_1'
			}, {
				'closed' : True,
				'horizon': 'so',
				'age'    : 2,
				'update' : True,
				'points' : ((1179553.6811741155, 647105.5431482664),
				            (1179553.6811741155, 626292.3013778647),
				            (1194354.20865529, 626292.3013778647),
				            (1194354.20865529, 647105.5431482664)),
				'name'   : 'Line_2'
			}, {
				'closed' : False,
				'horizon': 'mm',
				'age'    : 4,
				'update' : True,
				'points' : ((1179091.1646903288, 712782.8838459781),
				            (1161053.0218226474, 667456.2684348812),
				            (1214704.933941905, 641092.8288590391),
				            (1228580.428455506, 682719.3123998424),
				            (1218405.0658121984, 721108.1805541387)),
				'name'   : 'Line_3'
			}, {
				'closed' : False,
				'horizon': 'mo',
				'age'    : 5,
				'update' : True,
				'points' : ((1149490.1097279799, 691044.6091080031),
				            (1149490.1097279799, 648030.5761158396),
				            (1191579.1097525698, 648030.5761158396),
				            (1149490.1097279799, 648030.5761158396),
				            (1191579.1097525698, 691044.6091080031),
				            (1149490.1097279799, 691044.6091080031)),
				'name'   : 'Line_2'
			}
		]

		for point in self.points:
			new_point = GeoPoint(point["coords"][0], point["coords"][1], point["coords"][2],
			                     Stratigraphy(self.session, point["horizon"], point["age"], False), self.session,
			                     point["name"])
			new_point.save_to_db()

		for line in self.lines:
			points = list()
			for point in line['points']:
				points.append(GeoPoint(point[0], point[1], None, None, self.session, ""))
			new_line = Line(line['closed'], self.session,
			                Stratigraphy(self.session, line['horizon'], line['age'], line['update']), points,
			                line['name'])
			new_line.save_to_db()

	def test_init(self):
		# type: () -> None
		"""
		Test the initialisation of the database

		:return: Nothing
		"""

		pnts = len(self.points)
		for line in self.lines:
			pnts += len(line['points'])

		# 2 points will be automatically deleted and the lines will be closed
		pnts -= 2

		count_points = self.session.query(GeoPoint).count()
		lines = self.session.query(Line)
		count_lines = lines.count()
		lines = lines.all()
		stored_horizons = [x.name for x in self.session.query(Stratigraphy.name).all()]
		# expected number of horizons
		horizons = set([x['horizon'] for x in self.lines])

		self.assertEqual(count_points, pnts,
		                 "Number of points {} doesn't match the number of stored database points {}!". \
		                 format(count_points, pnts))
		self.assertEqual(count_lines, len(self.lines),
		                 "Number of lines {} doesn't match the number of stored database lines {}!". \
		                 format(count_lines, len(self.lines)))
		self.assertItemsEqual(horizons, stored_horizons, "Horizons doesn't match.\nDatabase: {}\nShould be: {}". \
		                      format(stored_horizons, horizons))
		self.assertEqual(len(lines[0].points), 4, "Number of points of the line with ID 1 should be {}, but is {}". \
		                 format(4, len(lines[0].points)))
		self.assertTrue(lines[0].is_closed, "line with ID 1 should be closed...")
		self.assertEqual(len(lines[1].points), 4, "Number of points of the line with ID 2 should be {}, but is {}". \
		                 format(4, len(lines[1].points)))
		self.assertTrue(lines[1].is_closed, "line with ID 2 should be closed...")
		self.assertEqual(len(lines[2].points), 5, "Number of points of the line with ID 3 should be {}, but is {}". \
		                 format(5, len(lines[2].points)))
		self.assertFalse(lines[2].is_closed, "line with ID 3 should not be closed...")
		self.assertEqual(len(lines[3].points), 5, "Number of points of the line with ID 4 should be {}, but is {}". \
		                 format(5, len(lines[3].points)))
		self.assertTrue(lines[3].is_closed, "line with ID 4 should be closed...")

	def tearDown(self):
		# type: () -> None
		"""
		Empty function, nothing to shutdown after the testing process

		:return: Nothing
		"""
		pass
