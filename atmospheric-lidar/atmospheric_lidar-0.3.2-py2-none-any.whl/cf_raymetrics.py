from licel import LicelLidarMeasurement

import cf_netcdf_parameters

class CfLidarMeasurement(LicelLidarMeasurement):
    
    extra_netcdf_parameters = cf_netcdf_parameters
