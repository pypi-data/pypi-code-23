class Helpers(object):
  def int_array_to_byte_array(ints):
    data = bytearray()
    for i in ints:
      data.append(i % 256)
    return data