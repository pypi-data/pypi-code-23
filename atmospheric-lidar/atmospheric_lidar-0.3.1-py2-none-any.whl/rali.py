import radiometer

from licel import LicelLidarMeasurement

import rali_netcdf_parameters

class RaliLidarMeasurement(LicelLidarMeasurement):
    extra_netcdf_parameters = rali_netcdf_parameters
    
    def get_PT(self):
        ''' Gets the pressure and temperature from Radiometer data.
        If no data file is found, mean values from past measurements are 
        used.
        '''
        
        start_time = self.info['start_time']
        stop_time = self.info['stop_time']
        dt = stop_time - start_time
        mean_time = start_time + dt/2
        
        meteo_triplet = radiometer.get_mean_PT(mean_time)
        
        if meteo_triplet:
            pressure, temperature, humidity = meteo_triplet
        else:
            print "Radiometer meteo data not available. Using past values."
            pressure = radiometer.P_mean[mean_time.month - 1, mean_time.hour]
            temperature = radiometer.T_mean[mean_time.month - 1, mean_time.hour]
            
        self.info['Temperature'] = temperature - 273.15
        self.info['Pressure'] = pressure


