# -*- coding: UTF-8 -*-

from Resources.DBHandler import DBHandler
from Resources.Geometries import GeoPoint, Line
from Resources.Stratigraphy import Stratigraphy

if __name__ == '__main__':
	handler = DBHandler(
			connection='sqlite:////Users/stephan/Documents/work/Dissertation/GIS/Modelling-Toolbox/data.db',
			debug=False)
	# handler = DBHandler(connection='sqlite:///D:\\data.db', debug=False)
	session = handler.get_session()

	points = [
		{
			'east'   : 1234567.12,
			'north'  : 3124235.23,
			'alt'    : 132.32,
			'horizon': 'mu',
			'age'    : 2
		}, {
			'east'   : 2342432.34,
			'north'  : 2342317.65,
			'alt'    : 342.12,
			'horizon': 'so',
			'age'    : 1
		}, {
			'east'   : 3234123.98,
			'north'  : 7654395.34,
			'alt'    : 543.34,
			'horizon': 'mm',
			'age'    : 3
		}
	]

	#points = [GeoPoint(easting=point['east'], northing=point['north'], altitude=point['alt'],
	#                   horizon=Stratigraphy(session, point['horizon'], point['age']), session=session) for point in points]

	points = [GeoPoint(easting=point['east'], northing=point['north'], altitude=point['alt'],
	                   horizon=None, session=session) for point in points]

	line = Line(closed=True, session=session, horizon=Stratigraphy(session=session, name="so", age=1), points=points)

	print("Line before db insert:\n{}".format(str(line)))

	line.save_to_db()

	print("Line after db insert:\n{}".format(str(line)))

	line.points[1].easting = 1010101.01
	line.points[1].horizon = Stratigraphy(session=session, name="mu", age=2)

	line.save_to_db()

	print("Line after db update:\n{}".format(str(line)))
