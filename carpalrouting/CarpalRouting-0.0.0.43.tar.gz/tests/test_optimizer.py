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
                   {'id':7,'time_slots': [[32400, 64800]], 'capacity': 15, 'speed': 30}]
           
        locations = {'Fishermall, Diliman, Quezon City': {(32400, 36000): [{'address': 'Fishermall, Diliman, Quezon City', 'coordinates': [14.6336204, 121.0193792], 'delivery_window': [32400, 36000], 'capacity': 0, 'order_time': 0}, {'address': 'Pacific Rim Cor. Commerce Ave., Filinvest City, Alabang, Muntinlupa City, 1781 Metro Manila, Philippines', 'coordinates': [14.4200106, 121.033259], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '1000005264'}, {'address': '4 Kamias Rd, Diliman, Quezon City, Metro Manila', 'coordinates': [14.6310151, 121.0467182], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '1000005265'}, {'address':'30 Humility St Multinational Village, Paranaque', 'coordinates': [14.4804117, 121.0048727], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '1000005268'}, {'address': 'Blk 6 lot 13 kalayaan village, brgy. 201, Pasay', 'coordinates': [14.507602, 121.029081], 'delivery_window': [39600, 46800], 'capacity': 2, 'order_time': 0, 'ref': '1000005274'}, {'address': 'Barangay 34, Maypajo, Caloocan, Metro Manila, Philippines', 'coordinates': [14.6367721, 120.9729332], 'delivery_window': [39600, 46800], 'capacity': 2, 'order_time': 0, 'ref': '1000005183'}, {'address': '2611 Taft Ave, Barangay 68, Pasay City', 'coordinates': [14.5783882, 120.986897], 'delivery_window': [39600, 46800], 'capacity': 2, 'order_time': 0, 'ref': '1000005184'}, {'address': '1838 Yakal St, Manila, 237', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [39600, 46800], 'capacity': 4, 'order_time': 0, 'ref': '1000005186'}, {'address': '1838 Yakal St 237, Manila', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [39600, 46800], 'capacity': 4, 'order_time': 0, 'ref': '1000005188'}, {'address': '18 Molave St., Marietta-Romeo Village, Brgy Sta Lucia, Pasig', 'coordinates': [14.5815801, 121.1017699], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '1000005189'}, {'address': '86E Cotabato St.\nBago Bantay\nAlicia, Quezon City', 'coordinates': [14.6619823, 121.0235792], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '1000005190'}, {'address': 'BLK 10 Lot 7 Cor Chesa St Model Community, Bgy 120, Zone 009 Tondo, Manila, Philippines', 'coordinates': [14.6205654, 120.9659653], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '1000005192'}, {'address': 'Le Gran Condominium Eisenhower St. Greenhills, San Juan', 'coordinates': [14.607297, 121.048476], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '1000005205'}, {'address': '1838 Yakal St 237, Manila', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [39600, 46800], 'capacity': 3, 'order_time': 0, 'ref': '1000005211'}, {'address': '1838 Yakal St 237, Manila', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [39600, 46800], 'capacity': 4, 'order_time': 0, 'ref': '1000005224'}, {'address': '1320 CP Garcia St Moriones, Bgy 123, Zone 009 Tondo, Manila', 'coordinates': [14.6096907, 120.9618301], 'delivery_window': [39600, 46800], 'capacity':2, 'order_time': 0, 'ref': '1000005225'}, {'address': 'Fairways Towers 5th Avenue corner McKinley Road, Taguig\nUnit N 15A/15/Fairways Towers', 'coordinates': [14.545619, 121.0454128], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '1000005229'}, {'address': '1310 C. P. Garcia Street, Tondo, Manila, Metro Manila, Philippines', 'coordinates': [14.6105919, 120.9617521], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '1000005233'}, {'address': '1320 CP Garcia St Moriones, Bgy 123, Zone 009 Tondo, Manila', 'coordinates': [14.6096907, 120.9618301], 'delivery_window': [39600, 46800], 'capacity': 2, 'order_time': 0, 'ref': '1000005236'}, {'address': '2176 Jesus St pandacan manila', 'coordinates': [14.5926865, 121.0044297], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '1000005243'}, {'address': '156 Session Road Quezon City Batasan Hills', 'coordinates': [14.6797936, 121.1032391], 'delivery_window': [39600, 46800], 'capacity': 1, 'order_time': 0, 'ref': '1000005250'}, {'address': '1838 Yakal St 237, Manila', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [39600, 46800], 'capacity': 5, 'order_time': 0, 'ref': '1000005254'}], (39600, 43200): [{'address': 'Fishermall, Diliman, Quezon City', 'coordinates': [14.6336204, 121.0193792],'delivery_window': [39600, 43200], 'capacity': 0, 'order_time': 0}, {'address': 'Anaheim 2, California Garden Square, D.M. Guevara St., Highway Hills, Mandaluyong', 'coordinates': [14.5786156, 121.047485], 'delivery_window': [46800, 57600], 'capacity': 2, 'order_time': 0, 'ref': '1000005266'}, {'address': 'Lebanon Street Don Bosco, Paranaque', 'coordinates': [14.4786895, 121.0327488], 'delivery_window': [46800, 57600], 'capacity': 1, 'order_time': 0, 'ref': '1000005228'}], (57600, 61200): [{'address': 'Fishermall, Diliman, Quezon City', 'coordinates': [14.6336204, 121.0193792], 'delivery_window': [57600, 61200], 'capacity': 0, 'order_time': 0}, {'address': '940, Maligaya Street, Manila', 'coordinates': [14.5665457, 120.9952634], 'delivery_window': [64800, 72000], 'capacity': 1, 'order_time': 0, 'ref': '1000005242'}, {'address': '1838 Yakal St 237, Manila', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [64800, 72000], 'capacity': 5, 'order_time': 0, 'ref': '1000005255'}, {'address': '1838 Yakal St 237, Manila', 'coordinates': [14.6156181, 120.9790745], 'delivery_window': [75600, 82800], 'capacity': 5, 'order_time': 0, 'ref': '1000005257'}], (50400, 54000): [{'address': 'Fishermall, Diliman, Quezon City', 'coordinates': [14.6336204, 121.0193792], 'delivery_window': [50400, 54000], 'capacity': 0, 'order_time': 0}, {'address': '81F Madasalin St Teachers Village East Diliman, Quezon City', 'coordinates': [14.6410582, 121.0591618], 'delivery_window': [57600, 64800], 'capacity': 2, 'order_time': 0, 'ref': '1000025061'}]}}
   
        schedules = DriverGrouping().group_drivers_by_time_slot(drivers=[Driver(id=item.get('id'),
                                                                            time_slots=item.get('time_slots'),
                                                                            capacity=item.get('capacity'),
                                                                            speed=item.get('speed')) for item in drivers])
        data, _ = LocationGrouping().group_locations(locations, schedules, True)
        self.assertEqual(len(_), 0)

        inhouse = []
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
                        driver_id = driver_ids.pop(0)                            

                        routes = []
                        for item in indices[0]:
                            if ';' in locs[filtered_indices[item]].ref:
                                for sub_item in locs[filtered_indices[item]].ref.split(';'):
                                    itm_info = sub_item.split(',')
                                    routes.append(Location(coordinates = Coordinates(locs[filtered_indices[item]].coordinates[0], locs[filtered_indices[item]].coordinates[1]),
                                                           address = locs[filtered_indices[item]].address,
                                                           delivery_window = locs[filtered_indices[item]].delivery_window,
                                                           capacity = float(itm_info[1]),
                                                           ref = itm_info[0]))
                            else:
                                routes.append(locs[filtered_indices[item]])
                            if filtered_indices[item] != 0:
                                locs[filtered_indices[item]] = None
                        inhouse.append({driver_id: routes})
                        locs = list(filter(lambda x: x is not None, locs))
                obj['locations'] = locs if len(locs) > 1 else []


        public = []
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
                                                                capacity = float(itm_info[1]),
                                                                ref = itm_info[0]))
                                else:
                                    routes.append(locs[item])

                                if item != 0:
                                    locs[item] = None
                            public.append(routes)
                        locs = list(filter(lambda x: x is not None, locs))
                        obj['locations'] = locs if len(locs) > 1 else []
        
        inhouse, public = Routing.merge_routes(inhouse_routes=inhouse, public_routes=public, drivers=drivers)
        
        self.assertEqual(len(inhouse), 6)
        self.assertEqual(len(public), 5)
