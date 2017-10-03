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
				            (1191579.1097525698, 691044.6091080031),
				            (1191579.1097525698, 648030.5761158396),
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
		self.assertEqual(len(lines[0].points), 4,
		                 "Number of points of the line with ID 1 should be {}, but is {}".format(4, len(lines[0].points)))
		self.assertTrue(lines[0].is_closed, "line with ID 1 should be closed...")
		self.assertEqual(len(lines[1].points), 4,
		                 "Number of points of the line with ID 2 should be {}, but is {}".format(4, len(lines[1].points)))
		self.assertTrue(lines[1].is_closed, "line with ID 2 should be closed...")
		self.assertEqual(len(lines[2].points), 5,
		                 "Number of points of the line with ID 3 should be {}, but is {}".format(5, len(lines[2].points)))
		self.assertFalse(lines[2].is_closed, "line with ID 3 should not be closed...")
		self.assertEqual(len(lines[3].points), 5,
		                 "Number of points of the line with ID 4 should be {}, but is {}".format(5, len(lines[3].points)))
		self.assertTrue(lines[3].is_closed, "line with ID 4 should be closed...")

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
		# 20 Point initially, 2 removed, new point is Nr 19 -> id=19
		# !!!ATTENTION!!! counting starts with 1 not 0 in sqlite-DB!
		# line-pos and get_point_index should be 1
		self.assertEqual(line.points[1].id, 19, "Wrong id ({}) for new point (should be {})". \
		                 format(line.points[1].id, 19))
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
		# 20 Point initially, 2 removed, new point are Nr 19-21 -> id=19 to 21
		# !!!ATTENTION!!! counting starts with 1 not 0 in sqlite-DB!
		# line-pos should be 1, 2 and 3
		self.assertEqual(line.points[1].id, 19, "Wrong id ({}) for new point (should be {})". \
		                 format(line.points[1].id, 19))
		self.assertEqual(line.points[2].id, 20, "Wrong id ({}) for new point (should be {})". \
		                 format(line.points[2].id, 20))
		self.assertEqual(line.points[3].id, 21, "Wrong id ({}) for new point (should be {})". \
		                 format(line.points[3].id, 21))
		self.assertEqual(line.points[4].id, 2, "Wrong id ({}) for point after insert (should be {})". \
		                 format(line.points[4].id, 2))
		self.assertEqual(line.points[1].line_pos, 1, "Wrong position of the new point ({}) in the line (should be {})". \
		                 format(line.points[1].line_pos, 1))
		self.assertEqual(line.points[2].line_pos, 2, "Wrong position of the new point ({}) in the line (should be {})". \
		                 format(line.points[2].line_pos, 2))
		self.assertEqual(line.points[3].line_pos, 3, "Wrong position of the new point ({}) in the line (should be {})". \
		                 format(line.points[3].line_pos, 3))
		self.assertEqual(line.points[1].easting, 1204200, "Wrong easting ({} / should be {})". \
		                 format(line.points[1].easting, 1204200))
		self.assertEqual(line.points[1].northing, 620800, "Wrong northing ({} / should be {})". \
		                 format(line.points[1].northing, 620800))
		self.assertEqual(line.points[1].altitude, 0, "Wrong altitude ({} / should be {})". \
		                 format(line.points[1].altitude, 0))
		self.assertEqual(line.points[1].has_z, False, "Wrong has_z ({} / should be {})". \
		                 format(line.points[1].has_z, False))

	def test_delete_point(self):
		# type: () -> None
		"""
		Test the deletion of a point.
		Part 1: the point itself
		Part 2: delete by coordinates
		Part 3: test auto-removal of doubled points after deletion

		:return: None
		:rtype: None
		"""

		line_query = self.session.query(Line).filter_by(id=2)
		count = line_query.count()
		self.assertEqual(count, 1, "Get more than one expected result for line-id-request ({})".format(count))
		line = line_query.one()
		line.session = self.session
		line.delete_point(line.points[2])

		# save deletion and reload line, test afterwards
		line.save_to_db()
		del count
		del line
		del line_query

		line = self.session.query(Line).filter_by(id=2).one()
		self.assertEqual(len(line.points), 3, "Wrong Nr of points ({}), should be {}".format(len(line.points), 3))
		del line

		# Part 2: test deletion by coordinates
		line_query = self.session.query(Line).filter_by(id=3)
		count = line_query.count()
		self.assertEqual(count, 1, "Get more than one expected result for line-id-request ({})".format(count))
		line = line_query.one()
		line.session = self.session
		line.delete_point_by_coordinates(1214704.933941905, 641092.8288590391, 0)

		# save deletion and reload line, test afterwards
		line.save_to_db()
		del count
		del line
		del line_query

		line = self.session.query(Line).filter_by(id=3).one()
		self.assertEqual(len(line.points), 4, "Wrong Nr of points ({}), should be {}".format(len(line.points), 4))

		# Part 3: test auto-removal of doubled points after deletion
		line_query = self.session.query(Line).filter_by(id=4)
		count = line_query.count()
		self.assertEqual(count, 1, "Get more than one expected result for line-id-request ({})".format(count))
		line = line_query.one()
		line.session = self.session
		line.delete_point_by_coordinates(1191579.1097525698, 691044.6091080031, 0)

		# save deletion and reload line, test afterwards
		line.save_to_db()
		del count
		del line
		del line_query

		line = self.session.query(Line).filter_by(id=4).one()
		self.assertEqual(len(line.points), 3, "Wrong Nr of points ({}), should be {}".format(len(line.points), 3))

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
