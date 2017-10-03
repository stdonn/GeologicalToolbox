# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.Geometries.Line class using unittest
"""

import unittest

from Resources.DBHandler import DBHandler
from Resources.Geometries import GeoPoint, Line
from Resources.Stratigraphy import Stratigraphy


class TestLineClass(unittest.TestCase):
	def setUp(self):
		# type: () -> None
		"""
		Initialise a temporary database connection for all test cases and fill the database with test data
		:return: None
		"""
		# initialise a in-memory sqlite database
		self.handler = DBHandler(connection='sqlite://', debug=False)
		self.session = self.handler.get_session()

		# handler = DBHandler(
		# 		connection='sqlite:////Users/stephan/Documents/work/Dissertation/GIS/Modelling-Toolbox/data.db',
		# 		debug=False)
		# handler = DBHandler(connection='sqlite:///D:\\data.db', debug=False)

		# add test data to the database
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
				            (1194354.20865529, 647105.5431482664),
				            (1179553.6811741155, 647105.5431482664)),
				'name'   : 'Line_2'
			}, {
				'closed' : True,
				'horizon': 'mm',
				'age'    : 4,
				'update' : True,
				'points' : ((1179091.1646903288, 712782.8838459781),
				            (1161053.0218226474, 667456.2684348812),
				            (1214704.933941905, 641092.8288590391),
				            (1228580.428455506, 682719.3123998424),
				            (1218405.0658121984, 721108.1805541387),
				            (1179091.1646903288, 712782.8838459781)),
				'name'   : 'Line_3'
			}, {
				'closed' : False,
				'horizon': 'mo',
				'age'    : 5,
				'update' : True,
				'points' : ((1149490.1097279799, 691044.6091080031),
				            (1149490.1097279799, 648030.5761158396),
				            (1191579.1097525698, 648030.5761158396),
				            (1191579.1097525698, 691044.6091080031),
				            (1149490.1097279799, 691044.6091080031)),
				'name'   : 'Line_2'
			}
		]

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

		:return: None
		:rtype: None
		"""

		pnts = 0
		for line in self.lines:
			pnts += len(line['points'])

		count_points = self.session.query(GeoPoint).count()
		count_lines = self.session.query(Line).count()
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

	def test_insert_one(self):
		# type: () -> None
		"""
		Test the insertion of one point. Additionally test get_point_index(point) function

		:return: None
		:rtype: None
		"""
		insert_point = GeoPoint(1204200, 620800, None, Stratigraphy(self.session, "mu"), self.session)
		line_query = self.session.query(Line).filter_by(id=1)
		count = line_query.count()
		self.assertEqual(count, 1, "Get more than one expected result for line-id-request ({})".format(count))
		line = line_query.one()
		line.session = self.session
		line.insert_point(insert_point, 1)
		line.save_to_db()

		# point is inserted, now delete insert details
		del count
		del line
		del line_query

		# test the insertion-process
		line_query = self.session.query(Line).filter_by(id=1)
		count = line_query.count()
		self.assertEqual(count, 1, "Get more than one expected result for line-id-request ({})".format(count))
		line = line_query.one()
		# 21 Point initially, new point is Nr 22 -> id=22
		# !!!ATTENTION!!! counting starts with 1 not 0 in sqlite-DB!
		# line-pos and get_point_index should be 1
		self.assertEqual(line.points[1].id, 22, "Wrong id ({}) for new point (should be {})". \
		                 format(line.points[1].id, 22))
		self.assertEqual(line.points[1].line_pos, 1, "Wrong position of the new point ({}) in the line (should be {})". \
		                 format(line.points[1].line_pos, 1))
		self.assertEqual(line.get_point_index(insert_point), 1,
		                 "Wrong get_point_index(...) value ({}) in the line (should be {})". \
		                 format(line.get_point_index(insert_point), 1))
		self.assertEqual(line.points[1].easting, 1204200, "Wrong easting ({} / should be {})". \
		                 format(line.points[1].easting, 1204200))
		self.assertEqual(line.points[1].northing, 620800, "Wrong northing ({} / should be {})". \
		                 format(line.points[1].northing, 620800))
		self.assertEqual(line.points[1].altitude, 0, "Wrong altitude ({} / should be {})". \
		                 format(line.points[1].altitude, 0))
		self.assertEqual(line.points[1].has_z, False, "Wrong has_z ({} / should be {})". \
		                 format(line.points[1].has_z, False))

	def test_insert_multiple(self):
		# type: () -> None
		"""
		Test the insertion of multiple points. Although test remove of doubled values in a line.

		:return: None
		:rtype: None
		"""
		insert_point_1 = GeoPoint(1204200, 620800, None, Stratigraphy(self.session, "mu"), self.session)
		insert_point_2 = GeoPoint(1204500, 621200, None, Stratigraphy(self.session, "mu"), self.session)
		insert_point_3 = GeoPoint(1204700, 621000, None, Stratigraphy(self.session, "mu"), self.session)
		insert_point_4 = GeoPoint(1204700, 621000, None, Stratigraphy(self.session, "mu"), self.session)

		points = [insert_point_1, insert_point_2, insert_point_3, insert_point_4]
		line_query = self.session.query(Line).filter_by(id=1)
		count = line_query.count()
		self.assertEqual(count, 1, "Get more than one expected result for line-id-request ({})".format(count))
		line = line_query.one()
		line.session = self.session
		line.insert_points(points, 1)
		line.save_to_db()

		# point is inserted, now delete insert details
		del count
		del insert_point_1, insert_point_2, insert_point_3, points
		del line
		del line_query

		# test the insertion-process
		line_query = self.session.query(Line).filter_by(id=1)
		count = line_query.count()
		self.assertEqual(count, 1, "Get more than one expected result for line-id-request ({})".format(count))
		line = line_query.one()
		# 21 Point initially, new point are Nr 22-24 -> id=22 to 24
		# !!!ATTENTION!!! counting starts with 1 not 0 in sqlite-DB!
		# line-pos should be 1, 2 and 3
		self.assertEqual(line.points[1].id, 22, "Wrong id ({}) for new point (should be {})". \
		                 format(line.points[1].id, 22))
		self.assertEqual(line.points[2].id, 23, "Wrong id ({}) for new point (should be {})". \
		                 format(line.points[2].id, 23))
		self.assertEqual(line.points[3].id, 24, "Wrong id ({}) for new point (should be {})". \
		                 format(line.points[3].id, 24))
		self.assertEqual(line.points[4].id, 2, "Wrong id ({}) for point after insert (should be {})". \
		                 format(line.points[4].id, 2))
		self.assertEqual(line.points[1].line_pos, 1, "Wrong position of the new point ({}) in the line (should be {})". \
		                 format(line.points[1].line_pos, 1))
		self.assertEqual(line.points[1].line_pos, 1, "Wrong position of the new point ({}) in the line (should be {})". \
		                 format(line.points[2].line_pos, 2))
		self.assertEqual(line.points[1].line_pos, 1, "Wrong position of the new point ({}) in the line (should be {})". \
		                 format(line.points[3].line_pos, 3))
		self.assertEqual(line.points[1].easting, 1204200, "Wrong easting ({} / should be {})". \
		                 format(line.points[1].easting, 1204200))
		self.assertEqual(line.points[1].northing, 620800, "Wrong northing ({} / should be {})". \
		                 format(line.points[1].northing, 620800))
		self.assertEqual(line.points[1].altitude, 0, "Wrong altitude ({} / should be {})". \
		                 format(line.points[1].altitude, 0))
		self.assertEqual(line.points[1].has_z, False, "Wrong has_z ({} / should be {})". \
		                 format(line.points[1].has_z, False))

		print(str(line))

	def test_delete_point(self):
		# type: () -> None
		"""
		Test the deletion of a point

		:return: None
		:rtype: None
		"""

		line_query = self.session.query(Line).filter_by(id=2)
		count = line_query.count()
		self.assertEqual(count, 1, "Get more than one expected result for line-id-request ({})".format(count))
		line = line_query.one()
		line.session = self.session
		line.delete_point(line.points[2])
		self.assertEqual(len(line.points), 4, "Wrong Nr of points ({}), should be {}".format(len(line.points), 4))
		line.save_to_db()


	def tearDown(self):
		# type: () -> None
		"""
		Empty function, nothing to shut down after the testing process

		:return: None
		:rtype: None
		"""
		pass


if __name__ == '__main__':
	unittest.main()
