"""
This module defines constants which are used in the API.
"""

# precision for float comparison
float_precision = 0.001  # 1 mm

# standard reference system
standard_reference_system = u"PROJCS['DHDN_3_Degree_Gauss_Zone_4'," + \
                             u"GEOGCS['GCS_Deutsches_Hauptdreiecksnetz'," + \
                             u"DATUM['D_Deutsches_Hauptdreiecksnetz'," + \
                             u"SPHEROID['Bessel_1841',6377397.155,299.1528128]]," + \
                             u"PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]," + \
                             u"PROJECTION['Gauss_Kruger'],PARAMETER['False_Easting',4500000.0]," + \
                             u"PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',12.0]," + \
                             u"PARAMETER['Scale_Factor',1.0],PARAMETER['Latitude_Of_Origin',0.0]," + \
                             u"UNIT['Meter',1.0]];-1122500 -10001000 10000;-100000 10000;-100000 10000;" + \
                             u"0,001;0,001;0,001;IsHighPrecision"
