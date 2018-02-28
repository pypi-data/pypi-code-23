import sys
import os
import ctypes
from ctypes import c_long, c_double, POINTER, c_int, Structure, c_char

_libraries = {}
dllname = ['geotrans2-32.dll', 'geotrans2-64.dll']['AMD64' in sys.version]
dllname = os.path.join(os.path.dirname(__file__), dllname)
# dllname = (
#     r'c:\users\jaraco\projects\geotrans2.4.2\geotrans2\win\geotrans2.dll'
_libraries['geotrans2.dll'] = ctypes.CDLL(dllname)
STRING = ctypes.c_char_p


Albers_Equal_Area_Conic = 9
MSL_EGM84_10D_NS_Height = 5
Input = 0
Ten_Seconds = 3
Eckert6 = 16
USNG = 6
Mercator = 21
Bonne = 12
GEOREF = 1
Geoid_or_MSL_Height = 2
Van_der_Grinten = 34
Second = 4
Equidistant_Cylindrical = 17
Transverse_Cylindrical_Equal_Area = 32
Geodetic = 0
Orthographic = 27
GARS = 2
Stereographic = 31
Mollweide = 23
Tenth_of_Second = 5
Three_Param_Datum_Type = 0
Sinusoidal = 30
Local_Cartesian = 4
Hundredth_of_Second = 6
File = 0
MSL_EGM84_10D_BL_Height = 4
Cassini = 13
Thousandth_of_Second = 7
Azimuthal_Equidistant = 10
Polyconic = 29
Ten_Minutes = 1
Ellipsoid_Height = 1
Ten_Thousandth_of_Second = 8
WGS84_Datum = 2
MGRS = 5
Lambert_Conformal_Conic_2 = 20
WGS72_Datum_Type = 3
Degree = 0
WGS72_Datum = 3
MSL_EGM96_VG_NS_Height = 3
No_Height = 0
Three_Param_Datum = 0
Output = 1
Neys = 24
Minute = 2
Seven_Param_Datum_Type = 1
Oblique_Mercator = 26
Seven_Param_Datum = 1
UPS = 8
UTM = 7
WGS84_Datum_Type = 2
Gnomonic = 18
Transverse_Mercator = 33
Interactive = 1
Polar_Stereo = 28
Geocentric = 3
Miller_Cylindrical = 22
NZMG = 25
Lambert_Conformal_Conic_1 = 19
Eckert4 = 15
BNG = 11
Cylindrical_Equal_Area = 14
LAMBERT_2_ORIGIN_LAT_ERROR = 64  # Variable c_int '64'
BONN_EASTING_ERROR = 4  # Variable c_int '4'
EQCY_STDP_ERROR = 16  # Variable c_int '16'
ENGINE_DATUM_FILE_PARSE_ERROR = 256  # Variable c_int '256'
DATUM_3PARAM_FILE_OPEN_ERROR = 16  # Variable c_int '16'
ALBERS_INV_F_ERROR = 128  # Variable c_int '128'
OMERC_LON2_ERROR = 64  # Variable c_int '64'
ORTH_LAT_ERROR = 1  # Variable c_int '1'
ENGINE_LON_ERROR = 536870912  # Variable c_int '536870912'
USNG_NO_ERROR = 0  # Variable c_int '0'
MGRS_EASTING_ERROR = 64  # Variable c_int '64'
TCEA_LON_WARNING = 512  # Variable c_int '512'
AZEQ_NORTHING_ERROR = 8  # Variable c_int '8'
BNG_ELLIPSOID_ERROR = 64  # Variable c_int '64'
TCEA_NO_ERROR = 0  # Variable c_int '0'
BONN_LON_ERROR = 2  # Variable c_int '2'
MOLL_LAT_ERROR = 1  # Variable c_int '1'
NEYS_FIRST_STDP_ERROR = 16  # Variable c_int '16'
RETURN_MSG_LENGTH = 256  # Variable c_int '256'
ELLIPSE_INVALID_INDEX_ERROR = 16  # Variable c_int '16'
AZEQ_EASTING_ERROR = 4  # Variable c_int '4'
MGRS_NO_ERROR = 0  # Variable c_int '0'
DATUM_CODE_LENGTH = 7  # Variable c_int '7'
GARS_STR_15_MIN_ERROR = 32  # Variable c_int '32'
GEOREF_LON_ERROR = 2  # Variable c_int '2'
ENGINE_STR_LAT_MIN_ERROR = 262144  # Variable c_int '262144'
GNOM_INV_F_ERROR = 128  # Variable c_int '128'
GEOID_NOT_INITIALIZED_ERROR = 4  # Variable c_int '4'
CYEQ_ORIGIN_LAT_ERROR = 16  # Variable c_int '16'
MILL_CENT_MER_ERROR = 32  # Variable c_int '32'
TRANMERC_SCALE_FACTOR_ERROR = 256  # Variable c_int '256'
ELLIPSE_TABLE_OVERFLOW_ERROR = 4  # Variable c_int '4'
UPS_A_ERROR = 32  # Variable c_int '32'
LAMBERT_1_A_ERROR = 128  # Variable c_int '128'
GRIN_NO_ERROR = 0  # Variable c_int '0'
ELLIPSE_INV_F_ERROR = 128  # Variable c_int '128'
MILL_EASTING_ERROR = 4  # Variable c_int '4'
MGRS_LON_ERROR = 2  # Variable c_int '2'
USNG_INV_F_ERROR = 32  # Variable c_int '32'
DATUM_7PARAM_FILE_OPEN_ERROR = 2  # Variable c_int '2'
BONN_INV_F_ERROR = 128  # Variable c_int '128'
ALBERS_A_ERROR = 64  # Variable c_int '64'
CYEQ_INV_F_ERROR = 128  # Variable c_int '128'
BONN_NORTHING_ERROR = 8  # Variable c_int '8'
GEOREF_STR_LAT_ERROR = 8  # Variable c_int '8'
CASS_LON_ERROR = 2  # Variable c_int '2'
BNG_LAT_ERROR = 1  # Variable c_int '1'
OMERC_NORTHING_ERROR = 1024  # Variable c_int '1024'
ELLIPSE_NO_ERROR = 0  # Variable c_int '0'
MOLL_NO_ERROR = 0  # Variable c_int '0'
MOLL_INV_F_ERROR = 128  # Variable c_int '128'
STEREO_LAT_ERROR = 1  # Variable c_int '1'
ELLIPSE_FILE_OPEN_ERROR = 1  # Variable c_int '1'
DATUM_LAT_ERROR = 2048  # Variable c_int '2048'
EQCY_INV_F_ERROR = 128  # Variable c_int '128'
BNG_NORTHING_ERROR = 8  # Variable c_int '8'
ORTH_RADIUS_ERROR = 256  # Variable c_int '256'
ENGINE_LON2_ERROR = 16777216  # Variable c_int '16777216'
LAMBERT_2_SCALE_FACTOR_ERROR = 4096  # Variable c_int '4096'
ALBERS_EASTING_ERROR = 4  # Variable c_int '4'
ENGINE_A_ERROR = 1073741824  # Variable c_int '1073741824'
ECK4_A_ERROR = 64  # Variable c_int '64'
OMERC_SCALE_FACTOR_ERROR = 8192  # Variable c_int '8192'
RED = 0  # Variable c_int '0'
ENGINE_NORTHING_ERROR = 8  # Variable c_int '8'
USNG_LAT_WARNING = 1024  # Variable c_int '1024'
NZMG_EASTING_ERROR = 4  # Variable c_int '4'
ALBERS_LAT_ERROR = 1  # Variable c_int '1'
GARS_STR_LON_ERROR = 16  # Variable c_int '16'
GEOID_FILE_OPEN_ERROR = 1  # Variable c_int '1'
AZEQ_PROJECTION_ERROR = 256  # Variable c_int '256'
OMERC_LON1_ERROR = 32  # Variable c_int '32'
NEYS_NORTHING_ERROR = 8  # Variable c_int '8'
TCEA_LAT_ERROR = 1  # Variable c_int '1'
ENGINE_INVALID_CODE_ERROR = 16384  # Variable c_int '16384'
ALBERS_CENT_MER_ERROR = 32  # Variable c_int '32'
CYEQ_NORTHING_ERROR = 8  # Variable c_int '8'
GRIN_EASTING_ERROR = 4  # Variable c_int '4'
GEOCENT_A_ERROR = 4  # Variable c_int '4'
DATUM_INVALID_SRC_INDEX_ERROR = 256  # Variable c_int '256'
GARS_PRECISION_ERROR = 128  # Variable c_int '128'
ELLIPSE_NOT_INITIALIZED_ERROR = 8  # Variable c_int '8'
DATUM_LON_ERROR = 4096  # Variable c_int '4096'
GREEN = 2  # Variable c_int '2'
CYEQ_LAT_ERROR = 1  # Variable c_int '1'
CASS_INV_F_ERROR = 128  # Variable c_int '128'
MERC_LAT_ERROR = 1  # Variable c_int '1'
ENGINE_ORIGIN_LAT_ERROR = 1  # Variable c_int '1'
OMERC_A_ERROR = 2048  # Variable c_int '2048'
NZMG_ELLIPSOID_ERROR = 16  # Variable c_int '16'
DATUM_ELLIPSE_ERROR = 32768  # Variable c_int '32768'
ENGINE_ELLIPSOID_OVERFLOW = 32768  # Variable c_int '32768'
ENGINE_INVALID_DIRECTION = 2048  # Variable c_int '2048'
AZEQ_ORIGIN_LAT_ERROR = 16  # Variable c_int '16'
EQCY_NORTHING_ERROR = 8  # Variable c_int '8'
ALBERS_FIRST_STDP_ERROR = 256  # Variable c_int '256'
LOCCART_ORIENTATION_ERROR = 64  # Variable c_int '64'
MGRS_ZONE_ERROR = 256  # Variable c_int '256'
SINU_NORTHING_ERROR = 8  # Variable c_int '8'
ENGINE_NOT_USERDEF_ERROR = 1048576  # Variable c_int '1048576'
ECK6_CENT_MER_ERROR = 32  # Variable c_int '32'
ELLIPSE_INITIALIZE_ERROR = 2  # Variable c_int '2'
GARS_LAT_ERROR = 1  # Variable c_int '1'
ELLIPSE_IN_USE_ERROR = 256  # Variable c_int '256'
TCEA_INV_F_ERROR = 128  # Variable c_int '128'
NZMG_NO_ERROR = 0  # Variable c_int '0'
ECK4_LON_ERROR = 2  # Variable c_int '2'
TCEA_LON_ERROR = 2  # Variable c_int '2'
POLY_INV_F_ERROR = 128  # Variable c_int '128'
NEYS_LON_ERROR = 2  # Variable c_int '2'
EQCY_EASTING_ERROR = 4  # Variable c_int '4'
GEOREF_NO_ERROR = 0  # Variable c_int '0'
USNG_ZONE_ERROR = 256  # Variable c_int '256'
DATUM_SCALE_ERROR = 262144  # Variable c_int '262144'
BONN_CENT_MER_ERROR = 32  # Variable c_int '32'
UTM_A_ERROR = 128  # Variable c_int '128'
NEYS_INV_F_ERROR = 256  # Variable c_int '256'
GARS_STR_5_MIN_ERROR = 64  # Variable c_int '64'
GNOM_LAT_ERROR = 1  # Variable c_int '1'
POLAR_INV_F_ERROR = 128  # Variable c_int '128'
GRIN_CENT_MER_ERROR = 32  # Variable c_int '32'
UTM_INV_F_ERROR = 256  # Variable c_int '256'
ENGINE_INPUT_WARNING = 1  # Variable c_int '1'
MERC_NO_ERROR = 0  # Variable c_int '0'
ENGINE_OUTPUT_WARNING = 4  # Variable c_int '4'
OMERC_INV_F_ERROR = 4096  # Variable c_int '4096'
CYEQ_NO_ERROR = 0  # Variable c_int '0'
DATUM_3PARAM_FILE_PARSING_ERROR = 32  # Variable c_int '32'
POLY_LON_WARNING = 256  # Variable c_int '256'
USNG_LAT_ERROR = 1  # Variable c_int '1'
POLAR_LAT_ERROR = 1  # Variable c_int '1'
DATUM_NAME_LENGTH = 33  # Variable c_int '33'
POLAR_A_ERROR = 64  # Variable c_int '64'
OMERC_LAT2_ERROR = 16  # Variable c_int '16'
UTM_ZONE_ERROR = 16  # Variable c_int '16'
UPS_INV_F_ERROR = 64  # Variable c_int '64'
ENGINE_STRING_ERROR = 65536  # Variable c_int '65536'
ELLIPSE_NOT_USERDEF_ERROR = 512  # Variable c_int '512'
MERC_A_ERROR = 64  # Variable c_int '64'
TCEA_ORIGIN_LAT_ERROR = 16  # Variable c_int '16'
ENGINE_LAT1_ERROR = 2097152  # Variable c_int '2097152'
LAMBERT_2_LON_ERROR = 2  # Variable c_int '2'
UTM_HEMISPHERE_ERROR = 32  # Variable c_int '32'
CYEQ_CENT_MER_ERROR = 32  # Variable c_int '32'
MOLL_A_ERROR = 64  # Variable c_int '64'
POLY_EASTING_ERROR = 4  # Variable c_int '4'
AZEQ_LON_ERROR = 2  # Variable c_int '2'
GARS_NO_ERROR = 0  # Variable c_int '0'
POLAR_NORTHING_ERROR = 32  # Variable c_int '32'
GARS_STR_LAT_ERROR = 8  # Variable c_int '8'
OMERC_ORIGIN_LAT_ERROR = 4  # Variable c_int '4'
DATUM_NO_ERROR = 0  # Variable c_int '0'
OMERC_LON_WARNING = 16384  # Variable c_int '16384'
DATUM_NOT_USERDEF_ERROR = 65536  # Variable c_int '65536'
ENGINE_INVALID_TYPE = 1024  # Variable c_int '1024'
MOLL_LON_ERROR = 2  # Variable c_int '2'
AZEQ_CENT_MER_ERROR = 32  # Variable c_int '32'
SINU_INV_F_ERROR = 128  # Variable c_int '128'
AZEQ_LAT_ERROR = 1  # Variable c_int '1'
BNG_INVALID_AREA_ERROR = 16  # Variable c_int '16'
ENGINE_DATUM_DOMAIN_ERROR = 262144  # Variable c_int '262144'
LAMBERT_2_FIRST_STDP_ERROR = 16  # Variable c_int '16'
TCEA_NORTHING_ERROR = 8  # Variable c_int '8'
MOLL_NORTHING_ERROR = 8  # Variable c_int '8'
POLY_A_ERROR = 64  # Variable c_int '64'
ENGINE_OUTPUT_ERROR = 8  # Variable c_int '8'
CYEQ_LON_ERROR = 2  # Variable c_int '2'
GRIN_A_ERROR = 64  # Variable c_int '64'
LOCCART_INV_F_ERROR = 8  # Variable c_int '8'
TCEA_EASTING_ERROR = 4  # Variable c_int '4'
ENGINE_ELLIPSE_IN_USE_ERROR = 524288  # Variable c_int '524288'
ELLIPSE_INVALID_CODE_ERROR = 32  # Variable c_int '32'
LAMBERT_1_EASTING_ERROR = 4  # Variable c_int '4'
NEYS_NO_ERROR = 0  # Variable c_int '0'
ENGINE_ZONE_ERROR = 16384  # Variable c_int '16384'
LAMBERT_2_INV_F_ERROR = 512  # Variable c_int '512'
MERC_EASTING_ERROR = 4  # Variable c_int '4'
MERC_INV_F_ERROR = 128  # Variable c_int '128'
TRANMERC_CENT_MER_ERROR = 32  # Variable c_int '32'
GNOM_CENT_MER_ERROR = 32  # Variable c_int '32'
EQCY_LON_ERROR = 2  # Variable c_int '2'
MOLL_CENT_MER_ERROR = 32  # Variable c_int '32'
ELLIPSE_A_ERROR = 64  # Variable c_int '64'
NZMG_LAT_ERROR = 1  # Variable c_int '1'
DATUM_NOT_INITIALIZED_ERROR = 1  # Variable c_int '1'
ENGINE_SCALE_FACTOR_ERROR = 64  # Variable c_int '64'
ECK6_A_ERROR = 64  # Variable c_int '64'
MGRS_LAT_ERROR = 1  # Variable c_int '1'
ECK4_CENT_MER_ERROR = 32  # Variable c_int '32'
LAMBERT_1_NO_ERROR = 0  # Variable c_int '0'
GRIN_NORTHING_ERROR = 8  # Variable c_int '8'
POLY_CENT_MER_ERROR = 32  # Variable c_int '32'
BNG_STRING_ERROR = 32  # Variable c_int '32'
BONN_A_ERROR = 64  # Variable c_int '64'
ECK6_INV_F_ERROR = 128  # Variable c_int '128'
BNG_NO_ERROR = 0  # Variable c_int '0'
DATUM_INVALID_INDEX_ERROR = 128  # Variable c_int '128'
ORTH_ORIGIN_LAT_ERROR = 16  # Variable c_int '16'
UPS_EASTING_ERROR = 8  # Variable c_int '8'
GRIN_INV_F_ERROR = 128  # Variable c_int '128'
ALBERS_LON_ERROR = 2  # Variable c_int '2'
MGRS_A_ERROR = 16  # Variable c_int '16'
MGRS_NORTHING_ERROR = 128  # Variable c_int '128'
ORTH_EASTING_ERROR = 4  # Variable c_int '4'
POLY_NO_ERROR = 0  # Variable c_int '0'
LOCCART_A_ERROR = 4  # Variable c_int '4'
USNG_STRING_ERROR = 4  # Variable c_int '4'
DATUM_SIGMA_ERROR = 8192  # Variable c_int '8192'
DATUM_7PARAM_FILE_PARSING_ERROR = 4  # Variable c_int '4'
LAMBERT_2_NORTHING_ERROR = 8  # Variable c_int '8'
UTM_ZONE_OVERRIDE_ERROR = 64  # Variable c_int '64'
TRANMERC_LON_WARNING = 512  # Variable c_int '512'
MILL_LAT_ERROR = 1  # Variable c_int '1'
UTM_NO_ERROR = 0  # Variable c_int '0'
BONN_LAT_ERROR = 1  # Variable c_int '1'
ENGINE_GEOID_ERROR = 128  # Variable c_int '128'
ALBERS_FIRST_SECOND_ERROR = 1024  # Variable c_int '1024'
LAMBERT_2_EASTING_ERROR = 4  # Variable c_int '4'
ECK4_LAT_ERROR = 1  # Variable c_int '1'
OMERC_DIFF_HEMISPHERE_ERROR = 256  # Variable c_int '256'
GEOCENT_NO_ERROR = 0  # Variable c_int '0'
BNG_LON_ERROR = 2  # Variable c_int '2'
ORTH_NO_ERROR = 0  # Variable c_int '0'
ENGINE_LAT_ERROR = 268435456  # Variable c_int '268435456'
ORTH_NORTHING_ERROR = 8  # Variable c_int '8'
GEOREF_STR_LON_MIN_ERROR = 64  # Variable c_int '64'
LOCCART_LAT_ERROR = 1  # Variable c_int '1'
USNG_NORTHING_ERROR = 128  # Variable c_int '128'
EQCY_LAT_ERROR = 1  # Variable c_int '1'
TCEA_CENT_MER_ERROR = 32  # Variable c_int '32'
DATUM_INVALID_CODE_ERROR = 1024  # Variable c_int '1024'
LAMBERT_2_CENT_MER_ERROR = 128  # Variable c_int '128'
BNG_EASTING_ERROR = 4  # Variable c_int '4'
USNG_HEMISPHERE_ERROR = 512  # Variable c_int '512'
CASS_LAT_ERROR = 1  # Variable c_int '1'
MILL_LON_ERROR = 2  # Variable c_int '2'
CASS_NO_ERROR = 0  # Variable c_int '0'
ENGINE_GEOID_FILE_PARSE_ERROR = 512  # Variable c_int '512'
TRANMERC_EASTING_ERROR = 4  # Variable c_int '4'
LAMBERT_2_HEMISPHERE_ERROR = 1024  # Variable c_int '1024'
COORD_SYS_NAME_LENGTH = 50  # Variable c_int '50'
LAMBERT_1_LAT_ERROR = 1  # Variable c_int '1'
STEREO_NO_ERROR = 0  # Variable c_int '0'
GNOM_LON_ERROR = 2  # Variable c_int '2'
GEOCENT_LAT_ERROR = 1  # Variable c_int '1'
MERC_NORTHING_ERROR = 8  # Variable c_int '8'
CASS_ORIGIN_LAT_ERROR = 16  # Variable c_int '16'
CASS_EASTING_ERROR = 4  # Variable c_int '4'
STEREO_INV_F_ERROR = 128  # Variable c_int '128'
CASS_NORTHING_ERROR = 8  # Variable c_int '8'
UPS_HEMISPHERE_ERROR = 4  # Variable c_int '4'
CASS_CENT_MER_ERROR = 32  # Variable c_int '32'
ENGINE_PROJECTION_ERROR = 1048576  # Variable c_int '1048576'
SINU_EASTING_ERROR = 4  # Variable c_int '4'
ALBERS_SECOND_STDP_ERROR = 512  # Variable c_int '512'
LAMBERT_1_CENT_MER_ERROR = 32  # Variable c_int '32'
NEYS_LAT_ERROR = 1  # Variable c_int '1'
ENGINE_HEMISPHERE_ERROR = 32  # Variable c_int '32'
TRANMERC_NO_ERROR = 0  # Variable c_int '0'
LAMBERT_1_SCALE_FACTOR_ERROR = 64  # Variable c_int '64'
SINU_NO_ERROR = 0  # Variable c_int '0'
YELLOW = 1  # Variable c_int '1'
ORTH_INV_F_ERROR = 128  # Variable c_int '128'
ENGINE_FIRST_SECOND_ERROR = 8192  # Variable c_int '8192'
ECK4_NO_ERROR = 0  # Variable c_int '0'
GARS_STR_ERROR = 4  # Variable c_int '4'
COORD_SYS_CODE_LENGTH = 3  # Variable c_int '3'
MILL_NORTHING_ERROR = 8  # Variable c_int '8'
TCEA_SCALE_FACTOR_ERROR = 256  # Variable c_int '256'
ENGINE_ORIGIN_LON_ERROR = 512  # Variable c_int '512'
LAMBERT_1_NORTHING_ERROR = 8  # Variable c_int '8'
POLAR_NO_ERROR = 0  # Variable c_int '0'
ECK4_INV_F_ERROR = 128  # Variable c_int '128'
ENGINE_INVALID_INDEX_ERROR = 8192  # Variable c_int '8192'
GEOREF_STR_ERROR = 4  # Variable c_int '4'
ENGINE_LAT2_ERROR = 8388608  # Variable c_int '8388608'
ENGINE_DATUM_SIGMA_ERROR = 131072  # Variable c_int '131072'
ENGINE_ELLIPSOID_CODE_ERROR = 134217728  # Variable c_int '134217728'
MGRS_STRING_ERROR = 4  # Variable c_int '4'
GARS_LON_ERROR = 2  # Variable c_int '2'
NUMBER_COORD_SYS = 35  # Variable c_int '35'
OMERC_EASTING_ERROR = 512  # Variable c_int '512'
GEOID_NO_ERROR = 0  # Variable c_int '0'
ALBERS_NORTHING_ERROR = 8  # Variable c_int '8'
ENGINE_DATUM_WARNING = 1024  # Variable c_int '1024'
ENGINE_ELLIPSOID_ERROR = 32  # Variable c_int '32'
OMERC_LAT_ERROR = 1  # Variable c_int '1'
ENGINE_EASTING_ERROR = 4  # Variable c_int '4'
ALBERS_HEMISPHERE_ERROR = 2048  # Variable c_int '2048'
CASS_A_ERROR = 64  # Variable c_int '64'
MILL_A_ERROR = 64  # Variable c_int '64'
ENGINE_RADIUS_ERROR = 16  # Variable c_int '16'
LAMBERT_2_NO_ERROR = 0  # Variable c_int '0'
DATUM_DOMAIN_ERROR = 16384  # Variable c_int '16384'
LAMBERT_1_INV_F_ERROR = 256  # Variable c_int '256'
STEREO_EASTING_ERROR = 16  # Variable c_int '16'
ENGINE_DATUM_ERROR = 64  # Variable c_int '64'
ECK4_EASTING_ERROR = 4  # Variable c_int '4'
ENGINE_INVALID_AREA_ERROR = 67108864  # Variable c_int '67108864'
ENGINE_CENT_MER_ERROR = 2  # Variable c_int '2'
ALBERS_NO_ERROR = 0  # Variable c_int '0'
GNOM_EASTING_ERROR = 4  # Variable c_int '4'
OMERC_LAT1_LAT2_ERROR = 128  # Variable c_int '128'
ORTH_LON_ERROR = 2  # Variable c_int '2'
POLY_NORTHING_ERROR = 8  # Variable c_int '8'
STEREO_A_ERROR = 64  # Variable c_int '64'
LAMBERT_1_ORIGIN_LAT_ERROR = 16  # Variable c_int '16'
TRANMERC_NORTHING_ERROR = 8  # Variable c_int '8'
DATUM_INVALID_DEST_INDEX_ERROR = 512  # Variable c_int '512'
ORTH_CENT_MER_ERROR = 32  # Variable c_int '32'
TRANMERC_LON_ERROR = 2  # Variable c_int '2'
ENGINE_STDP_ERROR = 524288  # Variable c_int '524288'
ECK6_NO_ERROR = 0  # Variable c_int '0'
NZMG_LON_ERROR = 2  # Variable c_int '2'
USNG_LON_ERROR = 2  # Variable c_int '2'
GNOM_NORTHING_ERROR = 8  # Variable c_int '8'
GRIN_LAT_ERROR = 1  # Variable c_int '1'
MERC_LON_ERROR = 2  # Variable c_int '2'
POLY_ORIGIN_LAT_ERROR = 16  # Variable c_int '16'
TRANMERC_INV_F_ERROR = 128  # Variable c_int '128'
MGRS_HEMISPHERE_ERROR = 512  # Variable c_int '512'
LAMBERT_2_SECOND_STDP_ERROR = 32  # Variable c_int '32'
ELLIPSOID_CODE_LENGTH = 3  # Variable c_int '3'
USNG_EASTING_ERROR = 64  # Variable c_int '64'
USNG_PRECISION_ERROR = 8  # Variable c_int '8'
SINU_LAT_ERROR = 1  # Variable c_int '1'
TRANMERC_ORIGIN_LAT_ERROR = 16  # Variable c_int '16'
CONVERT_MSG_LENGTH = 2048  # Variable c_int '2048'
MGRS_INV_F_ERROR = 32  # Variable c_int '32'
GNOM_ORIGIN_LAT_ERROR = 16  # Variable c_int '16'
MGRS_LAT_WARNING = 1024  # Variable c_int '1024'
TCEA_A_ERROR = 64  # Variable c_int '64'
MILL_NO_ERROR = 0  # Variable c_int '0'
SINU_LON_ERROR = 2  # Variable c_int '2'
UPS_NORTHING_ERROR = 16  # Variable c_int '16'
MOLL_EASTING_ERROR = 4  # Variable c_int '4'
STEREO_NORTHING_ERROR = 32  # Variable c_int '32'
GNOM_NO_ERROR = 0  # Variable c_int '0'
ENGINE_NO_ERROR = 0  # Variable c_int '0'
STEREO_LON_ERROR = 2  # Variable c_int '2'
ENGINE_INPUT_ERROR = 2  # Variable c_int '2'
ENGINE_INVALID_STATE = 4096  # Variable c_int '4096'
ENGINE_SECOND_STDP_ERROR = 4096  # Variable c_int '4096'
EQCY_A_ERROR = 64  # Variable c_int '64'
ORTH_A_ERROR = 64  # Variable c_int '64'
BONN_NO_ERROR = 0  # Variable c_int '0'
GRIN_RADIUS_ERROR = 256  # Variable c_int '256'
AZEQ_A_ERROR = 64  # Variable c_int '64'
ELLIPSOID_NAME_LENGTH = 30  # Variable c_int '30'
STEREO_ORIGIN_LAT_ERROR = 4  # Variable c_int '4'
ENGINE_STR_LON_MIN_ERROR = 131072  # Variable c_int '131072'
DATUM_ROTATION_ERROR = 131072  # Variable c_int '131072'
OMERC_NO_ERROR = 0  # Variable c_int '0'
LAMBERT_2_LAT_ERROR = 1  # Variable c_int '1'
AZEQ_INV_F_ERROR = 128  # Variable c_int '128'
UTM_LON_ERROR = 2  # Variable c_int '2'
POLY_LON_ERROR = 2  # Variable c_int '2'
UTM_LAT_ERROR = 1  # Variable c_int '1'
OMERC_LON_ERROR = 2  # Variable c_int '2'
GEOID_LON_ERROR = 16  # Variable c_int '16'
NEYS_A_ERROR = 128  # Variable c_int '128'
NEYS_EASTING_ERROR = 4  # Variable c_int '4'
GEOREF_STR_LAT_MIN_ERROR = 32  # Variable c_int '32'
USNG_A_ERROR = 16  # Variable c_int '16'
LAMBERT_2_A_ERROR = 256  # Variable c_int '256'
AZEQ_NO_ERROR = 0  # Variable c_int '0'
UPS_LAT_ERROR = 1  # Variable c_int '1'
POLAR_ORIGIN_LAT_ERROR = 4  # Variable c_int '4'
GNOM_A_ERROR = 64  # Variable c_int '64'
LAMBERT_2_FIRST_SECOND_ERROR = 2048  # Variable c_int '2048'
TRANMERC_LAT_ERROR = 1  # Variable c_int '1'
POLAR_EASTING_ERROR = 16  # Variable c_int '16'
MGRS_PRECISION_ERROR = 8  # Variable c_int '8'
TRANMERC_A_ERROR = 64  # Variable c_int '64'
BONN_ORIGIN_LAT_ERROR = 16  # Variable c_int '16'
UPS_NO_ERROR = 0  # Variable c_int '0'
ECK4_NORTHING_ERROR = 8  # Variable c_int '8'
NEYS_ORIGIN_LAT_ERROR = 32  # Variable c_int '32'
GRIN_LON_ERROR = 2  # Variable c_int '2'
GEOCENT_LON_ERROR = 2  # Variable c_int '2'
ECK6_NORTHING_ERROR = 8  # Variable c_int '8'
GEOREF_PRECISION_ERROR = 128  # Variable c_int '128'
DATUM_3PARAM_OVERFLOW_ERROR = 64  # Variable c_int '64'
GEOID_LAT_ERROR = 8  # Variable c_int '8'
LOCCART_ORIGIN_LAT_ERROR = 16  # Variable c_int '16'
ENGINE_LON1_ERROR = 4194304  # Variable c_int '4194304'
ENGINE_DATUM_OVERFLOW = 65536  # Variable c_int '65536'
SINU_A_ERROR = 64  # Variable c_int '64'
CASS_LON_WARNING = 256  # Variable c_int '256'
POLAR_RADIUS_ERROR = 256  # Variable c_int '256'
ENGINE_LAT1_LAT2_ERROR = 33554432  # Variable c_int '33554432'
ENGINE_ZONE_OVERRIDE_ERROR = 32768  # Variable c_int '32768'
OMERC_LAT1_ERROR = 8  # Variable c_int '8'
EQCY_CENT_MER_ERROR = 32  # Variable c_int '32'
UPS_LON_ERROR = 2  # Variable c_int '2'
ENGINE_LAT_WARNING = 256  # Variable c_int '256'
LOCCART_LON_ERROR = 2  # Variable c_int '2'
NEYS_SCALE_FACTOR_ERROR = 512  # Variable c_int '512'
UTM_NORTHING_ERROR = 8  # Variable c_int '8'
POLAR_ORIGIN_LON_ERROR = 8  # Variable c_int '8'
LOCCART_ORIGIN_LON_ERROR = 32  # Variable c_int '32'
MERC_CENT_MER_ERROR = 32  # Variable c_int '32'
LAMBERT_1_LON_ERROR = 2  # Variable c_int '2'
CYEQ_EASTING_ERROR = 4  # Variable c_int '4'
CYEQ_A_ERROR = 64  # Variable c_int '64'
MILL_INV_F_ERROR = 128  # Variable c_int '128'
POLY_LAT_ERROR = 1  # Variable c_int '1'
GEOCENT_INV_F_ERROR = 8  # Variable c_int '8'
GEOREF_STR_LON_ERROR = 16  # Variable c_int '16'
ECK6_LON_ERROR = 2  # Variable c_int '2'
UTM_EASTING_ERROR = 4  # Variable c_int '4'
EQCY_NO_ERROR = 0  # Variable c_int '0'
ECK6_EASTING_ERROR = 4  # Variable c_int '4'
SINU_CENT_MER_ERROR = 32  # Variable c_int '32'
LOCCART_NO_ERROR = 0  # Variable c_int '0'
ENGINE_LON_WARNING = 128  # Variable c_int '128'
ENGINE_FIRST_STDP_ERROR = 2048  # Variable c_int '2048'
STEREO_CENT_MER_ERROR = 8  # Variable c_int '8'
ALBERS_ORIGIN_LAT_ERROR = 16  # Variable c_int '16'
NEYS_CENT_MER_ERROR = 64  # Variable c_int '64'
GEOID_INITIALIZE_ERROR = 2  # Variable c_int '2'
ENGINE_NOT_INITIALIZED = 16  # Variable c_int '16'
POLAR_LON_ERROR = 2  # Variable c_int '2'
MERC_LAT_OF_TRUE_SCALE_ERROR = 16  # Variable c_int '16'
DATUM_7PARAM_OVERFLOW_ERROR = 8  # Variable c_int '8'
ECK6_LAT_ERROR = 1  # Variable c_int '1'
NZMG_NORTHING_ERROR = 8  # Variable c_int '8'
GEOREF_LAT_ERROR = 1  # Variable c_int '1'

