# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.Geometries.Line class using unittest
"""

import sys
import unittest

from sqlalchemy.orm.exc import NoResultFound

from GeologicalToolbox.DBHandler import DBHandler
from GeologicalToolbox.Geometries import GeoPoint, Line
from GeologicalToolbox.Stratigraphy import StratigraphicObject


class TestLineClass(unittest.TestCase):
    """
    This is a unittest class for the Resources.Geometries.Line class
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

        # handler = DBHandler(
        # 		connection='sqlite:////Users/stephan/Documents/data.db',
        # 		debug=False)
        # handler = DBHandler(connection='sqlite:///D:\\data.db', debug=False)

        # add test data to the database
        self.lines = [
            {
                'closed': False,
                'horizon': 'mu',
                'age': 3,
                'update': False,
                'points': ((1204067.0548148106, 634617.5980860253),
                           (1204067.0548148106, 620742.1035724243),
                           (1215167.4504256917, 620742.1035724243),
                           (1215167.4504256917, 634617.5980860253),
                           (1204067.0548148106, 634617.5980860253)),
                'name': 'Line_1'
            }, {
                'closed': True,
                'horizon': 'so',
                'age': 2,
                'update': True,
                'points': ((1179553.6811741155, 647105.5431482664),
                           (1179553.6811741155, 626292.3013778647),
                           (1194354.20865529, 626292.3013778647),
                           (1194354.20865529, 647105.5431482664)),
                'name': 'Line_2'
            }, {
                'closed': False,
                'horizon': 'mm',
                'age': 4,
                'update': True,
                'points': ((1179091.1646903288, 712782.8838459781),
                           (1161053.0218226474, 667456.2684348812),
                           (1214704.933941905, 641092.8288590391),
                           (1228580.428455506, 682719.3123998424),
                           (1218405.0658121984, 721108.1805541387)),
                'name': 'Line_3'
            }, {
                'closed': False,
                'horizon': 'mo',
                'age': 5,
                'update': True,
                'points': ((1149490.1097279799, 691044.6091080031),
                           (1149490.1097279799, 648030.5761158396),
                           (1191579.1097525698, 648030.5761158396),
                           (1149490.1097279799, 648030.5761158396),
                           (1191579.1097525698, 691044.6091080031),
                           (1149490.1097279799, 691044.6091080031)),
                'name': 'Line_2'
            }
        ]

        for line in self.lines:
            points = list()
            for point in line['points']:
                points.append(GeoPoint(None, False, '', point[0], point[1], 0, self.session, line['name'], ''))
            new_line = Line(line['closed'],
                            StratigraphicObject.init_stratigraphy(self.session, line['horizon'], line['age'],
                                                                  line['update']),
                            points, self.session, line['name'], '')
            new_line.save_to_db()

    def test_init(self):
        # type: () -> None
        """
        Test the initialisation of the database

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
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
        stored_horizons = [x.unit_name for x in self.session.query(StratigraphicObject.unit_name).all()]
        # expected number of horizons
        horizons = set([x['horizon'] for x in self.lines])

        self.assertEqual(count_points, pnts,
                         "Number of points {} doesn't match the number of stored database points {}!". \
                         format(count_points, pnts))
        self.assertEqual(count_lines, len(self.lines),
                         "Number of lines {} doesn't match the number of stored database lines {}!". \
                         format(count_lines, len(self.lines)))
        if sys.version_info[0] == 2:
            self.assertItemsEqual(horizons, stored_horizons, "Horizons doesn't match.\nDatabase: {}\nShould be: {}". \
                                  format(stored_horizons, horizons))
        else:
            self.assertCountEqual(horizons, stored_horizons, "Horizons doesn't match.\nDatabase: {}\nShould be: {}". \
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

    def test_insert_one(self):
        # type: () -> None
        """
        Test the insertion of one point. Additionally test get_point_index(point) function

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        insert_point = GeoPoint(StratigraphicObject.init_stratigraphy(self.session, 'mu'), False, '', 1204200, 620800,
                                0,
                                self.session)
        line_query = self.session.query(Line).filter_by(id=1)
        count = line_query.count()
        self.assertEqual(count, 1, "Get more than one expected result for line-id-request ({})".format(count))
        line = line_query.one()
        line.session = self.session
        line.insert_point(insert_point, 1)

        self.assertEqual(line.points[1].line_pos, 1)

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

        # test Exception handling
        self.assertRaises(TypeError, line.insert_point, "string", 1)
        self.assertRaises(ValueError, line.insert_points, insert_point, "abc")

    def test_insert_multiple(self):
        # type: () -> None
        """
        Test the insertion of multiple points. Although test remove of doubled values in a line.

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        insert_point_1 = GeoPoint(StratigraphicObject.init_stratigraphy(self.session, 'mu'), False, '', 1204200, 620800,
                                  0,
                                  self.session)
        insert_point_2 = GeoPoint(StratigraphicObject.init_stratigraphy(self.session, 'mu'), False, '', 1204500, 621200,
                                  0,
                                  self.session)
        insert_point_3 = GeoPoint(StratigraphicObject.init_stratigraphy(self.session, 'mu'), False, '', 1204700, 621000,
                                  0,
                                  self.session)
        insert_point_4 = GeoPoint(StratigraphicObject.init_stratigraphy(self.session, 'mu'), False, '', 1204700, 621000,
                                  0,
                                  self.session)

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
        del insert_point_1, insert_point_2, insert_point_3
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

        # test Exception handling
        self.assertRaises(ValueError, line.insert_points, points, "abc")
        points.append('cde')
        self.assertRaises(TypeError, line.insert_points, points, 2)

    def test_delete_point(self):
        # type: () -> None
        """
        Test the deletion of a point.
        /1/ the point itself
        /2/ delete by coordinates
        /3/ test auto-removal of doubled points after deletion

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
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

        # test exception handling
        self.assertRaises(TypeError, line.delete_point, "string")
        self.assertRaises(ValueError, line.delete_point, GeoPoint(None, False, '', 1, 2, 0, self.session, '', ''))

        del line

        # /2/ test deletion by coordinates
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
        self.assertEqual(line.points[1].id, 10,
                         "First point before deleted point should have id {} but has {}".format(10, line.points[1].id))
        self.assertEqual(line.points[2].id, 12,
                         "First point after deleted point should have id {} but has {}".format(12, line.points[2].id))

        # test exception handling
        self.assertRaises(ValueError, line.delete_point_by_coordinates, 123, 456, "test")
        self.assertRaises(ValueError, line.delete_point_by_coordinates, 123, 456, 789)

        # /3/ test auto-removal of doubled points after deletion
        line_query = self.session.query(Line).filter_by(id=4)
        count = line_query.count()
        self.assertEqual(count, 1, "Get more than one expected result for line-id-request ({})".format(count))
        line = line_query.one()
        line.session = self.session
        line.delete_point_by_coordinates(1191579.1097525698, 648030.5761158396, 0)

        # save deletion and reload line, test afterwards
        line.save_to_db()
        del count
        del line
        del line_query

        line = self.session.query(Line).filter_by(id=4).one()
        self.assertEqual(len(line.points), 3, "Wrong Nr of points ({}), should be {}".format(len(line.points), 3))
        self.assertEqual(line.points[1].id, 15,
                         "First point before deleted point should have id {} but has {}".format(15, line.points[1].id))
        self.assertEqual(line.points[2].id, 18,
                         "First point after deleted point should have id {} but has {}".format(18, line.points[2].id))

    def test_loading(self):
        # type: () -> None
        """
        Test the different types of loading of lines from the db.
        Part 1: load all lines from the database
        Part 2: load line by id
        Part 3: load lines by name
        Part 4: load lines with minimal one point in given extent

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """

        # Part 1: load all lines from the database
        lines = Line.load_all_from_db(self.session)

        self.assertEqual(len(lines), 4, "Wrong number of lines ({}), should be {}".format(len(lines), 4))
        self.assertEqual(lines[0].id, 1, "First line has wrong id ({}), should be {}".format(lines[0].id, 1))
        self.assertEqual(len(lines[0].points), 4, "Number of points ({}) of the first line is wrong. Should be {}". \
                         format(len(lines[0].points), 4))
        self.assertEqual(lines[3].id, 4, "First line has wrong id ({}), should be {}".format(lines[3].id, 4))
        self.assertEqual(len(lines[3].points), 5, "Number of points ({}) of the first line is wrong. Should be {}". \
                         format(len(lines[3].points), 5))

        # test exception handling
        self.assertRaises(TypeError, Line.load_all_from_db, "test")

        del lines

        # Part 2: load line by id
        line = Line.load_by_id_from_db(2, self.session)
        self.assertEqual(line.id, 2, "line id is wrong ({}), should be {}".format(line.id, 2))
        self.assertEqual(len(line.points), 4, "Number of points ({}) of the line with id=2 is wrong. Should be {}". \
                         format(len(line.points), 4))
        self.assertEqual(line.points[0].id, 5, "first point in line with id=2 should have id {}, is {}". \
                         format(5, line.points[0].id))
        self.assertEqual(line.points[-1].id, 8, "last point in line with id=2 should have id {}, is {}". \
                         format(8, line.points[-1].id))

        # test exception handling
        self.assertRaises(NoResultFound, Line.load_by_id_from_db, 25, self.session)

        del line

        # Part 3: load lines by name
        lines = Line.load_by_name_from_db("Line_3", self.session)
        self.assertEqual(len(lines), 1, "Wrong number of lines ({}), should be {}".format(len(lines), 1))
        self.assertEqual(lines[0].id, 3, "Returned line has wrong id ({}), should be {}".format(lines[0].id, 3))

        del lines

        lines = Line.load_by_name_from_db("Line_2", self.session)
        self.assertEqual(len(lines), 2, "Wrong number of lines ({}), should be {}".format(len(lines), 2))
        self.assertEqual(lines[0].id, 2, "Returned line has wrong id ({}), should be {}".format(lines[0].id, 2))
        self.assertEqual(lines[1].id, 4, "Returned line has wrong id ({}), should be {}".format(lines[0].id, 4))

        del lines

        lines = Line.load_by_name_from_db("Test", self.session)
        self.assertEqual(len(lines), 0, "Wrong number of lines ({}), should be {}".format(len(lines), 0))

        del lines

        # Part 4: load lines with minimal one point in given extent
        # x -> 1174000 - 1200000
        # y ->  613500 -  651000
        # should return 2 lines with id 2 and 4 ("Line_2")
        lines = Line.load_in_extent_from_db(self.session, 1174000, 1200000, 613500, 651000)
        self.assertEqual(len(lines), 2, "Wrong number of lines ({}), should be {}".format(len(lines), 2))
        self.assertEqual(lines[0].id, 2, "Returned line has wrong id ({}), should be {}".format(lines[0].id, 2))
        self.assertEqual(lines[1].id, 4, "Returned line has wrong id ({}), should be {}".format(lines[0].id, 4))

        del lines

        lines = Line.load_in_extent_from_db(self.session, 0, 1, 0, 1)
        self.assertEqual(len(lines), 0, "Wrong number of lines ({}), should be {}".format(len(lines), 9))

        del lines

    def test_setter_and_getter(self):
        # type: () -> None
        """
        Test the setter and getter functions of class Line

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        lines = Line.load_all_from_db(self.session)
        lines[0].is_closed = True
        lines[1].horizon = StratigraphicObject.init_stratigraphy(self.session, 'mu')
        lines[2].name = 'Line_2'
        session_2 = lines[3].session
        lines[3].session = session_2

        for line in lines:
            line.save_to_db()

        del lines

        lines = Line.load_all_from_db(self.session)
        line_with_name = Line.load_by_name_from_db('Line_2', self.session)
        self.assertTrue(lines[0].is_closed, "First line should be changed to closed.")
        self.assertEqual(lines[1].horizon.name, 'mu',
                         "Second line has wrong horizon ({}). Should have {}.".format(lines[1].horizon.name, 'mu'))
        self.assertEqual(lines[2].name, 'Line_2',
                         "Third line has wrong line name ({}). Should have {}".format(lines[2].name, 'Line_2'))
        self.assertEqual(len(line_with_name), 3, "Wrong Number of lines with line name 'Line_2' ({}). Should be {}". \
                         format(len(line_with_name), 3))

        def tearDown(self):
            # type: () -> None
            """
            Empty function, nothing to shutdown after the testing process

            :return: Nothing
            """
            pass

    if __name__ == '__main__':
        unittest.main()
