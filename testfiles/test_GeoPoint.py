# -*- coding: UTF-8 -*-

from sqlalchemy.exc import IntegrityError

from Resources.DBHandler import DBHandler
from Resources.Geometries import GeoPoint
from Resources.Stratigraphy import Stratigraphy

if __name__ == '__main__':
	handler = DBHandler(
			connection='sqlite:////Users/stephan/Documents/work/Dissertation/GIS/Modelling-Toolbox/data.db',
			debug=False)
	# handler = DBHandler(connection='sqlite:///D:\\data.db', debug=False)
	session = handler.get_session()

	points = [
		{
			'east' : 1234567.12,
			'north': 3124235.23,
			'alt': 132.32,
			'horizon' : 'mo',
			'age'     : 4
		}, {
			'east' : 2342432.34,
			'north': 2342317.65,
			'alt': 342.12,
			'horizon' : 'su',
			'age'     : 5
		}, {
			'east' : 3234123.98,
			'north': 7654395.34,
			'alt': 543.34,
			'horizon' : 'ku',
			'age'     : 6
		}
	]

	Points = [GeoPoint(easting=point['east'], northing=point['north'], altitude=point['alt'],
	                   horizon=Stratigraphy(point['horizon'], point['age']), session=session) for point in points]
	session.add_all(Points)

	try:
		session.commit()
	except IntegrityError as e:
		print('Cannot commit changes:')
		print(str(e))
		print('Rolling back changes!')
		session.rollback()

	print(Points[1].altitude)
	Points[1].altitude = 123.43