# values for enumeration 'Datum_Types'
Datum_Types = c_int  # enum
Datum_Type = Datum_Types
Initialize_Geoid = _libraries['geotrans2.dll'].Initialize_Geoid
Initialize_Geoid.restype = c_long
Initialize_Geoid.argtypes = []
Convert_Ellipsoid_To_Geoid_Height = (
	_libraries['geotrans2.dll'].Convert_Ellipsoid_To_Geoid_Height)
Convert_Ellipsoid_To_Geoid_Height.restype = c_long
Convert_Ellipsoid_To_Geoid_Height.argtypes = [
	c_double, c_double, c_double, POINTER(c_double)]
Convert_Ellipsoid_To_MSL_EGM96_VG_NS_Height = (
	_libraries['geotrans2.dll'].Convert_Ellipsoid_To_MSL_EGM96_VG_NS_Height)
Convert_Ellipsoid_To_MSL_EGM96_VG_NS_Height.restype = c_long
Convert_Ellipsoid_To_MSL_EGM96_VG_NS_Height.argtypes = [
	c_double, c_double, c_double, POINTER(c_double)]
Convert_Ellipsoid_To_MSL_EGM84_10D_BL_Height = (
	_libraries['geotrans2.dll'].Convert_Ellipsoid_To_MSL_EGM84_10D_BL_Height)
