from sqlalchemy.exc import IntegrityError

from Resources.DBHandler import DBHandler
from Resources.GeoPoint import GeoPoint
from Resources.Stratigraphy import Stratigraphy

if __name__ == '__main__':
	handler = DBHandler(connection='sqlite:///D:\\data.db', debug=False)

	points = [{
		'easting' : 1234567.12,
		'northing': 3124235.23,
		'altitude': 132.32,
		'horizon' : 'mu',
		'age'     : 2
	}, {
		'easting' : 2342432.34,
		'northing': 2342317.65,
		'altitude': 342.12,
		'horizon' : 'so',
		'age'     : 1
	}, {
		'easting' : 3234123.98,
		'northing': 7654395.34,
		'altitude': 543.34,
		'horizon' : 'mm',
		'age'     : 3
	}
	]

	Points = [GeoPoint(easting=point['easting'], northing=point['northing'], altitude=point['altitude'],
	                   horizon=Stratigraphy(point['horizon'], point['age'])) for point in points]
	session = handler.getSession()
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
