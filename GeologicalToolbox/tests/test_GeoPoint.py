# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.Geometries.GeoPoint class using unittest
"""

import math
import sys
import unittest

from GeologicalToolbox.DBHandler import DBHandler
from GeologicalToolbox.Geometries import GeoPoint, Line
from GeologicalToolbox.Properties import Property
from GeologicalToolbox.Stratigraphy import StratigraphicObject
from GeologicalToolbox.Constants import float_precision


class TestGeoPointClass(unittest.TestCase):
    """
    This is a unittest class for the Resources.Geometries.GeoPoint class
    """

    def setUp(self):
        # type: () -> Nonetmp.sqlite
        """
        Initialise a temporary database connection for all test cases and fill the database with test data

        :return: None
        """
        # initialise a in-memory sqlite database
        # self.handler = DBHandler(connection='sqlite:///C:\\Users\\steph\\PycharmProjects\\Modelling-Toolbox\\tmp.sqlite', echo=False)
        self.handler = DBHandler(connection='sqlite://', echo=False)
        self.session = self.handler.get_session()

        # add test data to the database
        self.points = [
            {
                'coords': (1234134, 5465462, 123),
                'horizon': 'mu',
                'age': 3,
                'name': '',
                'update': False
            },
            {
                'coords': (1254367, 5443636, 156),
                'horizon': 'so',
                'age': 23,
                'name': '',
                'update': False
            },
            {
                'coords': (1265469, 5467929, None),
                'horizon': 'sm',
                'age': 5,
                'name': 'point set',
                'update': False
            },
            {
                'coords': (1273456, 5449672, 101),
                'horizon': 'mu',
                'age': 26,
                'name': 'point set',
                'update': True
            }
        ]

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

        for point in self.points:
            strat = StratigraphicObject.init_stratigraphy(self.session, point['horizon'], point['age'], point['update'])
            new_point = GeoPoint(strat, False if (point['coords'][2] is None) else True, '', point['coords'][0],
                                 point['coords'][1], 0 if (point['coords'][2] is None) else point['coords'][2],
                                 self.session, point['name'], '')
            new_point.save_to_db()

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

        pnts = len(self.points)
        for line in self.lines:
            pnts += len(line['points'])

        # 2 points will be automatically deleted and the lines will be closed
        pnts -= 2

        points = self.session.query(GeoPoint)
        count_points = points.count()
        points = points.all()
        stored_horizons = self.session.query(StratigraphicObject).all()
        # for horizon in stored_horizons:
        #	print(str(horizon))

        # print()

        stored_horizons = [x.name for x in stored_horizons]
        # expected number of horizons
        horizons = set([x['horizon'] for x in self.lines] + [x['horizon'] for x in self.points])

        # for point in points:
        #	print(str(point))

        self.assertEqual(count_points, pnts,
                         "Number of points {} doesn't match the number of stored database points {}!". \
                         format(count_points, pnts))

        if sys.version_info[0] == 2:
            self.assertItemsEqual(horizons, stored_horizons, "Horizons doesn't match.\nDatabase: {}\nShould be: {}". \
                                  format(stored_horizons, horizons))
        else:
            self.assertCountEqual(horizons, stored_horizons, "Horizons doesn't match.\nDatabase: {}\nShould be: {}". \
                                  format(stored_horizons, horizons))
        self.assertEqual(points[0].id, 1, "Wrong ID {} for first point. Should be {}". \
                         format(points[0].id, 1))
        self.assertEqual(points[0].horizon.name, 'mu',
                         "Wrong name of stratigraphic unit ({}) of first point. Should be ". \
                         format(points[0].horizon.name, 'mu'))
        self.assertEqual(points[0].horizon.age, 26,
                         "Wrong age for stratigraphic unit ({}) of first point. Should be {}". \
                         format(points[0].horizon.age, 26))

    def test_loading(self):
        # type: () -> None
        """
        Test the loading functions of the GeoPoint class
        /1/ load all from database
        /2/ load by name
        /3/ load in extent

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """

        # /1/ load all from database
        points = GeoPoint.load_all_from_db(self.session)
        pnts_count = len(self.points)
        for line in self.lines:
            pnts_count += len(line['points'])

        # 2 points have been automatically deleted and the lines will be closed
        pnts_count -= 2
        self.assertEqual(len(points), pnts_count,
                         "Wrong point count ({}). Should be {}.".format(len(points), pnts_count))
        self.assertEqual(points[0].id, 1, "First point should have id {}, but has {}.".format(1, points[0].id))
        self.assertTrue(math.fabs(float(points[-1].easting) - 1191579.1097525698) < float_precision,
                        "Wrong easting difference to large ( |{} - {}| = {} > {}).". \
                        format(float(points[-1].easting), 1191579.1097525698,
                               math.fabs(float(points[-1].easting) - 1191579.1097525698), float_precision))
        self.assertTrue(math.fabs(float(points[-1].northing) - 691044.6091080031) < float_precision,
                        "Wrong northing difference to large ( |{} - {}| = {} > {}).". \
                        format(float(points[-1].northing), 691044.6091080031,
                               math.fabs(float(points[-1].northing) - 691044.6091080031), float_precision))
        del points

        points = GeoPoint.load_all_without_lines_from_db(self.session)
        pnts_count = len(self.points)  # only points which doesn't belong to a line are loaded
        self.assertEqual(len(points), pnts_count,
                         "Wrong point count ({}). Should be {}.".format(len(points), pnts_count))
        self.assertEqual(points[0].id, 1, "First point should have id {}, but has {}.".format(1, points[0].id))
        self.assertTrue(math.fabs(float(points[-1].easting) - 1273456) < float_precision,
                        "Wrong easting difference to large ( |{} - {}| = {} > {}).". \
                        format(float(points[-1].easting), 1273456,
                               math.fabs(float(points[-1].easting) - 1273456), float_precision))
        self.assertTrue(math.fabs(float(points[-1].northing) - 5449672) < float_precision,
                        "Wrong northing difference to large ( |{} - {}| = {} > {}).". \
                        format(float(points[-1].northing), 5449672,
                               math.fabs(float(points[-1].northing) - 5449672), float_precision))
        self.assertEqual(points[-1].horizon.name, 'mu',
                         "Wrong horizon ({}). Should be {}.".format(points[-1].horizon.name, 'mu'))
        del points

        # /2/ load by name
        points = GeoPoint.load_by_name_from_db('', self.session)

        pnts_count = len(self.points)
        # Added line name as points set name, so we have to comment the line points out...
        # for line in self.lines:
        #    pnts_count += len(line['points'])

        # 2 points will be automatically deleted and the lines will be closed
        # pnts_count -= 2

        # 2 points have another name (obviously they have a name)
        pnts_count -= 2

        self.assertEqual(len(points), pnts_count,
                         "Wrong point count ({}). Should be {}.".format(len(points), pnts_count))
        self.assertEqual(points[0].id, 1, "First point should have id {}, but has {}.".format(1, points[0].id))
        self.assertTrue(math.fabs(float(points[-1].easting) - 1254367) < float_precision,
                        "Wrong easting difference to large ( |{} - {}| = {} > {}).". \
                        format(float(points[-1].easting), 1254367,
                               math.fabs(float(points[-1].easting) - 1254367), float_precision))
        self.assertTrue(math.fabs(float(points[-1].northing) - 5443636) < float_precision,
                        "Wrong northing difference to large ( |{} - {}| = {} > {}).". \
                        format(float(points[-1].northing), 5443636,
                               math.fabs(float(points[-1].northing) - 5443636), float_precision))
        del points

        points = GeoPoint.load_by_name_without_lines_from_db('', self.session)

        pnts_count = len(self.points)
        # 2 points have another name (obviously they have a name)
        pnts_count -= 2

        self.assertEqual(len(points), pnts_count,
                         "Wrong point count ({}). Should be {}.".format(len(points), pnts_count))
        self.assertEqual(points[0].id, 1, "First point should have id {}, but has {}.".format(1, points[0].id))
        self.assertTrue(math.fabs(float(points[-1].easting) - 1254367) < float_precision,
                        "Wrong easting difference to large ( |{} - {}| = {} > {}).". \
                        format(float(points[-1].easting), 1254367,
                               math.fabs(float(points[-1].easting) - 1254367), float_precision))
        self.assertTrue(math.fabs(float(points[-1].northing) - 5443636) < float_precision,
                        "Wrong northing difference to large ( |{} - {}| = {} > {}).". \
                        format(float(points[-1].northing), 5443636,
                               math.fabs(float(points[-1].northing) - 5443636), float_precision))
        self.assertEqual(points[-1].horizon.name, 'so',
                         "Wrong horizon ({}). Should be {}.".format(points[-1].horizon.name, 'so'))
        del points

        # /3/ load points in given extent
        # x -> 1174000 - 1200000
        # y ->  613500 -  651000
        # should return points of 2 lines with line-ids 2 (all points) and 4 (1 point)
        points = GeoPoint.load_in_extent_from_db(self.session, 1174000, 1200000, 613500, 651000)

        self.assertEqual(len(points), 5, "Wrong number of points ({}), should be {}".format(len(points), 5))

        self.assertTrue(math.fabs(float(points[0].easting) - 1179553.6811741155) < float_precision,
                        "Wrong easting difference to large ( |{} - {}| = {} > {}).". \
                        format(float(points[0].easting), 1179553.6811741155,
                               math.fabs(float(points[0].easting) - 1179553.6811741155), float_precision))
        self.assertTrue(math.fabs(float(points[0].northing) - 647105.5431482664) < float_precision,
                        "Wrong northing difference to large ( |{} - {}| = {} > {}).". \
                        format(float(points[0].northing), 647105.5431482664,
                               math.fabs(float(points[0].northing) - 647105.5431482664), float_precision))
        self.assertEqual(points[0].horizon.name, 'so',
                         "Wrong horizon ({}). Should be {}.".format(points[-1].horizon.name, 'so'))

        del points

        points = GeoPoint.load_in_extent_without_lines_from_db(self.session, 0, 1, 0, 1)
        self.assertEqual(len(points), 0, "Wrong number of points ({}), should be {}".format(len(points), 0))

        del points

    def test_setter_and_getter(self):
        # type: () -> None
        """
        Test the setter and getter functions of class GeoPoint

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        # points = GeoPoint.load_all_from_db(self.session)
        points = GeoPoint.load_all_without_lines_from_db(self.session)
        self.assertEqual(len(points), len(self.points),
                         "Wrong point length ({}). Should be {}.".format(len(points), len(self.points)))
        points[0].easting = 1
        points[1].northing = 2
        points[2].altitude = 3
        points[2].use_z()
        points[3].horizon = StratigraphicObject.init_stratigraphy(self.session, 'so', 10, False)
        points[0].name = 'point set name'
        points[1].del_z()

        for point in points:
            point.save_to_db()

        del points
        points = GeoPoint.load_all_without_lines_from_db(self.session)
        self.assertEqual(len(points), len(self.points),
                         "Wrong point length ({}). Should be {}.".format(len(points), len(self.points)))
        self.assertEqual(points[0].easting, 1, "Wrong easting value ({}). Should be {}.".format(points[0].easting, 1))
        self.assertEqual(points[1].northing, 2,
                         "Wrong northing value ({}). Should be {}.".format(points[1].northing, 2))
        self.assertEqual(points[2].altitude, 3,
                         "Wrong altitude value ({}). Should be {}.".format(points[2].altitude, 3))
        self.assertTrue(points[2].has_z, "Third point has no z-value...")  # Third point got z-value
        self.assertEqual(points[3].horizon.name, 'so',
                         "Wrong horizon ({}). Should be {}.".format(points[3].horizon.name, 'so'))
        self.assertEqual(points[0].name, 'point set name',
                         "Wrong point name ({}). Should be {}.".format(points[0].name, 'point set name'))
        self.assertFalse(points[1].has_z, "Second point has a z-value...")
        self.assertEqual(points[1].altitude, 0,
                         "Wrong altitude value ({}). Should be {}.".format(points[1].altitude, 0))

    def test_add_and_delete_properties(self):
        # type: () -> None
        """
        Test the add_property and delete_property function

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        point = GeoPoint.load_all_from_db(self.session)[0]
        prop = Property('test prop', 'test unit', self.session)
        point.add_property(prop)
        prop = Property('test prop 2', 'test unit 2', self.session)
        point.add_property(prop)

        self.assertRaises(TypeError, point.add_property, 'string')

        del point
        del prop

        point = GeoPoint.load_all_from_db(self.session)[0]
        self.assertEqual(2, len(point.properties))
        self.assertEqual('test prop', point.properties[0].property_name)
        self.assertEqual('test prop 2', point.properties[1].property_name)
        self.assertEqual('test unit', point.properties[0].property_unit)
        self.assertEqual('test unit 2', point.properties[1].property_unit)
        self.assertTrue(point.has_property('test prop 2'))
        self.assertEqual('test unit 2', point.get_property('test prop 2').property_unit)

        prop = point.properties[0]
        point.delete_property(prop)
        self.assertRaises(TypeError, point.delete_property, 'string')
        self.assertRaises(ValueError, point.delete_property, prop)
        self.assertEqual(1, len(point.properties))
        self.assertEqual('test prop 2', point.properties[0].property_name)
        self.assertEqual('test unit 2', point.properties[0].property_unit)

        del point

        point = GeoPoint.load_all_from_db(self.session)[0]
        self.assertEqual(1, len(point.properties))
        self.assertEqual('test prop 2', point.properties[0].property_name)
        self.assertEqual('test unit 2', point.properties[0].property_unit)

    def tearDown(self):
        # type: () -> None
        """
        Empty function, nothing to shutdown after the testing process

        :return: Nothing
        """
        pass


if __name__ == '__main__':
    unittest.main()