Convert_Ellipsoid_To_MSL_EGM84_10D_BL_Height.restype = c_long
Convert_Ellipsoid_To_MSL_EGM84_10D_BL_Height.argtypes = [
	c_double, c_double, c_double, POINTER(c_double)]
Convert_Ellipsoid_To_MSL_EGM84_10D_NS_Height = (
	_libraries['geotrans2.dll'].Convert_Ellipsoid_To_MSL_EGM84_10D_NS_Height)
Convert_Ellipsoid_To_MSL_EGM84_10D_NS_Height.restype = c_long
Convert_Ellipsoid_To_MSL_EGM84_10D_NS_Height.argtypes = [
	c_double, c_double, c_double, POINTER(c_double)]

# values for enumeration 'Input_Output'
Input_Output = c_int  # enum
Input_or_Output = Input_Output

# values for enumeration 'File_Interactive'
File_Interactive = c_int  # enum
File_or_Interactive = File_Interactive

# values for enumeration 'Coordinate_Types'
Coordinate_Types = c_int  # enum
Coordinate_Type = Coordinate_Types

# values for enumeration 'Precisions'
Precisions = c_int  # enum
Precision = Precisions

# values for enumeration 'Height_Types'
Height_Types = c_int  # enum
Height_Type = Height_Types

# values for enumeration 'Define_Datum_Types'
Define_Datum_Types = c_int  # enum
Define_Datum_Type = Define_Datum_Types


class Geocentric_Tuple_Structure(Structure):
    pass
Geocentric_Tuple_Structure._fields_ = [
    ('x', c_double),
    ('y', c_double),
    ('z', c_double),
]
Geocentric_Tuple = Geocentric_Tuple_Structure
class Geodetic_Structure(Structure):
    pass
Geodetic_Structure._fields_ = [
    ('height_type', Height_Type),
]
Geodetic_Parameters = Geodetic_Structure
class Geodetic_Tuple_Structure(Structure):
    pass
Geodetic_Tuple_Structure._fields_ = [
    ('longitude', c_double),
    ('latitude', c_double),
    ('height', c_double),
]
Geodetic_Tuple = Geodetic_Tuple_Structure
class GEOREF_Tuple_Structure(Structure):
    pass
GEOREF_Tuple_Structure._fields_ = [
    ('string', c_char * 21),
]
GEOREF_Tuple = GEOREF_Tuple_Structure
class Albers_Equal_Area_Conic_Structure(Structure):
    pass
