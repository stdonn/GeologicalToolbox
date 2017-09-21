# -*- coding: UTF-8 -*-

import os
import sys

from osgeo import ogr, osr, gdal

from Resources.DBHandler import DBHandler
from Resources.Geometries import GeoPoint, Line
from Resources.Stratigraphy import Stratigraphy


def addData(session):
	lines = [
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

	for line in lines:
		points = list()
		for point in line['points']:
			points.append(GeoPoint(point[0], point[1], None, None, session, ""))
		newLine = Line(line['closed'], session, Stratigraphy(session, line['horizon'], line['age'], line['update']),
		               points, line['name'])
		newLine.save_to_db()


def main():
	handler = DBHandler(
			connection='sqlite:////Users/stephan/Documents/work/Dissertation/GIS/Modelling-Toolbox/data.db',
			debug=False)
	# handler = DBHandler(connection='sqlite:///D:\\data.db', debug=False)
	session = handler.get_session()

	# addData(session)

	# First: Use Exceptions in case of failures!
	gdal.UseExceptions()

	fileName = "/Users/stephan/Documents/work/Dissertation/GIS/Modelling-Toolbox/shapes/lines.shp"
	boundary = "/Users/stephan/Documents/work/Dissertation/GIS/Modelling-Toolbox/shapes/Boundary.shp"
	driver = ogr.GetDriverByName("ESRI Shapefile")
	if os.path.exists(fileName):
		driver.DeleteDataSource(fileName)

	if not os.path.exists(boundary):
		raise IOError("file <{}> not found!".format(boundary))

	try:
		in_shape = driver.Open(boundary, 0)
	except Exception, e:
		print(e)
		sys.exit()

	extent = in_shape.GetLayer().GetExtent()

	# print("Extend: {}".format(str(layer.GetExtent())))
	# for feature in layer:
	#	geom = feature.GetGeometryRef()
	#	print geom.ExportToWkt()

	# clean close
	del in_shape

	# get lines from the db
	lines = Line.load_in_extent_from_db(session, extent[0], extent[1], extent[2], extent[3])

	# create the data source
	data_source = driver.CreateDataSource(fileName)

	# create the spatial reference, WGS84 -- !!! NOT APPLICABLE HERE !!!
	srs = osr.SpatialReference()
	# srs.ImportFromEPSG(4326)

	layer = data_source.CreateLayer("TestLayer", srs, ogr.wkbLineString)

	# Add the fields we're interested in
	field_name = ogr.FieldDefn("Name", ogr.OFTString)
	field_name.SetWidth(100)
	layer.CreateField(field_name)
	field_region = ogr.FieldDefn("Horizon", ogr.OFTString)
	field_region.SetWidth(50)
	layer.CreateField(field_region)
	layer.CreateField(ogr.FieldDefn("Age", ogr.OFTInteger))
	layer.CreateField(ogr.FieldDefn("Closed", ogr.OFTBinary))

	# Process the text file and add the attributes and features to the shapefile
	for line in lines:
		# create the feature
		feature = ogr.Feature(layer.GetLayerDefn())
		# Set the attributes using the values from the delimited text file
		feature.SetField("Name", line.name)
		feature.SetField("Horizon", line.horizon.horizon)
		feature.SetField("Age", line.horizon.horizon_age)
		feature.SetField("Closed", line.closed)

		newLine = ogr.Geometry(ogr.wkbLinearRing)
		for point in line.points:
			newLine.AddPoint(float(point.easting), float(point.northing))

		if line.closed:
			newLine.AddPoint(float(line.points[0].easting), float(line.points[0].northing))

		# Set the feature geometry using the point
		feature.SetGeometry(newLine)
		# Create the feature in the layer (shapefile)
		layer.CreateFeature(feature)
	# Dereference the feature
	# feature = None

	# Save and close the data source
	# data_source = None


if __name__ == '__main__':
	main()
