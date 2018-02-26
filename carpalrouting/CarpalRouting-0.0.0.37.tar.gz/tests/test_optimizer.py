import os, sys
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path + '/../') 
import unittest
from carpalrouting.optimize import Routing
from carpalrouting.models import Driver, Location, Coordinates
from carpalrouting.grouping import DriverGrouping, LocationGrouping
import time


class TestOptimizer(unittest.TestCase):   
    def test_optimization_with_predefined_data(self):
        drivers = [{'id':1,'time_slots': [[32400, 64800]], 'capacity': 3, 'speed': 30},            
                   {'id':2,'time_slots': [[32400, 64800]], 'capacity': 3, 'speed': 30}, 
                   {'id':3,'time_slots': [[32400, 64800]], 'capacity': 3, 'speed': 30}, 
                   {'id':4,'time_slots': [[32400, 64800]], 'capacity': 3, 'speed': 30}, 
                   {'id':5,'time_slots': [[32400, 64800]], 'capacity': 3, 'speed': 30},
                   {'id':6,'time_slots': [[32400, 64800]], 'capacity': 15, 'speed': 30}, 
                   {'id':7,'time_slots': [[32400, 64800]], 'capacity': 15, 'speed': 30}, 
                   {'id':8,'time_slots': [[32400, 84000]], 'capacity': 15, 'speed': 30}, 
                   {'id':9,'time_slots': [[32400, 84000]], 'capacity': 15, 'speed': 30}]
           
        locations = {'Fishermall, Diliman, Quezon City': {
                    (50400, 54000): [
                        {'address': 'Fishermall, Diliman, Quezon City', 'coordinates': [14.6336204, 121.0193792], 'delivery_window': [50400, 54000], 'capacity': 0, 'order_time': 0, 'ref': '32'}, 
                        {'address': '81F Madasalin St Teachers Village East Diliman, Quezon City', 'coordinates': [14.6410582, 121.0591618], 'delivery_window': [57600, 64800], 'capacity': 2, 'order_time': 0, 'ref': '31'}], 
                    (32400, 36000): [
                        {'address': 'Fishermall, Diliman, Quezon City', 'coordinates': [14.6336204, 121.0193792], 'delivery_window': [32400, 36000], 'capacity': 0, 'order_time': 0, 'ref': '30'}, 
                        {'address': 'Pacific Rim Cor. Commerce Ave., Filinvest City, Alabang, Muntinlupa City, 1781 Metro Manila, Philippines', 'coordinates': [14.4200106, 121.033259], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '29'}, 
                        {'address': '4 Kamias Rd, Diliman, Quezon City, Metro Manila', 'coordinates': [14.6310151, 121.0467182], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '1'}, 		
                        {'address': '30 Humility St Multinational Village, Paranaque', 'coordinates': [14.4804117, 121.0048727], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '2'}, 		
                        {'address': '7 Marymount La Vista, Quezon City', 'coordinates': [14.6297431, 121.0907328], 'delivery_window': [39600, 46800], 'capacity': 2, 'order_time': 0, 'ref': '3'}, 
                        {'address': 'Blk 6 lot 13 kalayaan village, brgy. 201, Pasay', 'coordinates': [14.507602, 121.029081], 'delivery_window': [39600, 46800], 'capacity': 2, 'order_time': 0, 'ref': '4'}, 
                        {'address': 'Barangay 34, Maypajo, Caloocan, Metro Manila, Philippines', 'coordinates': [14.6367721, 120.9729332], 'delivery_window': [39600, 46800], 'capacity': 2, 'order_time': 0, 'ref': '5'}, 		
                        {'address': '2611 Taft Ave, Barangay 68, Pasay City', 'coordinates':[14.5783882, 120.986897], 'delivery_window': [39600, 46800], 'capacity': 2, 'order_time': 0, 'ref': '6'}, 
                        {'address': '1838 Yakal St, Manila, 237', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [39600, 46800], 'capacity': 4, 'order_time': 0, 'ref': '7'}, 
                        {'address': '1838 Yakal St 237, Manila', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [39600, 46800], 'capacity': 4, 'order_time': 0, 'ref': '8'}, 
                        {'address': '18 Molave St., Marietta-Romeo Village, Brgy Sta Lucia, Pasig', 'coordinates': [14.5815801, 121.1017699], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '9'}, 
                        {'address': '86E Cotabato St. Bago Bantay Alicia, Quezon City', 'coordinates': [14.6619823, 121.0235792], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '10'}, 		
                        {'address': 'BLK 10 Lot 7 Cor Chesa St Model Community, Bgy 120, Zone 009 Tondo, Manila, Philippines', 'coordinates': [14.6205654, 120.9637766], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '11'}, 
                        {'address': 'Le Gran Condominium Eisenhower St. Greenhills, San Juan', 'coordinates': [14.607297, 121.048476], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '12'}, 		
                        {'address': '1838 Yakal St 237, Manila', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [39600, 46800], 'capacity': 3, 'order_time': 0, 'ref': '13'}, 
                        {'address': '1838 Yakal St 237, Manila', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [39600, 46800], 'capacity': 4, 'order_time': 0, 'ref': '14'}, 
                        {'address': '1320 CP Garcia St Moriones, Bgy 123, Zone 009 Tondo, Manila', 'coordinates': [14.6205654, 120.9659653], 'delivery_window': [39600, 46800], 'capacity': 2, 'order_time': 0, 'ref': '15'},  
                        {'address': 'Fairways Towers 5th Avenue corner McKinley Road, Taguig\nUnit N 15A/15/Fairways Towers', 'coordinates': [14.545619, 121.0454128], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '16'}, 
                        {'address': '1310 C. P. Garcia Street, Tondo, Manila, Metro Manila, Philippines', 'coordinates': [14.6105919, 120.9617521], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '17'}, 
                        {'address': '1320 CP Garcia St Moriones, Bgy 123, Zone 009 Tondo, Manila', 'coordinates': [14.6205654, 120.9659653], 'delivery_window': [39600, 46800], 'capacity': 2, 'order_time': 0, 'ref': '18'}, 
                        {'address': '2176 Jesus St pandacan manila, barangay 848/6', 'coordinates': [14.5926865, 121.0044297], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '19'}, 
                        {'address': '156 Session Road Quezon City Batasan Hills', 'coordinates': [14.6797936, 121.1032391], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '20'}, 
                        {'address': '1838 Yakal St 237, Manila', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [39600, 46800], 'capacity': 5, 'order_time': 0, 'ref': '21'}], 
                    (39600, 43200): [
                        {'address': 'Fishermall, Diliman, Quezon City', 'coordinates': [14.6336204, 121.0193792], 'delivery_window': [39600, 43200], 'capacity': 0, 'order_time': 0, 'ref': '22'}, 
                        {'address': '4H Anaheim 2, California Garden Square, D.M. Guevara St., Highway Hills, Mandaluyong', 'coordinates': [14.5792302, 121.0452694], 'delivery_window': [46800, 57600], 'capacity': 2, 'order_time': 0, 'ref': '23'}, 
                        {'address': '45 Lebanon Street Don Bosco, Paranaque','coordinates': [14.4786641, 121.032481], 'delivery_window': [46800, 57600], 'capacity': 1, 'order_time': 0, 'ref': '24'}], 
                    (57600, 61200): [
                        {'address': 'Fishermall, Diliman, Quezon City', 'coordinates': [14.6336204, 121.0193792], 'delivery_window': [57600, 61200], 'capacity': 0, 'order_time': 0, 'ref': '25'}, 
                        {'address': '940, MaligayaStreet, Manila', 'coordinates': [14.5665457, 120.9952634], 'delivery_window': [64800, 72000], 'capacity': 1, 'order_time': 0, 'ref': '26'}, 
                        {'address': '1838 Yakal St 237, Manila', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [64800, 72000], 'capacity': 5, 'order_time': 0, 'ref': '27'}, 
                        {'address': '1838 Yakal St 237, Manila', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [64800, 72000], 'capacity': 5, 'order_time': 0, 'ref': '28'}]}}
   
        schedules = DriverGrouping().group_drivers_by_time_slot(drivers=[Driver(id=item.get('id'),
                                                                            time_slots=item.get('time_slots'),
                                                                            capacity=item.get('capacity'),
                                                                            speed=item.get('speed')) for item in drivers])
        data = LocationGrouping().group_locations(locations, schedules, True)

        for pickup_address, pickup_windows in data.items():
            for pickup_window, obj in pickup_windows.items():
                locs = obj.get('locations')
                driver_ids = obj.get('driver_ids')
                while locs and driver_ids:
                    driver = None 
                    for item in drivers:
                        if item.get('id') == driver_ids[0]:
                            driver = item
                            break

                    filtered_indices = []
                    for k, v in enumerate(locs):
                        if v.capacity <= driver.get('capacity'):
                            filtered_indices.append(k)
                            
                    indices = Routing(locations=[loc for loc in locs if loc.capacity <= driver.get('capacity')],
                                      num_vehicles=len(locs)).generate_routes(vehicle_capacity=driver.get('capacity'),
                                                                              speed=driver.get('speed'),
                                                                              service_time_unit=1800)
                    if len(indices) == 0:                       
                        break
                    else:
                        #remove driver from available driver list only if a route has been built
                        driver_ids.pop(0)                            

                        routes = []
                        for item in indices[0]:
                            if ';' in locs[filtered_indices[item]].ref:
                                for sub_item in locs[filtered_indices[item]].ref.split(';'):
                                    itm_info = sub_item.split(',')
                                    routes.append(Location(coordinates = Coordinates(locs[filtered_indices[item]].coordinates[0], locs[filtered_indices[item]].coordinates[1]),
                                                           address = locs[filtered_indices[item]].address,
                                                           delivery_window = locs[filtered_indices[item]].delivery_window,
                                                           capacity = itm_info[1],
                                                           ref = itm_info[0]))
                            else:
                                routes.append(locs[filtered_indices[item]])
                            if filtered_indices[item] != 0:
                                locs[filtered_indices[item]] = None

                        locs = list(filter(lambda x: x is not None, locs))

                        print([route.capacity for route in routes])
                        print([route.address for route in routes])
                        print([route.delivery_window for route in routes])

                obj['locations'] = locs if len(locs) > 1 else []

        print('Second round...')
        for pickup_address, pickup_windows in data.items():
            for pickup_window, obj in pickup_windows.items():
                locs = obj.get('locations')
                if locs:
                    indices = Routing(locations=locs,
                                      num_vehicles=len(locs)).generate_routes(
                                                                            vehicle_capacity=30,
                                                                            speed=30,
                                                                            service_time_unit=1800)

                    if len(indices) == 0:                    
                        break
                    else:                                                
                        for idx_list in indices:
                            routes = []

                            for item in idx_list:
                                if ';' in locs[item].ref:
                                    for sub_item in locs[item].ref.split(';'):
                                        itm_info = sub_item.split(',')
                                        routes.append(Location(coordinates = Coordinates(locs[item].coordinates[0], locs[item].coordinates[1]),
                                                                address = locs[item].address,
                                                                delivery_window = locs[item].delivery_window,
                                                                capacity = itm_info[1],
                                                                ref = itm_info[0]))
                                else:
                                    routes.append(locs[item])

                                if item != 0:
                                    locs[item] = None

                            print([route.capacity for route in routes])
                            print([route.address for route in routes])
                            
                        locs = list(filter(lambda x: x is not None, locs))
                        obj['locations'] = locs if len(locs) > 1 else []
        print(data)