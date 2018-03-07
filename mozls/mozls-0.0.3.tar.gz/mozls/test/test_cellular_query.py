import unittest

from mozls import CellTower, RadioType, query_mls, Fallback
from mozls.test import get_distance


class TestQuery(unittest.TestCase):
    def test_lte(self):
        cell_a = CellTower(radio_type=RadioType.LTE,
                           mobile_country_code=262,
                           mobile_network_code=2,
                           location_area_code=46452,
                           cell_id=16531201)
        location_a = query_mls(cell_towers=[cell_a])
        self.assertLess(get_distance((location_a.lat, location_a.lon), (49.861600114, 8.657891750)),
                        location_a.accuracy)

        cell_b = CellTower(radio_type=RadioType.LTE,
                           mobile_country_code=262,
                           mobile_network_code=2,
                           location_area_code=46452,
                           cell_id=51638803)
        location_b = query_mls(cell_towers=[cell_b])
        self.assertLess(get_distance((location_b.lat, location_b.lon), (49.841193030, 8.703660965)),
                        location_a.accuracy)

        cell_c = CellTower(radio_type=RadioType.LTE,
                           mobile_country_code=262,
                           mobile_network_code=2,
                           location_area_code=46452,
                           cell_id=51638804)
        location_c = query_mls(cell_towers=[cell_c])
        self.assertLess(get_distance((location_c.lat, location_c.lon), (49.835989574, 8.702201843)),
                        location_a.accuracy)

        cell_d = CellTower(radio_type=RadioType.LTE,
                           mobile_country_code=262,
                           mobile_network_code=2,
                           location_area_code=46452,
                           cell_id=51638805)
        location_d = query_mls(cell_towers=[cell_d])
        self.assertLess(get_distance((location_d.lat, location_d.lon), (49.837096739, 8.698425293)),
                        location_a.accuracy)

    def test_wcdma(self):
        cell_a = CellTower(radio_type=RadioType.WCDMA,
                           mobile_country_code=262,
                           mobile_network_code=2,
                           location_area_code=6325,
                           cell_id=(65536 * 2519) + 57021)
        location_a = query_mls(cell_towers=[cell_a])
        self.assertLess(get_distance((location_a.lat, location_a.lon), (49.841193030, 8.703660965)),
                        location_a.accuracy)

        cell_b = CellTower(radio_type=RadioType.WCDMA,
                           mobile_country_code=262,
                           mobile_network_code=2,
                           location_area_code=6325,
                           cell_id=(65536 * 2519) + 57022)
        location_b = query_mls(cell_towers=[cell_b])
        self.assertLess(get_distance((location_b.lat, location_b.lon), (49.835989574, 8.702201843)),
                        location_b.accuracy)

        cell_c = CellTower(radio_type=RadioType.WCDMA,
                           mobile_country_code=262,
                           mobile_network_code=2,
                           location_area_code=6325,
                           cell_id=(65536 * 2519) + 57023)
        location_c = query_mls(cell_towers=[cell_c])
        self.assertLess(get_distance((location_c.lat, location_c.lon), (49.837096739, 8.698425293)),
                        location_b.accuracy)

    def test_gsm(self):
        cell_a = CellTower(radio_type=RadioType.GSM,
                           mobile_country_code=262,
                           mobile_network_code=2,
                           location_area_code=664,
                           cell_id=5581)
        location_a = query_mls(cell_towers=[cell_a])
        self.assertLess(get_distance((location_a.lat, location_a.lon), (49.839310993, 8.702545166)),
                        location_a.accuracy)

        cell_b = CellTower(radio_type=RadioType.GSM,
                           mobile_country_code=262,
                           mobile_network_code=2,
                           location_area_code=664,
                           cell_id=5582)
        location_b = query_mls(cell_towers=[cell_b])
        self.assertLess(get_distance((location_b.lat, location_b.lon), (49.825857836, 8.695936203)),
                        location_b.accuracy)

        cell_c = CellTower(radio_type=RadioType.GSM,
                           mobile_country_code=262,
                           mobile_network_code=2,
                           location_area_code=664,
                           cell_id=5583)
        location_c = query_mls(cell_towers=[cell_c])
        self.assertLess(get_distance((location_c.lat, location_c.lon), (49.839532413, 8.680572510)),
                        location_b.accuracy)

    def test_fallback_gsm(self):
        cell_a = CellTower(radio_type=RadioType.GSM,
                           mobile_country_code=262,
                           mobile_network_code=2,
                           location_area_code=664)
        location_a = query_mls(cell_towers=[cell_a], fallbacks=(Fallback.LAC))
        self.assertLess(get_distance((location_a.lat, location_a.lon), (49.839310993, 8.702545166)),
                        location_a.accuracy)