Albers_Equal_Area_Conic_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('std_parallel_1', c_double),
    ('std_parallel_2', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Albers_Equal_Area_Conic_Parameters = Albers_Equal_Area_Conic_Structure
class Albers_Equal_Area_Conic_Tuple_Structure(Structure):
    pass
Albers_Equal_Area_Conic_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Albers_Equal_Area_Conic_Tuple = Albers_Equal_Area_Conic_Tuple_Structure
class Azimuthal_Equidistant_Structure(Structure):
    pass
Azimuthal_Equidistant_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Azimuthal_Equidistant_Parameters = Azimuthal_Equidistant_Structure
class Azimuthal_Equidistant_Tuple_Structure(Structure):
    pass
Azimuthal_Equidistant_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Azimuthal_Equidistant_Tuple = Azimuthal_Equidistant_Tuple_Structure
class BNG_Tuple_Structure(Structure):
    pass
BNG_Tuple_Structure._fields_ = [
    ('string', c_char * 21),
]
BNG_Tuple = BNG_Tuple_Structure
class Bonne_Structure(Structure):
    pass
Bonne_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Bonne_Parameters = Bonne_Structure
class Bonne_Tuple_Structure(Structure):
    pass
Bonne_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Bonne_Tuple = Bonne_Tuple_Structure
class Cassini_Structure(Structure):
    pass
Cassini_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Cassini_Parameters = Cassini_Structure
class Cassini_Tuple_Structure(Structure):
    pass
Cassini_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Cassini_Tuple = Cassini_Tuple_Structure
class Cylindrical_Equal_Area_Structure(Structure):
    pass
Cylindrical_Equal_Area_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Cylindrical_Equal_Area_Parameters = Cylindrical_Equal_Area_Structure
class Cylindrical_Equal_Area_Tuple_Structure(Structure):
    pass
Cylindrical_Equal_Area_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Cylindrical_Equal_Area_Tuple = Cylindrical_Equal_Area_Tuple_Structure
class Eckert4_Structure(Structure):
    pass
Eckert4_Structure._fields_ = [
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Eckert4_Parameters = Eckert4_Structure
class Eckert4_Tuple_Structure(Structure):
    pass
Eckert4_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Eckert4_Tuple = Eckert4_Tuple_Structure
class Eckert6_Structure(Structure):
    pass
Eckert6_Structure._fields_ = [
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Eckert6_Parameters = Eckert6_Structure
class Eckert6_Tuple_Structure(Structure):
    pass
Eckert6_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Eckert6_Tuple = Eckert6_Tuple_Structure
class Equidistant_Cylindrical_Structure(Structure):
    pass
Equidistant_Cylindrical_Structure._fields_ = [
    ('std_parallel', c_double),
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Equidistant_Cylindrical_Parameters = Equidistant_Cylindrical_Structure
class Equidistant_Cylindrical_Tuple_Structure(Structure):
    pass
Equidistant_Cylindrical_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Equidistant_Cylindrical_Tuple = Equidistant_Cylindrical_Tuple_Structure
class GARS_Tuple_Structure(Structure):
    pass
GARS_Tuple_Structure._fields_ = [
    ('string', c_char * 8),
]
GARS_Tuple = GARS_Tuple_Structure
class Gnomonic_Structure(Structure):
    pass
Gnomonic_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Gnomonic_Parameters = Gnomonic_Structure
class Gnomonic_Tuple_Structure(Structure):
    pass
Gnomonic_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Gnomonic_Tuple = Gnomonic_Tuple_Structure
class Lambert_Conformal_Conic_1_Structure(Structure):
    pass
Lambert_Conformal_Conic_1_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('scale_factor', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Lambert_Conformal_Conic_1_Parameters = Lambert_Conformal_Conic_1_Structure
class Lambert_Conformal_Conic_1_Tuple_Structure(Structure):
    pass
Lambert_Conformal_Conic_1_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Lambert_Conformal_Conic_1_Tuple = Lambert_Conformal_Conic_1_Tuple_Structure
class Lambert_Conformal_Conic_2_Structure(Structure):
    pass
Lambert_Conformal_Conic_2_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('std_parallel_1', c_double),
    ('std_parallel_2', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Lambert_Conformal_Conic_2_Parameters = Lambert_Conformal_Conic_2_Structure
class Lambert_Conformal_Conic_2_Tuple_Structure(Structure):
    pass
Lambert_Conformal_Conic_2_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Lambert_Conformal_Conic_2_Tuple = Lambert_Conformal_Conic_2_Tuple_Structure
class Local_Cartesian_Structure(Structure):
    pass
Local_Cartesian_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('origin_longitude', c_double),
    ('origin_height', c_double),
    ('orientation', c_double),
]
Local_Cartesian_Parameters = Local_Cartesian_Structure
class Local_Cartesian_Tuple_Structure(Structure):
    pass
Local_Cartesian_Tuple_Structure._fields_ = [
    ('x', c_double),
    ('y', c_double),
    ('z', c_double),
]
Local_Cartesian_Tuple = Local_Cartesian_Tuple_Structure
class Mercator_Structure(Structure):
    pass
Mercator_Structure._fields_ = [
    ('latitude_of_true_scale', c_double),
    ('central_meridian', c_double),
    ('scale_factor', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Mercator_Parameters = Mercator_Structure
class Mercator_Tuple_Structure(Structure):
    pass
Mercator_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Mercator_Tuple = Mercator_Tuple_Structure
class MGRS_Tuple_Structure(Structure):
    pass
MGRS_Tuple_Structure._fields_ = [
    ('string', c_char * 21),
]
MGRS_Tuple = MGRS_Tuple_Structure
class Miller_Cylindrical_Structure(Structure):
    pass
Miller_Cylindrical_Structure._fields_ = [
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Miller_Cylindrical_Parameters = Miller_Cylindrical_Structure
class Miller_Cylindrical_Tuple_Structure(Structure):
    pass
Miller_Cylindrical_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Miller_Cylindrical_Tuple = Miller_Cylindrical_Tuple_Structure
class Mollweide_Structure(Structure):
    pass
Mollweide_Structure._fields_ = [
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Mollweide_Parameters = Mollweide_Structure
class Mollweide_Tuple_Structure(Structure):
    pass
Mollweide_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Mollweide_Tuple = Mollweide_Tuple_Structure
class Neys_Structure(Structure):
    pass
Neys_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('std_parallel_1', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Neys_Parameters = Neys_Structure
class Neys_Tuple_Structure(Structure):
    pass
Neys_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Neys_Tuple = Neys_Tuple_Structure
class NZMG_Tuple_Structure(Structure):
    pass
NZMG_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
NZMG_Tuple = NZMG_Tuple_Structure
class Oblique_Mercator_Structure(Structure):
    pass
Oblique_Mercator_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('latitude_1', c_double),
    ('longitude_1', c_double),
    ('latitude_2', c_double),
    ('longitude_2', c_double),
    ('scale_factor', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Oblique_Mercator_Parameters = Oblique_Mercator_Structure
class Oblique_Mercator_Tuple_Structure(Structure):
    pass
Oblique_Mercator_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Oblique_Mercator_Tuple = Oblique_Mercator_Tuple_Structure
class Orthographic_Structure(Structure):
    pass
Orthographic_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Orthographic_Parameters = Orthographic_Structure
class Orthographic_Tuple_Structure(Structure):
    pass
Orthographic_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Orthographic_Tuple = Orthographic_Tuple_Structure
class Polar_Stereo_Structure(Structure):
    pass
Polar_Stereo_Structure._fields_ = [
    ('latitude_of_true_scale', c_double),
    ('longitude_down_from_pole', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Polar_Stereo_Parameters = Polar_Stereo_Structure
class Polar_Stereo_Tuple_Structure(Structure):
    pass
Polar_Stereo_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Polar_Stereo_Tuple = Polar_Stereo_Tuple_Structure
class Polyconic_Structure(Structure):
    pass
Polyconic_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Polyconic_Parameters = Polyconic_Structure
class Polyconic_Tuple_Structure(Structure):
    pass
Polyconic_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Polyconic_Tuple = Polyconic_Tuple_Structure
class Sinusoidal_Structure(Structure):
    pass
Sinusoidal_Structure._fields_ = [
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Sinusoidal_Parameters = Sinusoidal_Structure
class Sinusoidal_Tuple_Structure(Structure):
    pass
Sinusoidal_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Sinusoidal_Tuple = Sinusoidal_Tuple_Structure
class Stereographic_Structure(Structure):
    pass
Stereographic_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Stereographic_Parameters = Stereographic_Structure
class Stereographic_Tuple_Structure(Structure):
    pass
Stereographic_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Stereographic_Tuple = Stereographic_Tuple_Structure
class Transverse_Cylindrical_Equal_Area_Structure(Structure):
    pass
Transverse_Cylindrical_Equal_Area_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('scale_factor', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Transverse_Cylindrical_Equal_Area_Parameters = Transverse_Cylindrical_Equal_Area_Structure
class Transverse_Cylindrical_Equal_Area_Tuple_Structure(Structure):
    pass
Transverse_Cylindrical_Equal_Area_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Transverse_Cylindrical_Equal_Area_Tuple = Transverse_Cylindrical_Equal_Area_Tuple_Structure
class Transverse_Mercator_Structure(Structure):
    pass
Transverse_Mercator_Structure._fields_ = [
    ('origin_latitude', c_double),
    ('central_meridian', c_double),
    ('scale_factor', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Transverse_Mercator_Parameters = Transverse_Mercator_Structure
class Transverse_Mercator_Tuple_Structure(Structure):
    pass
Transverse_Mercator_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Transverse_Mercator_Tuple = Transverse_Mercator_Tuple_Structure
class UPS_Tuple_Structure(Structure):
    pass
UPS_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
    ('hemisphere', c_char),
]
UPS_Tuple = UPS_Tuple_Structure
class USNG_Tuple_Structure(Structure):
    pass
USNG_Tuple_Structure._fields_ = [
    ('string', c_char * 21),
]
USNG_Tuple = USNG_Tuple_Structure
class UTM_Structure(Structure):
    pass
UTM_Structure._fields_ = [
    ('zone', c_long),
    ('override', c_long),
]
UTM_Parameters = UTM_Structure
class UTM_Tuple_Structure(Structure):
    pass
UTM_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
    ('zone', c_long),
    ('hemisphere', c_char),
]
UTM_Tuple = UTM_Tuple_Structure
class Van_der_Grinten_Structure(Structure):
    pass
Van_der_Grinten_Structure._fields_ = [
    ('central_meridian', c_double),
    ('false_easting', c_double),
    ('false_northing', c_double),
]
Van_der_Grinten_Parameters = Van_der_Grinten_Structure
class Van_der_Grinten_Tuple_Structure(Structure):
    pass
Van_der_Grinten_Tuple_Structure._fields_ = [
    ('easting', c_double),
    ('northing', c_double),
]
Van_der_Grinten_Tuple = Van_der_Grinten_Tuple_Structure
Initialize_Engine = _libraries['geotrans2.dll'].Initialize_Engine
Initialize_Engine.restype = c_long
Initialize_Engine.argtypes = []
Valid_Conversion = _libraries['geotrans2.dll'].Valid_Conversion
Valid_Conversion.restype = c_int
Valid_Conversion.argtypes = [Coordinate_Types, Coordinate_Types, c_long, c_long]
Get_Coordinate_System_Count = _libraries['geotrans2.dll'].Get_Coordinate_System_Count
Get_Coordinate_System_Count.restype = c_long
Get_Coordinate_System_Count.argtypes = [POINTER(c_long)]
Get_Coordinate_System_Index = _libraries['geotrans2.dll'].Get_Coordinate_System_Index
Get_Coordinate_System_Index.restype = c_long
Get_Coordinate_System_Index.argtypes = [STRING, POINTER(c_long)]
Get_Coordinate_System_Type = _libraries['geotrans2.dll'].Get_Coordinate_System_Type
Get_Coordinate_System_Type.restype = c_long
Get_Coordinate_System_Type.argtypes = [c_long, POINTER(Coordinate_Type)]
Get_Coordinate_System_Name = _libraries['geotrans2.dll'].Get_Coordinate_System_Name
Get_Coordinate_System_Name.restype = c_long
Get_Coordinate_System_Name.argtypes = [c_long, STRING]
Get_Coordinate_System_Code = _libraries['geotrans2.dll'].Get_Coordinate_System_Code
Get_Coordinate_System_Code.restype = c_long
Get_Coordinate_System_Code.argtypes = [c_long, STRING]
Set_Coordinate_System = _libraries['geotrans2.dll'].Set_Coordinate_System
Set_Coordinate_System.restype = c_long
Set_Coordinate_System.argtypes = [File_Interactive, Input_Output, Coordinate_Types]
Get_Coordinate_System = _libraries['geotrans2.dll'].Get_Coordinate_System
Get_Coordinate_System.restype = c_long
Get_Coordinate_System.argtypes = [File_Interactive, Input_Output, POINTER(Coordinate_Type)]
Get_Datum_Count = _libraries['geotrans2.dll'].Get_Datum_Count
Get_Datum_Count.restype = c_long
Get_Datum_Count.argtypes = [POINTER(c_long)]
Get_Datum_Index = _libraries['geotrans2.dll'].Get_Datum_Index
Get_Datum_Index.restype = c_long
Get_Datum_Index.argtypes = [STRING, POINTER(c_long)]
Get_Datum_Name = _libraries['geotrans2.dll'].Get_Datum_Name
Get_Datum_Name.restype = c_long
Get_Datum_Name.argtypes = [c_long, STRING]
Get_Datum_Code = _libraries['geotrans2.dll'].Get_Datum_Code
Get_Datum_Code.restype = c_long
Get_Datum_Code.argtypes = [c_long, STRING]
Get_Datum_Ellipsoid_Code = _libraries['geotrans2.dll'].Get_Datum_Ellipsoid_Code
Get_Datum_Ellipsoid_Code.restype = c_long
Get_Datum_Ellipsoid_Code.argtypes = [c_long, STRING]
Get_Datum_Type = _libraries['geotrans2.dll'].Get_Datum_Type
Get_Datum_Type.restype = c_long
Get_Datum_Type.argtypes = [c_long, POINTER(Define_Datum_Type)]
Get_Datum_Seven_Parameters = _libraries['geotrans2.dll'].Get_Datum_Seven_Parameters
Get_Datum_Seven_Parameters.restype = c_long
Get_Datum_Seven_Parameters.argtypes = [c_long, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
Get_Datum_Three_Parameters = _libraries['geotrans2.dll'].Get_Datum_Three_Parameters
Get_Datum_Three_Parameters.restype = c_long
Get_Datum_Three_Parameters.argtypes = [c_long, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
Get_Datum_Errors = _libraries['geotrans2.dll'].Get_Datum_Errors
Get_Datum_Errors.restype = c_long
Get_Datum_Errors.argtypes = [c_long, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
Get_Datum_Valid_Rectangle = _libraries['geotrans2.dll'].Get_Datum_Valid_Rectangle
Get_Datum_Valid_Rectangle.restype = c_long
Get_Datum_Valid_Rectangle.argtypes = [c_long, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
Check_Datum_User_Defined = _libraries['geotrans2.dll'].Check_Datum_User_Defined
Check_Datum_User_Defined.restype = c_long
Check_Datum_User_Defined.argtypes = [c_long, POINTER(c_long)]
Check_Valid_Datum = _libraries['geotrans2.dll'].Check_Valid_Datum
Check_Valid_Datum.restype = c_long
Check_Valid_Datum.argtypes = [c_long, c_double, c_double, POINTER(c_long)]
Set_Datum = _libraries['geotrans2.dll'].Set_Datum
Set_Datum.restype = c_long
Set_Datum.argtypes = [File_Interactive, Input_Output, c_long]
Get_Datum = _libraries['geotrans2.dll'].Get_Datum
Get_Datum.restype = c_long
Get_Datum.argtypes = [File_Interactive, Input_Output, POINTER(c_long)]
Define_Datum = _libraries['geotrans2.dll'].Define_Datum
Define_Datum.restype = c_long
Define_Datum.argtypes = [Define_Datum_Types, STRING, STRING, STRING, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double]
Remove_Datum = _libraries['geotrans2.dll'].Remove_Datum
Remove_Datum.restype = c_long
Remove_Datum.argtypes = [STRING]
Get_Ellipsoid_Count = _libraries['geotrans2.dll'].Get_Ellipsoid_Count
Get_Ellipsoid_Count.restype = c_long
Get_Ellipsoid_Count.argtypes = [POINTER(c_long)]
Get_Ellipsoid_Index = _libraries['geotrans2.dll'].Get_Ellipsoid_Index
Get_Ellipsoid_Index.restype = c_long
Get_Ellipsoid_Index.argtypes = [STRING, POINTER(c_long)]
Get_Ellipsoid_Name = _libraries['geotrans2.dll'].Get_Ellipsoid_Name
Get_Ellipsoid_Name.restype = c_long
Get_Ellipsoid_Name.argtypes = [c_long, STRING]
Get_Ellipsoid_Parameters = _libraries['geotrans2.dll'].Get_Ellipsoid_Parameters
Get_Ellipsoid_Parameters.restype = c_long
Get_Ellipsoid_Parameters.argtypes = [c_long, POINTER(c_double), POINTER(c_double)]
Get_Ellipsoid_Code = _libraries['geotrans2.dll'].Get_Ellipsoid_Code
Get_Ellipsoid_Code.restype = c_long
Get_Ellipsoid_Code.argtypes = [c_long, STRING]
Get_Ellipsoid_Eccentricity2 = _libraries['geotrans2.dll'].Get_Ellipsoid_Eccentricity2
Get_Ellipsoid_Eccentricity2.restype = c_long
Get_Ellipsoid_Eccentricity2.argtypes = [c_long, POINTER(c_double)]
Check_Ellipsoid_User_Defined = _libraries['geotrans2.dll'].Check_Ellipsoid_User_Defined
Check_Ellipsoid_User_Defined.restype = c_long
Check_Ellipsoid_User_Defined.argtypes = [c_long, POINTER(c_long)]
Define_Ellipsoid = _libraries['geotrans2.dll'].Define_Ellipsoid
Define_Ellipsoid.restype = c_long
Define_Ellipsoid.argtypes = [STRING, STRING, c_double, c_double]
Remove_Ellipsoid = _libraries['geotrans2.dll'].Remove_Ellipsoid
Remove_Ellipsoid.restype = c_long
Remove_Ellipsoid.argtypes = [STRING]
Set_Precision = _libraries['geotrans2.dll'].Set_Precision
Set_Precision.restype = None
Set_Precision.argtypes = [Precisions]
Get_Precision = _libraries['geotrans2.dll'].Get_Precision
Get_Precision.restype = None
Get_Precision.argtypes = [POINTER(Precision)]
Set_Geocentric_Coordinates = _libraries['geotrans2.dll'].Set_Geocentric_Coordinates
Set_Geocentric_Coordinates.restype = c_long
Set_Geocentric_Coordinates.argtypes = [File_Interactive, Input_Output, Geocentric_Tuple_Structure]
Get_Geocentric_Coordinates = _libraries['geotrans2.dll'].Get_Geocentric_Coordinates
Get_Geocentric_Coordinates.restype = c_long
Get_Geocentric_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Geocentric_Tuple)]
Set_Geodetic_Params = _libraries['geotrans2.dll'].Set_Geodetic_Params
Set_Geodetic_Params.restype = c_long
Set_Geodetic_Params.argtypes = [File_Interactive, Input_Output, Geodetic_Structure]
Get_Geodetic_Params = _libraries['geotrans2.dll'].Get_Geodetic_Params
Get_Geodetic_Params.restype = c_long
Get_Geodetic_Params.argtypes = [File_Interactive, Input_Output, POINTER(Geodetic_Parameters)]
Set_Geodetic_Coordinates = _libraries['geotrans2.dll'].Set_Geodetic_Coordinates
Set_Geodetic_Coordinates.restype = c_long
Set_Geodetic_Coordinates.argtypes = [File_Interactive, Input_Output, Geodetic_Tuple_Structure]
Get_Geodetic_Coordinates = _libraries['geotrans2.dll'].Get_Geodetic_Coordinates
Get_Geodetic_Coordinates.restype = c_long
Get_Geodetic_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Geodetic_Tuple)]
Set_GEOREF_Coordinates = _libraries['geotrans2.dll'].Set_GEOREF_Coordinates
Set_GEOREF_Coordinates.restype = c_long
Set_GEOREF_Coordinates.argtypes = [File_Interactive, Input_Output, GEOREF_Tuple_Structure]
Get_GEOREF_Coordinates = _libraries['geotrans2.dll'].Get_GEOREF_Coordinates
Get_GEOREF_Coordinates.restype = c_long
Get_GEOREF_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(GEOREF_Tuple)]
Set_Albers_Equal_Area_Conic_Params = _libraries['geotrans2.dll'].Set_Albers_Equal_Area_Conic_Params
Set_Albers_Equal_Area_Conic_Params.restype = c_long
Set_Albers_Equal_Area_Conic_Params.argtypes = [File_Interactive, Input_Output, Albers_Equal_Area_Conic_Structure]
Get_Albers_Equal_Area_Conic_Params = _libraries['geotrans2.dll'].Get_Albers_Equal_Area_Conic_Params
Get_Albers_Equal_Area_Conic_Params.restype = c_long
Get_Albers_Equal_Area_Conic_Params.argtypes = [File_Interactive, Input_Output, POINTER(Albers_Equal_Area_Conic_Parameters)]
Set_Albers_Equal_Area_Conic_Coordinates = _libraries['geotrans2.dll'].Set_Albers_Equal_Area_Conic_Coordinates
Set_Albers_Equal_Area_Conic_Coordinates.restype = c_long
Set_Albers_Equal_Area_Conic_Coordinates.argtypes = [File_Interactive, Input_Output, Albers_Equal_Area_Conic_Tuple_Structure]
Get_Albers_Equal_Area_Conic_Coordinates = _libraries['geotrans2.dll'].Get_Albers_Equal_Area_Conic_Coordinates
Get_Albers_Equal_Area_Conic_Coordinates.restype = c_long
Get_Albers_Equal_Area_Conic_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Albers_Equal_Area_Conic_Tuple)]
Set_Azimuthal_Equidistant_Params = _libraries['geotrans2.dll'].Set_Azimuthal_Equidistant_Params
Set_Azimuthal_Equidistant_Params.restype = c_long
Set_Azimuthal_Equidistant_Params.argtypes = [File_Interactive, Input_Output, Azimuthal_Equidistant_Structure]
Get_Azimuthal_Equidistant_Params = _libraries['geotrans2.dll'].Get_Azimuthal_Equidistant_Params
Get_Azimuthal_Equidistant_Params.restype = c_long
Get_Azimuthal_Equidistant_Params.argtypes = [File_Interactive, Input_Output, POINTER(Azimuthal_Equidistant_Parameters)]
Set_Azimuthal_Equidistant_Coordinates = _libraries['geotrans2.dll'].Set_Azimuthal_Equidistant_Coordinates
Set_Azimuthal_Equidistant_Coordinates.restype = c_long
Set_Azimuthal_Equidistant_Coordinates.argtypes = [File_Interactive, Input_Output, Azimuthal_Equidistant_Tuple_Structure]
Get_Azimuthal_Equidistant_Coordinates = _libraries['geotrans2.dll'].Get_Azimuthal_Equidistant_Coordinates
Get_Azimuthal_Equidistant_Coordinates.restype = c_long
Get_Azimuthal_Equidistant_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Azimuthal_Equidistant_Tuple)]
Set_BNG_Coordinates = _libraries['geotrans2.dll'].Set_BNG_Coordinates
Set_BNG_Coordinates.restype = c_long
Set_BNG_Coordinates.argtypes = [File_Interactive, Input_Output, BNG_Tuple_Structure]
Get_BNG_Coordinates = _libraries['geotrans2.dll'].Get_BNG_Coordinates
Get_BNG_Coordinates.restype = c_long
Get_BNG_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(BNG_Tuple)]
Set_Bonne_Params = _libraries['geotrans2.dll'].Set_Bonne_Params
Set_Bonne_Params.restype = c_long
Set_Bonne_Params.argtypes = [File_Interactive, Input_Output, Bonne_Structure]
Get_Bonne_Params = _libraries['geotrans2.dll'].Get_Bonne_Params
Get_Bonne_Params.restype = c_long
Get_Bonne_Params.argtypes = [File_Interactive, Input_Output, POINTER(Bonne_Parameters)]
Set_Bonne_Coordinates = _libraries['geotrans2.dll'].Set_Bonne_Coordinates
Set_Bonne_Coordinates.restype = c_long
Set_Bonne_Coordinates.argtypes = [File_Interactive, Input_Output, Bonne_Tuple_Structure]
Get_Bonne_Coordinates = _libraries['geotrans2.dll'].Get_Bonne_Coordinates
Get_Bonne_Coordinates.restype = c_long
Get_Bonne_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Bonne_Tuple)]
Set_Cassini_Params = _libraries['geotrans2.dll'].Set_Cassini_Params
Set_Cassini_Params.restype = c_long
Set_Cassini_Params.argtypes = [File_Interactive, Input_Output, Cassini_Structure]
Get_Cassini_Params = _libraries['geotrans2.dll'].Get_Cassini_Params
Get_Cassini_Params.restype = c_long
Get_Cassini_Params.argtypes = [File_Interactive, Input_Output, POINTER(Cassini_Parameters)]
Set_Cassini_Coordinates = _libraries['geotrans2.dll'].Set_Cassini_Coordinates
Set_Cassini_Coordinates.restype = c_long
Set_Cassini_Coordinates.argtypes = [File_Interactive, Input_Output, Cassini_Tuple_Structure]
Get_Cassini_Coordinates = _libraries['geotrans2.dll'].Get_Cassini_Coordinates
Get_Cassini_Coordinates.restype = c_long
Get_Cassini_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Cassini_Tuple)]
Set_Cylindrical_Equal_Area_Params = _libraries['geotrans2.dll'].Set_Cylindrical_Equal_Area_Params
Set_Cylindrical_Equal_Area_Params.restype = c_long
Set_Cylindrical_Equal_Area_Params.argtypes = [File_Interactive, Input_Output, Cylindrical_Equal_Area_Structure]
Get_Cylindrical_Equal_Area_Params = _libraries['geotrans2.dll'].Get_Cylindrical_Equal_Area_Params
Get_Cylindrical_Equal_Area_Params.restype = c_long
Get_Cylindrical_Equal_Area_Params.argtypes = [File_Interactive, Input_Output, POINTER(Cylindrical_Equal_Area_Parameters)]
Set_Cylindrical_Equal_Area_Coordinates = _libraries['geotrans2.dll'].Set_Cylindrical_Equal_Area_Coordinates
Set_Cylindrical_Equal_Area_Coordinates.restype = c_long
Set_Cylindrical_Equal_Area_Coordinates.argtypes = [File_Interactive, Input_Output, Cylindrical_Equal_Area_Tuple_Structure]
Get_Cylindrical_Equal_Area_Coordinates = _libraries['geotrans2.dll'].Get_Cylindrical_Equal_Area_Coordinates
Get_Cylindrical_Equal_Area_Coordinates.restype = c_long
Get_Cylindrical_Equal_Area_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Cylindrical_Equal_Area_Tuple)]
Set_Eckert4_Params = _libraries['geotrans2.dll'].Set_Eckert4_Params
Set_Eckert4_Params.restype = c_long
Set_Eckert4_Params.argtypes = [File_Interactive, Input_Output, Eckert4_Structure]
Get_Eckert4_Params = _libraries['geotrans2.dll'].Get_Eckert4_Params
Get_Eckert4_Params.restype = c_long
Get_Eckert4_Params.argtypes = [File_Interactive, Input_Output, POINTER(Eckert4_Parameters)]
Set_Eckert4_Coordinates = _libraries['geotrans2.dll'].Set_Eckert4_Coordinates
Set_Eckert4_Coordinates.restype = c_long
Set_Eckert4_Coordinates.argtypes = [File_Interactive, Input_Output, Eckert4_Tuple_Structure]
Get_Eckert4_Coordinates = _libraries['geotrans2.dll'].Get_Eckert4_Coordinates
Get_Eckert4_Coordinates.restype = c_long
Get_Eckert4_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Eckert4_Tuple)]
Set_Eckert6_Params = _libraries['geotrans2.dll'].Set_Eckert6_Params
Set_Eckert6_Params.restype = c_long
Set_Eckert6_Params.argtypes = [File_Interactive, Input_Output, Eckert6_Structure]
Get_Eckert6_Params = _libraries['geotrans2.dll'].Get_Eckert6_Params
Get_Eckert6_Params.restype = c_long
Get_Eckert6_Params.argtypes = [File_Interactive, Input_Output, POINTER(Eckert6_Parameters)]
Set_Eckert6_Coordinates = _libraries['geotrans2.dll'].Set_Eckert6_Coordinates
Set_Eckert6_Coordinates.restype = c_long
Set_Eckert6_Coordinates.argtypes = [File_Interactive, Input_Output, Eckert6_Tuple_Structure]
Get_Eckert6_Coordinates = _libraries['geotrans2.dll'].Get_Eckert6_Coordinates
Get_Eckert6_Coordinates.restype = c_long
Get_Eckert6_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Eckert6_Tuple)]
Set_Equidistant_Cylindrical_Params = _libraries['geotrans2.dll'].Set_Equidistant_Cylindrical_Params
Set_Equidistant_Cylindrical_Params.restype = c_long
Set_Equidistant_Cylindrical_Params.argtypes = [File_Interactive, Input_Output, Equidistant_Cylindrical_Structure]
Get_Equidistant_Cylindrical_Params = _libraries['geotrans2.dll'].Get_Equidistant_Cylindrical_Params
Get_Equidistant_Cylindrical_Params.restype = c_long
Get_Equidistant_Cylindrical_Params.argtypes = [File_Interactive, Input_Output, POINTER(Equidistant_Cylindrical_Parameters)]
Set_Equidistant_Cylindrical_Coordinates = _libraries['geotrans2.dll'].Set_Equidistant_Cylindrical_Coordinates
Set_Equidistant_Cylindrical_Coordinates.restype = c_long
Set_Equidistant_Cylindrical_Coordinates.argtypes = [File_Interactive, Input_Output, Equidistant_Cylindrical_Tuple_Structure]
Get_Equidistant_Cylindrical_Coordinates = _libraries['geotrans2.dll'].Get_Equidistant_Cylindrical_Coordinates
Get_Equidistant_Cylindrical_Coordinates.restype = c_long
Get_Equidistant_Cylindrical_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Equidistant_Cylindrical_Tuple)]
Set_GARS_Coordinates = _libraries['geotrans2.dll'].Set_GARS_Coordinates
Set_GARS_Coordinates.restype = c_long
Set_GARS_Coordinates.argtypes = [File_Interactive, Input_Output, GARS_Tuple_Structure]
Get_GARS_Coordinates = _libraries['geotrans2.dll'].Get_GARS_Coordinates
Get_GARS_Coordinates.restype = c_long
Get_GARS_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(GARS_Tuple)]
Set_Gnomonic_Params = _libraries['geotrans2.dll'].Set_Gnomonic_Params
Set_Gnomonic_Params.restype = c_long
Set_Gnomonic_Params.argtypes = [File_Interactive, Input_Output, Gnomonic_Structure]
Get_Gnomonic_Params = _libraries['geotrans2.dll'].Get_Gnomonic_Params
Get_Gnomonic_Params.restype = c_long
Get_Gnomonic_Params.argtypes = [File_Interactive, Input_Output, POINTER(Gnomonic_Parameters)]
Set_Gnomonic_Coordinates = _libraries['geotrans2.dll'].Set_Gnomonic_Coordinates
Set_Gnomonic_Coordinates.restype = c_long
Set_Gnomonic_Coordinates.argtypes = [File_Interactive, Input_Output, Gnomonic_Tuple_Structure]
Get_Gnomonic_Coordinates = _libraries['geotrans2.dll'].Get_Gnomonic_Coordinates
Get_Gnomonic_Coordinates.restype = c_long
Get_Gnomonic_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Gnomonic_Tuple)]
Set_Lambert_Conformal_Conic_1_Params = _libraries['geotrans2.dll'].Set_Lambert_Conformal_Conic_1_Params
Set_Lambert_Conformal_Conic_1_Params.restype = c_long
Set_Lambert_Conformal_Conic_1_Params.argtypes = [File_Interactive, Input_Output, Lambert_Conformal_Conic_1_Structure]
Get_Lambert_Conformal_Conic_1_Params = _libraries['geotrans2.dll'].Get_Lambert_Conformal_Conic_1_Params
Get_Lambert_Conformal_Conic_1_Params.restype = c_long
Get_Lambert_Conformal_Conic_1_Params.argtypes = [File_Interactive, Input_Output, POINTER(Lambert_Conformal_Conic_1_Parameters)]
Set_Lambert_Conformal_Conic_1_Coordinates = _libraries['geotrans2.dll'].Set_Lambert_Conformal_Conic_1_Coordinates
Set_Lambert_Conformal_Conic_1_Coordinates.restype = c_long
Set_Lambert_Conformal_Conic_1_Coordinates.argtypes = [File_Interactive, Input_Output, Lambert_Conformal_Conic_1_Tuple_Structure]
Get_Lambert_Conformal_Conic_1_Coordinates = _libraries['geotrans2.dll'].Get_Lambert_Conformal_Conic_1_Coordinates
Get_Lambert_Conformal_Conic_1_Coordinates.restype = c_long
Get_Lambert_Conformal_Conic_1_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Lambert_Conformal_Conic_1_Tuple)]
Set_Lambert_Conformal_Conic_2_Params = _libraries['geotrans2.dll'].Set_Lambert_Conformal_Conic_2_Params
Set_Lambert_Conformal_Conic_2_Params.restype = c_long
Set_Lambert_Conformal_Conic_2_Params.argtypes = [File_Interactive, Input_Output, Lambert_Conformal_Conic_2_Structure]
Get_Lambert_Conformal_Conic_2_Params = _libraries['geotrans2.dll'].Get_Lambert_Conformal_Conic_2_Params
Get_Lambert_Conformal_Conic_2_Params.restype = c_long
Get_Lambert_Conformal_Conic_2_Params.argtypes = [File_Interactive, Input_Output, POINTER(Lambert_Conformal_Conic_2_Parameters)]
Set_Lambert_Conformal_Conic_2_Coordinates = _libraries['geotrans2.dll'].Set_Lambert_Conformal_Conic_2_Coordinates
Set_Lambert_Conformal_Conic_2_Coordinates.restype = c_long
Set_Lambert_Conformal_Conic_2_Coordinates.argtypes = [File_Interactive, Input_Output, Lambert_Conformal_Conic_2_Tuple_Structure]
Get_Lambert_Conformal_Conic_2_Coordinates = _libraries['geotrans2.dll'].Get_Lambert_Conformal_Conic_2_Coordinates
Get_Lambert_Conformal_Conic_2_Coordinates.restype = c_long
Get_Lambert_Conformal_Conic_2_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Lambert_Conformal_Conic_2_Tuple)]
Set_Local_Cartesian_Params = _libraries['geotrans2.dll'].Set_Local_Cartesian_Params
Set_Local_Cartesian_Params.restype = c_long
Set_Local_Cartesian_Params.argtypes = [File_Interactive, Input_Output, Local_Cartesian_Structure]
Get_Local_Cartesian_Params = _libraries['geotrans2.dll'].Get_Local_Cartesian_Params
Get_Local_Cartesian_Params.restype = c_long
Get_Local_Cartesian_Params.argtypes = [File_Interactive, Input_Output, POINTER(Local_Cartesian_Parameters)]
Set_Local_Cartesian_Coordinates = _libraries['geotrans2.dll'].Set_Local_Cartesian_Coordinates
Set_Local_Cartesian_Coordinates.restype = c_long
Set_Local_Cartesian_Coordinates.argtypes = [File_Interactive, Input_Output, Local_Cartesian_Tuple_Structure]
Get_Local_Cartesian_Coordinates = _libraries['geotrans2.dll'].Get_Local_Cartesian_Coordinates
Get_Local_Cartesian_Coordinates.restype = c_long
Get_Local_Cartesian_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Local_Cartesian_Tuple)]
Set_Mercator_Params = _libraries['geotrans2.dll'].Set_Mercator_Params
Set_Mercator_Params.restype = c_long
Set_Mercator_Params.argtypes = [File_Interactive, Input_Output, Mercator_Structure]
Get_Mercator_Params = _libraries['geotrans2.dll'].Get_Mercator_Params
Get_Mercator_Params.restype = c_long
Get_Mercator_Params.argtypes = [File_Interactive, Input_Output, POINTER(Mercator_Parameters)]
Set_Mercator_Coordinates = _libraries['geotrans2.dll'].Set_Mercator_Coordinates
Set_Mercator_Coordinates.restype = c_long
Set_Mercator_Coordinates.argtypes = [File_Interactive, Input_Output, Mercator_Tuple_Structure]
Get_Mercator_Coordinates = _libraries['geotrans2.dll'].Get_Mercator_Coordinates
Get_Mercator_Coordinates.restype = c_long
Get_Mercator_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Mercator_Tuple)]
Set_MGRS_Coordinates = _libraries['geotrans2.dll'].Set_MGRS_Coordinates
Set_MGRS_Coordinates.restype = c_long
Set_MGRS_Coordinates.argtypes = [File_Interactive, Input_Output, MGRS_Tuple_Structure]
Get_MGRS_Coordinates = _libraries['geotrans2.dll'].Get_MGRS_Coordinates
Get_MGRS_Coordinates.restype = c_long
Get_MGRS_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(MGRS_Tuple)]
Set_Miller_Cylindrical_Params = _libraries['geotrans2.dll'].Set_Miller_Cylindrical_Params
Set_Miller_Cylindrical_Params.restype = c_long
Set_Miller_Cylindrical_Params.argtypes = [File_Interactive, Input_Output, Miller_Cylindrical_Structure]
Get_Miller_Cylindrical_Params = _libraries['geotrans2.dll'].Get_Miller_Cylindrical_Params
Get_Miller_Cylindrical_Params.restype = c_long
Get_Miller_Cylindrical_Params.argtypes = [File_Interactive, Input_Output, POINTER(Miller_Cylindrical_Parameters)]
Set_Miller_Cylindrical_Coordinates = _libraries['geotrans2.dll'].Set_Miller_Cylindrical_Coordinates
Set_Miller_Cylindrical_Coordinates.restype = c_long
Set_Miller_Cylindrical_Coordinates.argtypes = [File_Interactive, Input_Output, Miller_Cylindrical_Tuple_Structure]
Get_Miller_Cylindrical_Coordinates = _libraries['geotrans2.dll'].Get_Miller_Cylindrical_Coordinates
Get_Miller_Cylindrical_Coordinates.restype = c_long
Get_Miller_Cylindrical_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Miller_Cylindrical_Tuple)]
Set_Mollweide_Params = _libraries['geotrans2.dll'].Set_Mollweide_Params
Set_Mollweide_Params.restype = c_long
Set_Mollweide_Params.argtypes = [File_Interactive, Input_Output, Mollweide_Structure]
Get_Mollweide_Params = _libraries['geotrans2.dll'].Get_Mollweide_Params
Get_Mollweide_Params.restype = c_long
Get_Mollweide_Params.argtypes = [File_Interactive, Input_Output, POINTER(Mollweide_Parameters)]
Set_Mollweide_Coordinates = _libraries['geotrans2.dll'].Set_Mollweide_Coordinates
Set_Mollweide_Coordinates.restype = c_long
Set_Mollweide_Coordinates.argtypes = [File_Interactive, Input_Output, Mollweide_Tuple_Structure]
Get_Mollweide_Coordinates = _libraries['geotrans2.dll'].Get_Mollweide_Coordinates
Get_Mollweide_Coordinates.restype = c_long
Get_Mollweide_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Mollweide_Tuple)]
Set_Neys_Params = _libraries['geotrans2.dll'].Set_Neys_Params
Set_Neys_Params.restype = c_long
Set_Neys_Params.argtypes = [File_Interactive, Input_Output, Neys_Structure]
Get_Neys_Params = _libraries['geotrans2.dll'].Get_Neys_Params
Get_Neys_Params.restype = c_long
Get_Neys_Params.argtypes = [File_Interactive, Input_Output, POINTER(Neys_Parameters)]
Set_Neys_Coordinates = _libraries['geotrans2.dll'].Set_Neys_Coordinates
Set_Neys_Coordinates.restype = c_long
Set_Neys_Coordinates.argtypes = [File_Interactive, Input_Output, Neys_Tuple_Structure]
Get_Neys_Coordinates = _libraries['geotrans2.dll'].Get_Neys_Coordinates
Get_Neys_Coordinates.restype = c_long
Get_Neys_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Neys_Tuple)]
Set_NZMG_Coordinates = _libraries['geotrans2.dll'].Set_NZMG_Coordinates
Set_NZMG_Coordinates.restype = c_long
Set_NZMG_Coordinates.argtypes = [File_Interactive, Input_Output, NZMG_Tuple_Structure]
Get_NZMG_Coordinates = _libraries['geotrans2.dll'].Get_NZMG_Coordinates
Get_NZMG_Coordinates.restype = c_long
Get_NZMG_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(NZMG_Tuple)]
Set_Oblique_Mercator_Params = _libraries['geotrans2.dll'].Set_Oblique_Mercator_Params
Set_Oblique_Mercator_Params.restype = c_long
Set_Oblique_Mercator_Params.argtypes = [File_Interactive, Input_Output, Oblique_Mercator_Structure]
Get_Oblique_Mercator_Params = _libraries['geotrans2.dll'].Get_Oblique_Mercator_Params
Get_Oblique_Mercator_Params.restype = c_long
Get_Oblique_Mercator_Params.argtypes = [File_Interactive, Input_Output, POINTER(Oblique_Mercator_Parameters)]
Set_Oblique_Mercator_Coordinates = _libraries['geotrans2.dll'].Set_Oblique_Mercator_Coordinates
Set_Oblique_Mercator_Coordinates.restype = c_long
Set_Oblique_Mercator_Coordinates.argtypes = [File_Interactive, Input_Output, Oblique_Mercator_Tuple_Structure]
Get_Oblique_Mercator_Coordinates = _libraries['geotrans2.dll'].Get_Oblique_Mercator_Coordinates
Get_Oblique_Mercator_Coordinates.restype = c_long
Get_Oblique_Mercator_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Oblique_Mercator_Tuple)]
Set_Orthographic_Params = _libraries['geotrans2.dll'].Set_Orthographic_Params
Set_Orthographic_Params.restype = c_long
Set_Orthographic_Params.argtypes = [File_Interactive, Input_Output, Orthographic_Structure]
Get_Orthographic_Params = _libraries['geotrans2.dll'].Get_Orthographic_Params
Get_Orthographic_Params.restype = c_long
Get_Orthographic_Params.argtypes = [File_Interactive, Input_Output, POINTER(Orthographic_Parameters)]
Set_Orthographic_Coordinates = _libraries['geotrans2.dll'].Set_Orthographic_Coordinates
Set_Orthographic_Coordinates.restype = c_long
Set_Orthographic_Coordinates.argtypes = [File_Interactive, Input_Output, Orthographic_Tuple_Structure]
Get_Orthographic_Coordinates = _libraries['geotrans2.dll'].Get_Orthographic_Coordinates
Get_Orthographic_Coordinates.restype = c_long
Get_Orthographic_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Orthographic_Tuple)]
Set_Polar_Stereo_Params = _libraries['geotrans2.dll'].Set_Polar_Stereo_Params
Set_Polar_Stereo_Params.restype = c_long
Set_Polar_Stereo_Params.argtypes = [File_Interactive, Input_Output, Polar_Stereo_Structure]
Get_Polar_Stereo_Params = _libraries['geotrans2.dll'].Get_Polar_Stereo_Params
Get_Polar_Stereo_Params.restype = c_long
Get_Polar_Stereo_Params.argtypes = [File_Interactive, Input_Output, POINTER(Polar_Stereo_Parameters)]
Set_Polar_Stereo_Coordinates = _libraries['geotrans2.dll'].Set_Polar_Stereo_Coordinates
Set_Polar_Stereo_Coordinates.restype = c_long
Set_Polar_Stereo_Coordinates.argtypes = [File_Interactive, Input_Output, Polar_Stereo_Tuple_Structure]
Get_Polar_Stereo_Coordinates = _libraries['geotrans2.dll'].Get_Polar_Stereo_Coordinates
Get_Polar_Stereo_Coordinates.restype = c_long
Get_Polar_Stereo_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Polar_Stereo_Tuple)]
Set_Polyconic_Params = _libraries['geotrans2.dll'].Set_Polyconic_Params
Set_Polyconic_Params.restype = c_long
Set_Polyconic_Params.argtypes = [File_Interactive, Input_Output, Polyconic_Structure]
Get_Polyconic_Params = _libraries['geotrans2.dll'].Get_Polyconic_Params
Get_Polyconic_Params.restype = c_long
Get_Polyconic_Params.argtypes = [File_Interactive, Input_Output, POINTER(Polyconic_Parameters)]
Set_Polyconic_Coordinates = _libraries['geotrans2.dll'].Set_Polyconic_Coordinates
Set_Polyconic_Coordinates.restype = c_long
Set_Polyconic_Coordinates.argtypes = [File_Interactive, Input_Output, Polyconic_Tuple_Structure]
Get_Polyconic_Coordinates = _libraries['geotrans2.dll'].Get_Polyconic_Coordinates
Get_Polyconic_Coordinates.restype = c_long
Get_Polyconic_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Polyconic_Tuple)]
Set_Sinusoidal_Params = _libraries['geotrans2.dll'].Set_Sinusoidal_Params
Set_Sinusoidal_Params.restype = c_long
Set_Sinusoidal_Params.argtypes = [File_Interactive, Input_Output, Sinusoidal_Structure]
Get_Sinusoidal_Params = _libraries['geotrans2.dll'].Get_Sinusoidal_Params
Get_Sinusoidal_Params.restype = c_long
Get_Sinusoidal_Params.argtypes = [File_Interactive, Input_Output, POINTER(Sinusoidal_Parameters)]
Set_Sinusoidal_Coordinates = _libraries['geotrans2.dll'].Set_Sinusoidal_Coordinates
Set_Sinusoidal_Coordinates.restype = c_long
Set_Sinusoidal_Coordinates.argtypes = [File_Interactive, Input_Output, Sinusoidal_Tuple_Structure]
Get_Sinusoidal_Coordinates = _libraries['geotrans2.dll'].Get_Sinusoidal_Coordinates
Get_Sinusoidal_Coordinates.restype = c_long
Get_Sinusoidal_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Sinusoidal_Tuple)]
Set_Stereographic_Params = _libraries['geotrans2.dll'].Set_Stereographic_Params
Set_Stereographic_Params.restype = c_long
Set_Stereographic_Params.argtypes = [File_Interactive, Input_Output, Stereographic_Structure]
Get_Stereographic_Params = _libraries['geotrans2.dll'].Get_Stereographic_Params
Get_Stereographic_Params.restype = c_long
Get_Stereographic_Params.argtypes = [File_Interactive, Input_Output, POINTER(Stereographic_Parameters)]
Set_Stereographic_Coordinates = _libraries['geotrans2.dll'].Set_Stereographic_Coordinates
Set_Stereographic_Coordinates.restype = c_long
Set_Stereographic_Coordinates.argtypes = [File_Interactive, Input_Output, Stereographic_Tuple_Structure]
Get_Stereographic_Coordinates = _libraries['geotrans2.dll'].Get_Stereographic_Coordinates
Get_Stereographic_Coordinates.restype = c_long
Get_Stereographic_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Stereographic_Tuple)]
Set_Transverse_Cylindrical_Equal_Area_Params = _libraries['geotrans2.dll'].Set_Transverse_Cylindrical_Equal_Area_Params
Set_Transverse_Cylindrical_Equal_Area_Params.restype = c_long
Set_Transverse_Cylindrical_Equal_Area_Params.argtypes = [File_Interactive, Input_Output, Transverse_Cylindrical_Equal_Area_Structure]
Get_Transverse_Cylindrical_Equal_Area_Params = _libraries['geotrans2.dll'].Get_Transverse_Cylindrical_Equal_Area_Params
Get_Transverse_Cylindrical_Equal_Area_Params.restype = c_long
Get_Transverse_Cylindrical_Equal_Area_Params.argtypes = [File_Interactive, Input_Output, POINTER(Transverse_Cylindrical_Equal_Area_Parameters)]
Set_Transverse_Cylindrical_Equal_Area_Coordinates = _libraries['geotrans2.dll'].Set_Transverse_Cylindrical_Equal_Area_Coordinates
Set_Transverse_Cylindrical_Equal_Area_Coordinates.restype = c_long
Set_Transverse_Cylindrical_Equal_Area_Coordinates.argtypes = [File_Interactive, Input_Output, Transverse_Cylindrical_Equal_Area_Tuple_Structure]
Get_Transverse_Cylindrical_Equal_Area_Coordinates = _libraries['geotrans2.dll'].Get_Transverse_Cylindrical_Equal_Area_Coordinates
Get_Transverse_Cylindrical_Equal_Area_Coordinates.restype = c_long
Get_Transverse_Cylindrical_Equal_Area_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Transverse_Cylindrical_Equal_Area_Tuple)]
Set_Transverse_Mercator_Params = _libraries['geotrans2.dll'].Set_Transverse_Mercator_Params
Set_Transverse_Mercator_Params.restype = c_long
Set_Transverse_Mercator_Params.argtypes = [File_Interactive, Input_Output, Transverse_Mercator_Structure]
Get_Transverse_Mercator_Params = _libraries['geotrans2.dll'].Get_Transverse_Mercator_Params
Get_Transverse_Mercator_Params.restype = c_long
Get_Transverse_Mercator_Params.argtypes = [File_Interactive, Input_Output, POINTER(Transverse_Mercator_Parameters)]
Set_Transverse_Mercator_Coordinates = _libraries['geotrans2.dll'].Set_Transverse_Mercator_Coordinates
Set_Transverse_Mercator_Coordinates.restype = c_long
Set_Transverse_Mercator_Coordinates.argtypes = [File_Interactive, Input_Output, Transverse_Mercator_Tuple_Structure]
Get_Transverse_Mercator_Coordinates = _libraries['geotrans2.dll'].Get_Transverse_Mercator_Coordinates
Get_Transverse_Mercator_Coordinates.restype = c_long
Get_Transverse_Mercator_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Transverse_Mercator_Tuple)]
Set_UPS_Coordinates = _libraries['geotrans2.dll'].Set_UPS_Coordinates
Set_UPS_Coordinates.restype = c_long
Set_UPS_Coordinates.argtypes = [File_Interactive, Input_Output, UPS_Tuple_Structure]
Get_UPS_Coordinates = _libraries['geotrans2.dll'].Get_UPS_Coordinates
Get_UPS_Coordinates.restype = c_long
Get_UPS_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(UPS_Tuple)]
Set_USNG_Coordinates = _libraries['geotrans2.dll'].Set_USNG_Coordinates
Set_USNG_Coordinates.restype = c_long
Set_USNG_Coordinates.argtypes = [File_Interactive, Input_Output, USNG_Tuple_Structure]
Get_USNG_Coordinates = _libraries['geotrans2.dll'].Get_USNG_Coordinates
Get_USNG_Coordinates.restype = c_long
Get_USNG_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(USNG_Tuple)]
Set_UTM_Params = _libraries['geotrans2.dll'].Set_UTM_Params
Set_UTM_Params.restype = c_long
Set_UTM_Params.argtypes = [File_Interactive, Input_Output, UTM_Structure]
Get_UTM_Params = _libraries['geotrans2.dll'].Get_UTM_Params
Get_UTM_Params.restype = c_long
Get_UTM_Params.argtypes = [File_Interactive, Input_Output, POINTER(UTM_Parameters)]
Set_UTM_Coordinates = _libraries['geotrans2.dll'].Set_UTM_Coordinates
Set_UTM_Coordinates.restype = c_long
Set_UTM_Coordinates.argtypes = [File_Interactive, Input_Output, UTM_Tuple_Structure]
Get_UTM_Coordinates = _libraries['geotrans2.dll'].Get_UTM_Coordinates
Get_UTM_Coordinates.restype = c_long
Get_UTM_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(UTM_Tuple)]
Set_Van_der_Grinten_Params = _libraries['geotrans2.dll'].Set_Van_der_Grinten_Params
Set_Van_der_Grinten_Params.restype = c_long
Set_Van_der_Grinten_Params.argtypes = [File_Interactive, Input_Output, Van_der_Grinten_Structure]
Get_Van_der_Grinten_Params = _libraries['geotrans2.dll'].Get_Van_der_Grinten_Params
Get_Van_der_Grinten_Params.restype = c_long
Get_Van_der_Grinten_Params.argtypes = [File_Interactive, Input_Output, POINTER(Van_der_Grinten_Parameters)]
Set_Van_der_Grinten_Coordinates = _libraries['geotrans2.dll'].Set_Van_der_Grinten_Coordinates
Set_Van_der_Grinten_Coordinates.restype = c_long
Set_Van_der_Grinten_Coordinates.argtypes = [File_Interactive, Input_Output, Van_der_Grinten_Tuple_Structure]
Get_Van_der_Grinten_Coordinates = _libraries['geotrans2.dll'].Get_Van_der_Grinten_Coordinates
Get_Van_der_Grinten_Coordinates.restype = c_long
Get_Van_der_Grinten_Coordinates.argtypes = [File_Interactive, Input_Output, POINTER(Van_der_Grinten_Tuple)]
Convert = _libraries['geotrans2.dll'].Convert
Convert.restype = c_long
Convert.argtypes = [File_Interactive]
Get_Conversion_Errors = _libraries['geotrans2.dll'].Get_Conversion_Errors
Get_Conversion_Errors.restype = c_long
Get_Conversion_Errors.argtypes = [File_Interactive, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
Set_Conversion_Errors = _libraries['geotrans2.dll'].Set_Conversion_Errors
Set_Conversion_Errors.restype = c_long
Set_Conversion_Errors.argtypes = [File_Interactive, c_double, c_double, c_double]
Get_Conversion_Status = _libraries['geotrans2.dll'].Get_Conversion_Status
Get_Conversion_Status.restype = c_long
Get_Conversion_Status.argtypes = [File_Interactive, Input_Output, POINTER(c_long)]
Get_Conversion_Status_String = _libraries['geotrans2.dll'].Get_Conversion_Status_String
Get_Conversion_Status_String.restype = c_long
Get_Conversion_Status_String.argtypes = [File_Interactive, Input_Output, STRING, STRING]
Get_Return_Code_String = _libraries['geotrans2.dll'].Get_Return_Code_String
Get_Return_Code_String.restype = None
Get_Return_Code_String.argtypes = [c_long, STRING, STRING]
__all__ = ['Get_Oblique_Mercator_Coordinates',
           'LAMBERT_2_ORIGIN_LAT_ERROR', 'Define_Datum',
           'BONN_EASTING_ERROR', 'Set_Bonne_Coordinates',
           'WGS72_Datum_Type', 'EQCY_STDP_ERROR',
           'ENGINE_DATUM_FILE_PARSE_ERROR',
           'Azimuthal_Equidistant_Structure', 'WGS72_Datum',
           'ALBERS_INV_F_ERROR', 'OMERC_LON2_ERROR', 'ORTH_LAT_ERROR',
           'ENGINE_LON_ERROR', 'Get_Datum_Type', 'USNG_NO_ERROR',
           'MGRS_EASTING_ERROR', 'TCEA_LON_WARNING',
           'AZEQ_NORTHING_ERROR', 'GEOCENT_A_ERROR',
           'Set_UTM_Coordinates', 'TCEA_NO_ERROR',
           'Lambert_Conformal_Conic_1_Parameters', 'BONN_LON_ERROR',
           'Mercator_Tuple_Structure', 'MOLL_LAT_ERROR',
           'Polyconic_Tuple_Structure',
           'Get_Transverse_Cylindrical_Equal_Area_Params',
           'BNG_Tuple_Structure', 'NEYS_FIRST_STDP_ERROR',
           'RETURN_MSG_LENGTH', 'ELLIPSE_INVALID_INDEX_ERROR',
           'AZEQ_EASTING_ERROR', 'MGRS_NO_ERROR', 'Get_Bonne_Params',
           'DATUM_CODE_LENGTH', 'GARS_STR_15_MIN_ERROR',
           'GEOREF_LON_ERROR', 'Local_Cartesian_Tuple',
           'ENGINE_STR_LAT_MIN_ERROR', 'GNOM_INV_F_ERROR',
           'GEOID_NOT_INITIALIZED_ERROR', 'CYEQ_ORIGIN_LAT_ERROR',
           'Get_Stereographic_Coordinates', 'Stereographic',
           'MILL_CENT_MER_ERROR', 'Get_Eckert4_Coordinates',
           'TRANMERC_SCALE_FACTOR_ERROR',
           'Cylindrical_Equal_Area_Tuple',
           'Lambert_Conformal_Conic_2_Tuple_Structure',
           'Lambert_Conformal_Conic_1_Tuple',
           'ELLIPSE_TABLE_OVERFLOW_ERROR', 'Set_Datum', 'UPS_A_ERROR',
           'LAMBERT_1_A_ERROR', 'Get_Coordinate_System_Type',
           'GRIN_NO_ERROR', 'ELLIPSE_INV_F_ERROR',
           'MILL_EASTING_ERROR', 'Mercator_Structure',
           'Set_Local_Cartesian_Coordinates',
           'Set_Van_der_Grinten_Coordinates', 'MGRS_LON_ERROR',
           'USNG_INV_F_ERROR', 'Set_Sinusoidal_Coordinates',
           'Eckert6_Structure', 'Get_NZMG_Coordinates',
           'DATUM_7PARAM_FILE_OPEN_ERROR', 'BONN_INV_F_ERROR',
           'ALBERS_A_ERROR', 'Get_GEOREF_Coordinates',
           'DATUM_3PARAM_FILE_OPEN_ERROR',
           'Convert_Ellipsoid_To_MSL_EGM84_10D_BL_Height',
           'CYEQ_INV_F_ERROR', 'Neys',
           'Get_Equidistant_Cylindrical_Coordinates',
           'Polyconic_Parameters', 'GEOREF_STR_LAT_ERROR',
           'Get_Local_Cartesian_Params', 'Get_Datum_Name',
           'CASS_LON_ERROR', 'Orthographic_Parameters',
           'Set_Mollweide_Coordinates', 'BNG_LAT_ERROR',
           'Eckert4_Tuple_Structure', 'Eckert6_Tuple_Structure',
           'OMERC_NORTHING_ERROR', 'ELLIPSE_NO_ERROR',
           'Set_MGRS_Coordinates', 'MOLL_NO_ERROR',
           'MOLL_INV_F_ERROR', 'STEREO_LAT_ERROR',
           'ELLIPSE_FILE_OPEN_ERROR', 'DATUM_LAT_ERROR',
           'EQCY_INV_F_ERROR', 'BNG_NORTHING_ERROR', 'MGRS',
           'ORTH_RADIUS_ERROR', 'ENGINE_LON2_ERROR',
           'Set_Stereographic_Params', 'Polar_Stereo_Structure',
           'LAMBERT_2_SCALE_FACTOR_ERROR', 'Get_Neys_Coordinates',
           'ALBERS_EASTING_ERROR', 'Set_Sinusoidal_Params',
           'ENGINE_A_ERROR',
           'Get_Transverse_Cylindrical_Equal_Area_Coordinates',
           'ECK4_A_ERROR', 'Get_Albers_Equal_Area_Conic_Coordinates',
           'Input', 'Sinusoidal_Tuple_Structure',
           'OMERC_SCALE_FACTOR_ERROR', 'RED',
           'Get_Van_der_Grinten_Params', 'ENGINE_NORTHING_ERROR',
           'Set_Orthographic_Params', 'Set_Polar_Stereo_Params',
           'USNG_LAT_WARNING', 'Geodetic_Tuple',
           'Set_Transverse_Mercator_Params',
           'Get_Oblique_Mercator_Params', 'NZMG_EASTING_ERROR',
           'ALBERS_LAT_ERROR', 'Albers_Equal_Area_Conic',
           'GEOID_FILE_OPEN_ERROR', 'Stereographic_Structure',
           'Set_Lambert_Conformal_Conic_1_Params', 'BNG_LON_ERROR',
           'Set_Lambert_Conformal_Conic_2_Coordinates',
           'Get_Lambert_Conformal_Conic_2_Coordinates',
           'Polar_Stereo_Tuple_Structure',
           'Get_Sinusoidal_Coordinates', 'OMERC_LON1_ERROR',
           'Get_Azimuthal_Equidistant_Coordinates',
           'NEYS_NORTHING_ERROR', 'TCEA_LAT_ERROR',
           'Get_Miller_Cylindrical_Coordinates',
           'ENGINE_INVALID_CODE_ERROR', 'ALBERS_CENT_MER_ERROR',
           'CYEQ_NORTHING_ERROR', 'GRIN_EASTING_ERROR',
           'Get_UTM_Params', 'Lambert_Conformal_Conic_2_Tuple',
           'BNG_ELLIPSOID_ERROR', 'DATUM_INVALID_SRC_INDEX_ERROR',
           'Set_Equidistant_Cylindrical_Params', 'Eckert4_Tuple',
           'GARS_PRECISION_ERROR', 'ELLIPSE_NOT_INITIALIZED_ERROR',
           'Get_Bonne_Coordinates', 'DATUM_LON_ERROR', 'GREEN',
           'CYEQ_LAT_ERROR', 'CASS_INV_F_ERROR', 'MERC_LAT_ERROR',
           'Azimuthal_Equidistant_Tuple', 'Input_Output',
           'ENGINE_ORIGIN_LAT_ERROR', 'OMERC_A_ERROR',
           'Oblique_Mercator', 'Get_Gnomonic_Coordinates',
           'DATUM_ELLIPSE_ERROR',
           'Cylindrical_Equal_Area_Tuple_Structure', 'YELLOW',
           'ENGINE_ELLIPSOID_OVERFLOW', 'Orthographic_Structure',
           'ENGINE_INVALID_DIRECTION', 'AZEQ_ORIGIN_LAT_ERROR',
           'EQCY_NORTHING_ERROR', 'Sinusoidal_Structure',
           'MERC_A_ERROR', 'LOCCART_ORIENTATION_ERROR',
           'MGRS_ZONE_ERROR', 'SINU_NORTHING_ERROR',
           'Get_Conversion_Errors', 'Bonne',
           'ENGINE_NOT_USERDEF_ERROR', 'Get_Mercator_Coordinates',
           'Set_Transverse_Cylindrical_Equal_Area_Coordinates',
           'Sinusoidal', 'ECK6_CENT_MER_ERROR', 'Orthographic_Tuple',
           'ELLIPSE_INITIALIZE_ERROR', 'Precision', 'GARS_LAT_ERROR',
           'GARS_Tuple_Structure', 'ELLIPSE_IN_USE_ERROR',
           'TCEA_INV_F_ERROR', 'Get_Ellipsoid_Name', 'NZMG_NO_ERROR',
           'Lambert_Conformal_Conic_2', 'File', 'Cassini',
           'Miller_Cylindrical_Tuple_Structure',
           'Orthographic_Tuple_Structure',
           'Convert_Ellipsoid_To_MSL_EGM84_10D_NS_Height',
           'ECK4_LON_ERROR', 'Get_Ellipsoid_Index', 'TCEA_LON_ERROR',
           'Van_der_Grinten_Tuple_Structure', 'Precisions',
           'POLY_INV_F_ERROR', 'UTM_Tuple_Structure',
           'Gnomonic_Structure', 'NEYS_LON_ERROR',
           'EQCY_EASTING_ERROR', 'GEOREF_NO_ERROR',
           'Get_Transverse_Mercator_Params', 'USNG_ZONE_ERROR',
           'Bonne_Structure', 'Set_Oblique_Mercator_Coordinates',
           'DATUM_SCALE_ERROR', 'Ten_Seconds',
           'Get_Equidistant_Cylindrical_Params',
           'BONN_CENT_MER_ERROR', 'UTM_A_ERROR', 'Height_Types',
           'Set_Eckert4_Coordinates', 'NEYS_INV_F_ERROR',
           'Geocentric_Tuple', 'GARS_STR_5_MIN_ERROR',
           'GNOM_LAT_ERROR', 'POLAR_INV_F_ERROR',
           'GRIN_CENT_MER_ERROR', 'UTM_INV_F_ERROR', 'No_Height',
           'Set_Precision', 'ENGINE_INPUT_WARNING', 'MERC_NO_ERROR',
           'ENGINE_OUTPUT_WARNING', 'OMERC_INV_F_ERROR',
           'CYEQ_NO_ERROR', 'Geodetic_Tuple_Structure',
           'Remove_Ellipsoid', 'DATUM_3PARAM_FILE_PARSING_ERROR',
           'POLY_LON_WARNING', 'Oblique_Mercator_Tuple',
           'USNG_LAT_ERROR', 'Height_Type', 'Datum_Types',
           'POLAR_LAT_ERROR', 'DATUM_NAME_LENGTH',
           'Set_Van_der_Grinten_Params', 'Orthographic',
           'OMERC_LAT2_ERROR', 'UTM_ZONE_ERROR', 'Get_Datum',
           'Define_Ellipsoid', 'UPS_INV_F_ERROR', 'Get_Precision',
           'Get_Geodetic_Coordinates',
           'Albers_Equal_Area_Conic_Structure', 'ENGINE_STRING_ERROR',
           'ELLIPSE_NOT_USERDEF_ERROR', 'Bonne_Tuple_Structure',
           'Get_BNG_Coordinates',
           'Set_Lambert_Conformal_Conic_1_Coordinates',
           'Cassini_Parameters', 'ALBERS_FIRST_STDP_ERROR',
           'Three_Param_Datum_Type', 'TCEA_ORIGIN_LAT_ERROR',
           'MSL_EGM84_10D_NS_Height', 'ENGINE_DATUM_WARNING',
           'Get_Cassini_Params', 'LAMBERT_2_LON_ERROR',
           'UTM_HEMISPHERE_ERROR', 'CYEQ_CENT_MER_ERROR',
           'MOLL_A_ERROR', 'USNG_A_ERROR',
           'Geocentric_Tuple_Structure', 'POLY_EASTING_ERROR',
           'AZEQ_LON_ERROR', 'GARS_NO_ERROR', 'POLAR_NORTHING_ERROR',
           'BNG_Tuple', 'GARS_STR_LAT_ERROR',
           'OMERC_ORIGIN_LAT_ERROR', 'DATUM_NO_ERROR',
           'OMERC_LON_WARNING', 'Get_Miller_Cylindrical_Params',
           'DATUM_NOT_USERDEF_ERROR', 'ENGINE_INVALID_TYPE',
           'Transverse_Cylindrical_Equal_Area_Tuple',
           'Check_Datum_User_Defined', 'MOLL_LON_ERROR',
           'Set_Orthographic_Coordinates', 'AZEQ_CENT_MER_ERROR',
           'File_Interactive', 'SINU_INV_F_ERROR', 'AZEQ_LAT_ERROR',
           'BNG_INVALID_AREA_ERROR', 'Set_Stereographic_Coordinates',
           'Van_der_Grinten_Parameters', 'Eckert4_Parameters',
           'Azimuthal_Equidistant_Tuple_Structure',
           'ENGINE_DATUM_DOMAIN_ERROR', 'LAMBERT_2_FIRST_STDP_ERROR',
           'TCEA_NORTHING_ERROR', 'MOLL_NORTHING_ERROR',
           'POLY_A_ERROR', 'Get_Orthographic_Params',
           'ENGINE_OUTPUT_ERROR', 'CYEQ_LON_ERROR',
           'Local_Cartesian_Parameters', 'Get_Datum_Code',
           'GRIN_A_ERROR', 'LOCCART_INV_F_ERROR', 'Get_Neys_Params',
           'TCEA_EASTING_ERROR', 'ENGINE_ELLIPSE_IN_USE_ERROR',
           'ELLIPSE_INVALID_CODE_ERROR', 'LAMBERT_1_EASTING_ERROR',
           'NEYS_NO_ERROR', 'ENGINE_ZONE_ERROR', 'Cassini_Structure',
           'LAMBERT_2_INV_F_ERROR', 'MERC_EASTING_ERROR',
           'MERC_INV_F_ERROR', 'TRANMERC_CENT_MER_ERROR',
           'GNOM_CENT_MER_ERROR', 'Remove_Datum',
           'Set_Coordinate_System', 'EQCY_LON_ERROR',
           'Polyconic_Structure', 'MOLL_CENT_MER_ERROR',
           'Polyconic_Tuple',
           'Set_Equidistant_Cylindrical_Coordinates',
           'ELLIPSE_A_ERROR', 'NZMG_LAT_ERROR',
           'DATUM_NOT_INITIALIZED_ERROR',
           'Set_Oblique_Mercator_Params', 'Initialize_Geoid',
           'ENGINE_SCALE_FACTOR_ERROR', 'ECK6_A_ERROR',
           'MGRS_LAT_ERROR', 'Neys_Structure',
           'Get_Sinusoidal_Params', 'ECK4_CENT_MER_ERROR',
           'Get_Datum_Valid_Rectangle', 'LAMBERT_1_NO_ERROR',
           'GEOREF_Tuple_Structure', 'Convert', 'GRIN_NORTHING_ERROR',
           'Neys_Parameters', 'POLY_CENT_MER_ERROR',
           'ALBERS_NORTHING_ERROR', 'BNG_STRING_ERROR',
           'BONN_A_ERROR', 'ECK6_INV_F_ERROR', 'BNG_NO_ERROR',
           'Cylindrical_Equal_Area', 'DATUM_INVALID_INDEX_ERROR',
           'ORTH_ORIGIN_LAT_ERROR', 'Get_Ellipsoid_Count',
           'UPS_EASTING_ERROR', 'GRIN_INV_F_ERROR',
           'Set_Cassini_Params',
           'Transverse_Cylindrical_Equal_Area_Parameters',
           'Stereographic_Tuple', 'ALBERS_LON_ERROR', 'MGRS_A_ERROR',
           'MGRS_NORTHING_ERROR', 'Gnomonic', 'ORTH_EASTING_ERROR',
           'Set_Azimuthal_Equidistant_Params', 'POLY_NO_ERROR',
           'Lambert_Conformal_Conic_1', 'LOCCART_A_ERROR',
           'USNG_STRING_ERROR', 'Sinusoidal_Tuple',
           'DATUM_SIGMA_ERROR', 'MGRS_STRING_ERROR', 'Mercator',
           'Define_Datum_Type', 'LAMBERT_2_NORTHING_ERROR',
           'UTM_ZONE_OVERRIDE_ERROR', 'TRANMERC_LON_WARNING',
           'MILL_LAT_ERROR', 'UTM_NO_ERROR', 'BONN_LAT_ERROR',
           'Set_Lambert_Conformal_Conic_2_Params',
           'ENGINE_GEOID_ERROR', 'LAMBERT_2_SECOND_STDP_ERROR',
           'LAMBERT_2_EASTING_ERROR', 'Check_Ellipsoid_User_Defined',
           'ECK4_LAT_ERROR', 'OMERC_DIFF_HEMISPHERE_ERROR',
           'Thousandth_of_Second',
           'Albers_Equal_Area_Conic_Parameters', 'Polar_Stereo_Tuple',
           'Three_Param_Datum', 'Set_Polar_Stereo_Coordinates',
           'Set_NZMG_Coordinates', 'Gnomonic_Tuple',
           'Gnomonic_Tuple_Structure', 'GEOCENT_NO_ERROR',
           'Set_Gnomonic_Coordinates', 'AZEQ_PROJECTION_ERROR',
           'Set_Neys_Coordinates', 'ORTH_NO_ERROR',
           'Set_Cylindrical_Equal_Area_Coordinates',
           'Lambert_Conformal_Conic_2_Structure',
           'Cassini_Tuple_Structure', 'ENGINE_LAT_ERROR',
           'Get_Van_der_Grinten_Coordinates', 'ORTH_NORTHING_ERROR',
           'Set_Miller_Cylindrical_Coordinates',
           'GEOREF_STR_LON_MIN_ERROR', 'UTM_Structure',
           'LOCCART_LAT_ERROR', 'Get_Coordinate_System',
           'USNG_NORTHING_ERROR', 'Mollweide_Structure',
           'Get_GARS_Coordinates', 'EQCY_LAT_ERROR',
           'Get_Lambert_Conformal_Conic_1_Coordinates', 'BNG',
           'Get_Mollweide_Params', 'TCEA_CENT_MER_ERROR',
           'DATUM_INVALID_CODE_ERROR', 'MGRS_PRECISION_ERROR',
           'Get_Lambert_Conformal_Conic_1_Params',
           'LAMBERT_2_CENT_MER_ERROR', 'BNG_EASTING_ERROR',
           'Set_Albers_Equal_Area_Conic_Params',
           'Equidistant_Cylindrical_Tuple_Structure',
           'USNG_HEMISPHERE_ERROR', 'CASS_LAT_ERROR',
           'MILL_LON_ERROR', 'Get_Eckert6_Coordinates',
           'Get_Geodetic_Params', 'CASS_NO_ERROR',
           'Set_GARS_Coordinates', 'Get_Eckert4_Params',
           'ENGINE_GEOID_FILE_PARSE_ERROR',
           'Transverse_Mercator_Parameters', 'TRANMERC_EASTING_ERROR',
           'LAMBERT_2_HEMISPHERE_ERROR',
           'Transverse_Mercator_Structure', 'MGRS_INV_F_ERROR',
           'Set_GEOREF_Coordinates', 'COORD_SYS_NAME_LENGTH',
           'Get_Ellipsoid_Code', 'LAMBERT_1_LAT_ERROR', 'Geocentric',
           'Van_der_Grinten_Structure',
           'Get_Conversion_Status_String', 'STEREO_NO_ERROR',
           'GNOM_LON_ERROR', 'GEOCENT_LAT_ERROR', 'Minute',
           'Get_Cylindrical_Equal_Area_Params', 'MERC_NORTHING_ERROR',
           'CASS_ORIGIN_LAT_ERROR', 'CASS_EASTING_ERROR',
           'DATUM_7PARAM_FILE_PARSING_ERROR', 'MGRS_LAT_WARNING',
           'UPS_HEMISPHERE_ERROR', 'CASS_CENT_MER_ERROR',
           'ENGINE_PROJECTION_ERROR', 'Geodetic_Parameters',
           'SINU_EASTING_ERROR', 'Get_Coordinate_System_Index',
           'ALBERS_SECOND_STDP_ERROR', 'Datum_Type',
           'LOCCART_LON_ERROR', 'UPS_Tuple_Structure',
           'LAMBERT_1_CENT_MER_ERROR', 'NEYS_LAT_ERROR',
           'ENGINE_HEMISPHERE_ERROR', 'TRANMERC_NO_ERROR',
           'Get_Albers_Equal_Area_Conic_Params', 'Coordinate_Types',
           'LAMBERT_1_SCALE_FACTOR_ERROR', 'SINU_NO_ERROR',
           'MSL_EGM84_10D_BL_Height', 'ORTH_INV_F_ERROR',
           'Get_Eckert6_Params', 'ENGINE_FIRST_SECOND_ERROR',
           'Set_USNG_Coordinates', 'Get_Gnomonic_Params',
           'Set_BNG_Coordinates', 'ECK4_NO_ERROR', 'Bonne_Parameters',
           'Polyconic', 'GARS_STR_ERROR', 'Get_Datum_Errors',
           'Miller_Cylindrical_Parameters', 'Degree',
           'Oblique_Mercator_Parameters', 'UTM_Parameters',
           'COORD_SYS_CODE_LENGTH', 'MILL_NORTHING_ERROR', 'GARS',
           'TCEA_SCALE_FACTOR_ERROR', 'ENGINE_ORIGIN_LON_ERROR',
           'LAMBERT_1_NORTHING_ERROR', 'POLAR_NO_ERROR',
           'Define_Datum_Types', 'Van_der_Grinten_Tuple',
           'ECK4_INV_F_ERROR', 'Get_USNG_Coordinates',
           'Eckert6_Parameters', 'Get_Azimuthal_Equidistant_Params',
           'Transverse_Cylindrical_Equal_Area_Structure', 'UPS_Tuple',
           'Get_Lambert_Conformal_Conic_2_Params',
           'ENGINE_INVALID_INDEX_ERROR',
           'Cylindrical_Equal_Area_Parameters',
           'Set_Mollweide_Params', 'Ellipsoid_Height',
           'GEOREF_STR_ERROR', 'ENGINE_LAT2_ERROR',
           'ENGINE_DATUM_SIGMA_ERROR', 'Set_Local_Cartesian_Params',
           'ENGINE_ELLIPSOID_CODE_ERROR', 'Set_Eckert6_Params',
           'Set_Bonne_Params', 'USNG', 'Get_Ellipsoid_Eccentricity2',
           'Get_Conversion_Status', 'GARS_LON_ERROR',
           'NUMBER_COORD_SYS',
           'Lambert_Conformal_Conic_1_Tuple_Structure',
           'OMERC_EASTING_ERROR', 'UPS_LAT_ERROR', 'GEOID_NO_ERROR',
           'Valid_Conversion', 'Albers_Equal_Area_Conic_Tuple',
           'NZMG_ELLIPSOID_ERROR', 'BONN_NORTHING_ERROR',
           'Get_UPS_Coordinates', 'ENGINE_ELLIPSOID_ERROR',
           'OMERC_LAT_ERROR', 'ENGINE_EASTING_ERROR',
           'Miller_Cylindrical_Structure', 'ALBERS_HEMISPHERE_ERROR',
           'CASS_A_ERROR', 'MILL_A_ERROR', 'ENGINE_RADIUS_ERROR',
           'Set_Eckert6_Coordinates', 'LAMBERT_2_NO_ERROR',
           'Azimuthal_Equidistant', 'DATUM_DOMAIN_ERROR',
           'Set_Cassini_Coordinates', 'LAMBERT_1_INV_F_ERROR',
           'STEREO_EASTING_ERROR', 'MGRS_Tuple_Structure',
           'ENGINE_DATUM_ERROR', 'ECK4_EASTING_ERROR',
           'Miller_Cylindrical', 'ENGINE_INVALID_AREA_ERROR',
           'Mollweide_Tuple_Structure', 'Get_MGRS_Coordinates',
           'ENGINE_CENT_MER_ERROR', 'ALBERS_NO_ERROR',
           'GNOM_EASTING_ERROR', 'OMERC_LAT1_LAT2_ERROR',
           'ORTH_LON_ERROR',
           'Convert_Ellipsoid_To_MSL_EGM96_VG_NS_Height',
           'ENGINE_INPUT_ERROR', 'STEREO_A_ERROR',
           'Gnomonic_Parameters', 'Local_Cartesian',
           'LAMBERT_1_ORIGIN_LAT_ERROR', 'TRANMERC_NORTHING_ERROR',
           'Get_Mercator_Params', 'ORTH_CENT_MER_ERROR',
           'TRANMERC_LON_ERROR', 'Get_Polar_Stereo_Coordinates',
           'ENGINE_STDP_ERROR', 'UTM', 'ECK6_NO_ERROR',
           'Get_Datum_Seven_Parameters', 'GARS_Tuple',
           'NZMG_LON_ERROR', 'Set_Mercator_Params',
           'Equidistant_Cylindrical_Parameters',
           'Get_Local_Cartesian_Coordinates', 'USNG_LON_ERROR',
           'Eckert6_Tuple', 'Mollweide_Parameters',
           'GNOM_NORTHING_ERROR', 'GRIN_LAT_ERROR', 'MERC_LON_ERROR',
           'MGRS_Tuple', 'POLY_ORIGIN_LAT_ERROR',
           'TRANMERC_INV_F_ERROR', 'MGRS_HEMISPHERE_ERROR',
           'ALBERS_FIRST_SECOND_ERROR', 'Ten_Minutes',
           'Set_Eckert4_Params', 'ELLIPSOID_CODE_LENGTH',
           'Oblique_Mercator_Structure', 'USNG_EASTING_ERROR',
           'Get_Geocentric_Coordinates', 'Get_Stereographic_Params',
           'USNG_PRECISION_ERROR', 'SINU_LAT_ERROR',
           'TRANMERC_ORIGIN_LAT_ERROR', 'Polar_Stereo_Parameters',
           'CONVERT_MSG_LENGTH', 'DATUM_INVALID_DEST_INDEX_ERROR',
           'GNOM_ORIGIN_LAT_ERROR', 'CASS_NORTHING_ERROR',
           'Initialize_Engine', 'TCEA_A_ERROR', 'MILL_NO_ERROR',
           'SINU_LON_ERROR', 'UTM_EASTING_ERROR', 'UTM_Tuple',
           'UPS_NORTHING_ERROR', 'Mercator_Parameters',
           'Azimuthal_Equidistant_Parameters', 'MOLL_EASTING_ERROR',
           'STEREO_NORTHING_ERROR', 'Set_UPS_Coordinates',
           'GNOM_NO_ERROR', 'Mercator_Tuple',
           'Miller_Cylindrical_Tuple', 'ENGINE_NO_ERROR',
           'GEOREF_Tuple', 'STEREO_LON_ERROR', 'Get_Datum_Index',
           'POLY_NORTHING_ERROR', 'Set_Geocentric_Coordinates',
           'ENGINE_INVALID_STATE', 'Get_Datum_Three_Parameters',
           'Get_Datum_Count', 'USNG_Tuple',
           'ENGINE_SECOND_STDP_ERROR', 'Set_Mercator_Coordinates',
           'GRIN_RADIUS_ERROR', 'ORTH_A_ERROR', 'BONN_NO_ERROR',
           'EQCY_A_ERROR', 'STEREO_INV_F_ERROR', 'AZEQ_A_ERROR',
           'Transverse_Mercator_Tuple_Structure', 'Neys_Tuple',
           'ELLIPSOID_NAME_LENGTH', 'Mollweide_Tuple',
           'Coordinate_Type', 'STEREO_ORIGIN_LAT_ERROR',
           'USNG_Tuple_Structure', 'ENGINE_STR_LON_MIN_ERROR',
           'Set_Conversion_Errors', 'Equidistant_Cylindrical_Tuple',
           'DATUM_ROTATION_ERROR', 'Eckert4_Structure',
           'OMERC_NO_ERROR', 'LAMBERT_2_LAT_ERROR', 'Eckert4',
           'Bonne_Tuple', 'Eckert6', 'WGS84_Datum_Type',
           'Input_or_Output', 'NZMG', 'Transverse_Mercator_Tuple',
           'Set_Azimuthal_Equidistant_Coordinates',
           'Check_Valid_Datum', 'ENGINE_FIRST_STDP_ERROR',
           'UTM_LAT_ERROR', 'OMERC_LON_ERROR', 'WGS84_Datum',
           'GEOID_LON_ERROR', 'Local_Cartesian_Tuple_Structure',
           'Get_Mollweide_Coordinates', 'NEYS_A_ERROR',
           'Local_Cartesian_Structure', 'Stereographic_Parameters',
           'Hundredth_of_Second', 'NEYS_EASTING_ERROR',
           'GEOREF_STR_LAT_MIN_ERROR', 'POLAR_A_ERROR',
           'MERC_CENT_MER_ERROR', 'LAMBERT_2_A_ERROR',
           'Oblique_Mercator_Tuple_Structure', 'File_or_Interactive',
           'AZEQ_NO_ERROR', 'Geodetic',
           'Set_Transverse_Mercator_Coordinates',
           'Get_Transverse_Mercator_Coordinates', 'UPS', 'Mollweide',
           'Get_Datum_Ellipsoid_Code', 'Geoid_or_MSL_Height',
           'Van_der_Grinten', 'Seven_Param_Datum_Type',
           'POLAR_ORIGIN_LAT_ERROR', 'NZMG_Tuple',
           'Geodetic_Structure', 'Equidistant_Cylindrical_Structure',
           'GNOM_A_ERROR', 'LAMBERT_2_FIRST_SECOND_ERROR',
           'Get_Polyconic_Coordinates', 'TRANMERC_LAT_ERROR',
           'Transverse_Cylindrical_Equal_Area_Tuple_Structure',
           'GEOID_INITIALIZE_ERROR', 'ENGINE_NOT_INITIALIZED',
           'POLAR_EASTING_ERROR', 'ENGINE_LAT1_ERROR',
           'Get_Return_Code_String', 'Set_UTM_Params',
           'Get_Coordinate_System_Name', 'TRANMERC_A_ERROR',
           'BONN_ORIGIN_LAT_ERROR', 'UPS_NO_ERROR',
           'Set_Polyconic_Coordinates', 'ECK4_NORTHING_ERROR',
           'NEYS_ORIGIN_LAT_ERROR', 'GRIN_LON_ERROR',
           'GEOCENT_LON_ERROR', 'Set_Neys_Params',
           'ECK6_NORTHING_ERROR', 'Neys_Tuple_Structure',
           'Set_Polyconic_Params', 'GEOREF_PRECISION_ERROR',
           'DATUM_3PARAM_OVERFLOW_ERROR', 'Set_Gnomonic_Params',
           'GEOID_LAT_ERROR', 'LOCCART_ORIGIN_LAT_ERROR',
           'Tenth_of_Second', 'ENGINE_LON1_ERROR',
           'Set_Geodetic_Coordinates',
           'Lambert_Conformal_Conic_2_Parameters',
           'Set_Geodetic_Params', 'ENGINE_DATUM_OVERFLOW',
           'SINU_A_ERROR', 'Set_Albers_Equal_Area_Conic_Coordinates',
           'Set_Cylindrical_Equal_Area_Params', 'AZEQ_INV_F_ERROR',
           'NZMG_Tuple_Structure', 'Cassini_Tuple', 'Interactive',
           'UTM_LON_ERROR', 'CASS_LON_WARNING', 'Get_UTM_Coordinates',
           'POLAR_RADIUS_ERROR',
           'Albers_Equal_Area_Conic_Tuple_Structure',
           'Get_Ellipsoid_Parameters', 'ENGINE_LAT1_LAT2_ERROR',
           'ENGINE_ZONE_OVERRIDE_ERROR', 'OMERC_LAT1_ERROR',
           'GARS_STR_LON_ERROR', 'EQCY_CENT_MER_ERROR',
           'Get_Coordinate_System_Code', 'UPS_LON_ERROR',
           'ENGINE_LAT_WARNING', 'Transverse_Mercator',
           'NEYS_SCALE_FACTOR_ERROR', 'Polar_Stereo',
           'Get_Cylindrical_Equal_Area_Coordinates',
           'UTM_NORTHING_ERROR', 'POLAR_ORIGIN_LON_ERROR',
           'MSL_EGM96_VG_NS_Height', 'LOCCART_ORIGIN_LON_ERROR',
           'Ten_Thousandth_of_Second', 'Get_Orthographic_Coordinates',
           'LAMBERT_1_LON_ERROR', 'CYEQ_EASTING_ERROR',
           'CYEQ_A_ERROR', 'MILL_INV_F_ERROR',
           'Set_Miller_Cylindrical_Params', 'Get_Polyconic_Params',
           'POLY_LAT_ERROR', 'GEOCENT_INV_F_ERROR',
           'GEOREF_STR_LON_ERROR', 'Get_Cassini_Coordinates',
           'ECK6_LON_ERROR', 'Transverse_Cylindrical_Equal_Area',
           'EQCY_NO_ERROR',
           'Set_Transverse_Cylindrical_Equal_Area_Params',
           'Sinusoidal_Parameters', 'ECK6_EASTING_ERROR',
           'SINU_CENT_MER_ERROR', 'LOCCART_NO_ERROR',
           'ENGINE_LON_WARNING', 'POLY_LON_ERROR',
           'STEREO_CENT_MER_ERROR', 'Seven_Param_Datum',
           'Convert_Ellipsoid_To_Geoid_Height',
           'ALBERS_ORIGIN_LAT_ERROR', 'NEYS_CENT_MER_ERROR',
           'Cylindrical_Equal_Area_Structure', 'GEOREF', 'Output',
           'POLAR_LON_ERROR', 'MERC_LAT_OF_TRUE_SCALE_ERROR',
           'DATUM_7PARAM_OVERFLOW_ERROR', 'ECK6_LAT_ERROR',
           'NZMG_NORTHING_ERROR', 'Get_Polar_Stereo_Params',
           'Lambert_Conformal_Conic_1_Structure',
           'Get_Coordinate_System_Count', 'Second',
           'GEOREF_LAT_ERROR', 'Equidistant_Cylindrical',
           'Stereographic_Tuple_Structure']
