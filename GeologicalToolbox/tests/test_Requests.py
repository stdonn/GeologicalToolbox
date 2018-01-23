# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.Geometries.Well and WellMarker classes using unittest
"""

import unittest

from GeologicalToolbox.DBHandler import DBHandler
from GeologicalToolbox.Requests import Requests
from GeologicalToolbox.Stratigraphy import StratigraphicObject
from GeologicalToolbox.Wells import WellMarker, Well


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
                'depth'     : 751.13,
                'marker'    : ((34, 'mu', 4, ''),
                               (234, 'so', 3, 'Comment 1'),
                               (345, 'Fault', 0, 'Comment 2'),
                               (635, 'mu', 4, 'Comment 3'),
                               (636, 'Fault', 0, ''),
                               (645, 'mu', 4, ''),
                               (665, 'Fault', 0, ''),
                               (699, 'so', 3, 'Comment 1'))
            }, {
                'name'      : 'Well_4',
                'short_name': 'W4',
                'comment'   : 'A fourth well',
                'east'      : 234,
                'north'     : 5645.45,
                'altitude'  : 234.63,
                'depth'     : 645.21,
                'marker'    : ((34, 'mu', 4, ''),
                               (65, 'so', 3, 'Comment 1'),
                               (70, 'Fault', 0, 'Comment 2'),
                               (85, 'so', 3, 'Comment 1'),
                               (105, 'mu', 4, ''),
                               (123, 'mu', 4, ''),
                               (201, 'so', 3, 'Comment 1'))
            }
        ]

        for well in self.wells:
            new_well = Well(well['name'], well['short_name'], well['depth'], 'spatial_reference_unknown', well['east'],
                            well['north'], well['altitude'], self.session, 'well_set', well['comment'])
            new_well.save_to_db()

            for mark in well['marker']:
                new_well.marker.append(WellMarker(mark[0],
                                                  StratigraphicObject.init_stratigraphy(self.session, mark[1], mark[2],
                                                                                        False),
                                                  self.session, well['name'], mark[3]))
                new_well.marker[-1].save_to_db()

    def test_well_markers_to_thickness(self):
        # type: () -> None
        """
        Tests the Requests.well_markers_to_thickness(...) function

        :return: Nothing
        :raises AssertionError: if a test fails
        """
        result = Requests.well_markers_to_thickness(self.session, 'mu', 'so', summarise_multiple=False,
                                                    use_faulted=False, fault_name='Fault', extent=None)

        self.assertEqual(len(result), 4)
        self.assertTrue(result[0].has_property('thickness'))
        self.assertFalse(result[0].has_property('faulted'))
        self.assertFalse(result[0].has_property('summarised'))
        self.assertEqual(result[0].get_property('thickness').value, 5)
        self.assertEqual(result[1].get_property('thickness').value, 200)
        self.assertEqual(result[2].get_property('thickness').value, 31)
        self.assertEqual(result[3].get_property('thickness').value, 78)
        self.assertEqual(result[0].easting, 1234.56)
        self.assertEqual(result[0].northing, 123.45)
        self.assertEqual(result[0].altitude, 10.5 - 10)
        self.assertEqual(result[0].name, 'Well_1')
        self.assertEqual(result[1].name, 'Well_3')
        self.assertEqual(result[2].name, 'Well_4')
        self.assertEqual(result[3].name, 'Well_4')

        del result

        result = Requests.well_markers_to_thickness(self.session, 'mu', 'so', summarise_multiple=False,
                                                    use_faulted=True, extent=None)
        self.assertEqual(len(result), 5)
        self.assertTrue(result[0].has_property('thickness'))
        self.assertTrue(result[0].has_property('faulted'))
        self.assertFalse(result[0].has_property('summarised'))
        self.assertEqual(result[0].get_property('thickness').value, 5)
        self.assertEqual(result[0].get_property('faulted').value, 0)
        self.assertEqual(result[1].get_property('thickness').value, 200)
        self.assertEqual(result[1].get_property('faulted').value, 0)
        self.assertEqual(result[2].get_property('thickness').value, 54)
        self.assertEqual(result[2].get_property('faulted').value, 1)
        self.assertEqual(result[3].get_property('thickness').value, 31)
        self.assertEqual(result[3].get_property('faulted').value, 0)
        self.assertEqual(result[4].get_property('thickness').value, 78)
        self.assertEqual(result[4].get_property('faulted').value, 0)
        self.assertEqual(result[0].name, 'Well_1')
        self.assertEqual(result[1].easting, 3454.34)
        self.assertEqual(result[1].northing, 2340.22)
        self.assertEqual(result[1].altitude, 342.20 - 34)
        self.assertEqual(result[1].name, 'Well_3')
        self.assertEqual(result[2].altitude, 342.20 - 645)
        self.assertEqual(result[2].name, 'Well_3')
        self.assertEqual(result[3].name, 'Well_4')
        self.assertEqual(result[4].name, 'Well_4')

        del result

        result = Requests.well_markers_to_thickness(self.session, 'mu', 'so', summarise_multiple=True,
                                                    use_faulted=False, fault_name='Fault', extent=None)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].has_property('thickness'))
        self.assertFalse(result[0].has_property('faulted'))
        self.assertTrue(result[0].has_property('summarised'))
        self.assertEqual(result[0].get_property('thickness').value, 5)
        self.assertEqual(result[0].get_property('summarised').value, 0)
        self.assertEqual(result[0].easting, 1234.56)
        self.assertEqual(result[0].northing, 123.45)
        self.assertEqual(result[0].altitude, 10.5 - 10)
        self.assertEqual(result[0].name, 'Well_1')

        del result

        result = Requests.well_markers_to_thickness(self.session, 'mu', 'so', summarise_multiple=True,
                                                    use_faulted=True, extent=None)
        self.assertEqual(len(result), 3)
        self.assertTrue(result[0].has_property('thickness'))
        self.assertTrue(result[0].has_property('faulted'))
        self.assertTrue(result[0].has_property('summarised'))
        self.assertEqual(result[0].get_property('thickness').value, 5)
        self.assertEqual(result[0].get_property('faulted').value, 0)
        self.assertEqual(result[0].get_property('summarised').value, 0)
        self.assertEqual(result[1].get_property('thickness').value, 665)
        self.assertEqual(result[1].get_property('faulted').value, 1)
        self.assertEqual(result[1].get_property('summarised').value, 1)
        self.assertEqual(result[2].get_property('thickness').value, 167)
        self.assertEqual(result[2].get_property('faulted').value, 1)
        self.assertEqual(result[2].get_property('summarised').value, 1)
        self.assertEqual(result[0].name, 'Well_1')
        self.assertEqual(result[1].name, 'Well_3')
        self.assertEqual(result[2].name, 'Well_4')
        self.assertEqual(result[2].easting, 234)
        self.assertEqual(result[2].northing, 5645.45)
        self.assertEqual(result[2].altitude, 234.63 - 34)

        del result

        extent = [1000, 1500, 0, 3000]  # Well_1 and Well_2, 1 marker from Well_1
        result = Requests.well_markers_to_thickness(self.session, 'mu', 'so', summarise_multiple=True,
                                                    use_faulted=True, extent=extent)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Well_1')

        del result

        extent = [1000, 1500, 2000, 3000]  # only Well_2, no marker
        result = Requests.well_markers_to_thickness(self.session, 'mu', 'so', summarise_multiple=True,
                                                    use_faulted=True, extent=extent)
        self.assertEqual(len(result), 0)

        del result

        extent = [0, 500, 5000, 6000]  # only Well_4
        result = Requests.well_markers_to_thickness(self.session, 'mu', 'so', summarise_multiple=False,
                                                    use_faulted=True, extent=extent)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, 'Well_4')
        self.assertTrue(result[0].has_property('thickness'))
        self.assertEqual(result[0].get_property('thickness').value, 31)
        self.assertEqual(result[1].name, 'Well_4')
        self.assertTrue(result[1].has_property('thickness'))
        self.assertEqual(result[1].get_property('thickness').value, 78)

        del result

        # test failures and exceptions

        """
        :raises AttributeError: if marker_1 and marker_2 are equal
        :raises DatabaseException: if the database query results in less than 2 marker of a well_id
        :raises DatabaseRequestException: if an unexpected query result occurs
        :raises FaultException: if a fault is inside the section and use_faulted is False
        :raises TypeError: if session is not an instance of SQLAlchemy session
        :raises ValueError: if a parameter is not compatible with the required type
        """
        self.assertRaises(AttributeError, Requests.well_markers_to_thickness,
                          self.session, 'mu', 'mu', summarise_multiple=False, use_faulted=True, extent=None)
        self.assertRaises(TypeError, Requests.well_markers_to_thickness,
                          'wrong type', 'mu', 'so', summarise_multiple=False, use_faulted=True, extent=None)
        self.assertRaises(TypeError, Requests.well_markers_to_thickness,
                          self.session, 'mu', 'so', summarise_multiple=False, use_faulted=True, extent='ab')
        self.assertRaises(ValueError, Requests.well_markers_to_thickness,
                          self.session, 'mu', 'so', summarise_multiple=False, use_faulted=True, extent=[1,2,3])
        self.assertRaises(ValueError, Requests.well_markers_to_thickness,
                          self.session, 'mu', 'so', summarise_multiple=False, use_faulted=True, extent=[1, 2, 3, 'ab'])


if __name__ == '__main__':
    unittest.main()
