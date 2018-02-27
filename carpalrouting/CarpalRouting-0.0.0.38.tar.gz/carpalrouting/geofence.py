import copy
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from .models import Coordinates, GeoArea, Location

class GeoTools(object):
    @staticmethod
    def is_point_in_area(edge_coordinates, coordinates):
        polygon = []
        for item in edge_coordinates:
            polygon.append((item[0], item[1]))

        return Polygon(polygon).contains(Point(coordinates[0], coordinates[1]))

    def group_locations_by_time_slot(self, locations, time_slot, threshhold=0):
        """
        Return locations that not included in the given time slot
        """
        result = [[], []]
        for loc in locations:
            if threshhold == 0:
                if time_slot[0] < loc.delivery_window[0] and loc.delivery_window[1] < time_slot[1]:
                    result[0].append(loc)
                else:
                    result[1].append(loc)
            else:
                #TODO: make use of threshhold argument
                if (time_slot[0] < loc.delivery_window[0] < time_slot[1] and loc.delivery_window[0] == (time_slot[0]+time_slot[1])/2) or \
                    (time_slot[0] < loc.delivery_window[1] < time_slot[1] and loc.delivery_window[0] == (time_slot[0]+time_slot[1])/2):
                    result[0].append(loc)
                else:
                    result[1].append(loc)
        return result

    @staticmethod
    def group_locations(edge_coordinates, delivery_locations, pickup_location, schedules=[]):
        """
        This method will group locations by multiple areas with groups of edge locations

        Sample processed:
        {'pickup1': {(43140, 79200): [<carpalrouting.models.Location object at 0x110b62be0>], 
                     (0, 43140): [<carpalrouting.models.Location object at 0x1127d66d8>, <carpalrouting.models.Location object at 0x112a15748>]}, 
         'pickup2': {(28800, 79200): [<carpalrouting.models.Location object at 0x110778320>, <carpalrouting.models.Location object at 0x112f0ecf8>, <carpalrouting.models.Location object at 0x112f0ee48>]}, 
         'pickup3': {(28800, 79200): [<carpalrouting.models.Location object at 0x112a15dd8>]}}

        Sample unprocessed: 
        {'pickup1': [], 'pickup2': [], 'pickup3': [<carpalrouting.models.Location object at 0x110778390>]}

        """
        locations = []        
        area = GeoArea()
        area.edge_locations = [v for k, v in edge_coordinates.items()]

        for item in delivery_locations:
            if GeoTools.is_point_in_area(area.edge_locations, item.get('coordinates')):  
                locations.append(item)

        all_processed = {}
        all_unprocessed = {}
        copied_schedules = copy.deepcopy(schedules)
        
        getTool = GeoTools()
        for pickup, dropoff_list in {pickup_location.get('address'): locations}.items():
            #clone delivery locations of each pick up location
            dropoffs = dropoff_list[:]
            processed_locs = {}   

            #loop all available driver scheduels
            for time_slot, driver_list in copied_schedules.items():
                processed_locs[time_slot] = []  

                # The loop will continue the check 
                # if there are still unprocessed delivery locations and available drivers
                while(dropoffs and driver_list):
                    grp = getTool.group_locations_by_time_slot(
                        locations=[Location(coordinates=Coordinates(item.get('coordinates')[0], item.get('coordinates')[1]),
                                    address=item.get('address'),
                                    delivery_window=item.get('delivery_window'),
                                    capacity=item.get('capacity'),
                                    order_time=item.get('order_time')) for item in dropoffs],
                        time_slot=time_slot)

                    #if locations partially processed, pop a driver from the pool
                    driver_list.pop(0)
                    processed_locs[time_slot].extend(grp[0])

                    dropoffs = [{'coordinates':[item.coordinates[0], item.coordinates[1]],
                                 'address': item.address,
                                 'delivery_window': item.delivery_window,
                                 'capacity': item.capacity,
                                 'order_time': item.order_time} for item in grp[1]]

            all_unprocessed.update({pickup: [Location(coordinates=Coordinates(item.get('coordinates')[0], item.get('coordinates')[1]),
                                                      address=item.get('address'),
                                                      delivery_window=item.get('delivery_window'),
                                                      capacity=item.get('capacity'),
                                                      order_time=item.get('order_time')) for item in dropoffs]})
            all_processed.update({pickup: processed_locs})
        return (all_processed, all_unprocessed)