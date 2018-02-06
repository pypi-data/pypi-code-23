import hashlib
import struct

def calculate_virtual_slot(key, total_slot=1024):
    """
    用md5哈希key，再与total_slot取模
    :param key:
    :param total_slot:
    :return:
    """
    m = hashlib.md5()
    m.update(key.encode())
    a, b = struct.unpack('Q Q', m.digest())
    return (a ^ b) % total_slot


if __name__ == "__main__":
    value1_at_slice1 = "hhub:RoomCount:0341"
    value2_at_slice1 = "hhub:RoomPrice:0341"
    value3_at_slice1 = "hhub:SalesConditon1:0372"
    value4_at_slice1 = "hhub:SalesConditon2:0375"

    value1_at_slice2 = "hhub:RoomCount:0360"
    value2_at_slice2 = "hhub:RoomPrice:0360"
    value3_at_slice2 = "hhub:SalesConditon1:0380"
    value4_at_slice2 = "hhub:SalesConditon2:0341"

    value1_at_slice3 = "hhub:RoomCount:0372"
    value2_at_slice3 = "hhub:RoomPrice:0372"
    value3_at_slice3 = "hhub:SalesConditon1:0341"
    value4_at_slice3 = "hhub:SalesConditon2:0372"

    print(calculate_virtual_slot(value1_at_slice1))
    print(calculate_virtual_slot(value2_at_slice1))
    print(calculate_virtual_slot(value3_at_slice1))
    print(calculate_virtual_slot(value4_at_slice1))

    print(calculate_virtual_slot(value1_at_slice2))
    print(calculate_virtual_slot(value2_at_slice2))
    print(calculate_virtual_slot(value3_at_slice2))
    print(calculate_virtual_slot(value4_at_slice2))

    print(calculate_virtual_slot(value1_at_slice3))
    print(calculate_virtual_slot(value2_at_slice3))
    print(calculate_virtual_slot(value3_at_slice3))
    print(calculate_virtual_slot(value4_at_slice3))
