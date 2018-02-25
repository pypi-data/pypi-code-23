# -*- coding: utf-8 -*-
   
import shutil
   
from exiv2 import lowlevel as exiv2


###########################################################################################
#
#  open a jpg file read a Iptc key
#
def example1():
    im = exiv2.ImageFactory_open("../test/test.jpg")
    exiv2.Image_readMetadata(im)               
    iptc_data = exiv2.Image_iptcData(im)
    key = "Iptc.Application2.Caption"
    datum = exiv2.IptcData_operator_bracket(iptc_data, key)
    value = exiv2.Iptcdatum_toString(datum)
    print(key, value)
    exiv2.Image_delete(im)


###########################################################################################
#
#  open a jpg file, read a Iptc key, change it and write the file
#
def example2():
    shutil.copy("../test/test.jpg", "out.jpg")
    im = exiv2.ImageFactory_open("out.jpg")
    exiv2.Image_readMetadata(im)               
    iptc_data = exiv2.Image_iptcData(im)
    key = "Iptc.Application2.Caption"
    datum = exiv2.IptcData_operator_bracket(iptc_data, key)
    value = exiv2.Iptcdatum_toString(datum)
    assert value == "*insert title here*"

    # change metadata
    result = exiv2.Iptcdatum_setValue(datum, "Hi Mum!")
    assert result == 0

    # make a new key
    key = "Iptc.Application2.Copyright"
    datum = exiv2.IptcData_operator_bracket(iptc_data, key)
    result = exiv2.Iptcdatum_setValue(datum, "(c) 2018")
    assert result == 0
    
    # clear exif and xmp data so we're sure we'll see the ipct data in
    # the file properties in windows explorer
    exiv2.Image_clearExifData(im)
    exiv2.Image_clearXmpData(im)
    
    # write
    exiv2.Image_writeMetadata(im)

    exiv2.Image_delete(im)

    
###########################################################################################
#
#  work straight from a buffer
#
def example3():
    with open("out.jpg", "rb") as f:
        imdata = f.read()
    im = exiv2.ImageFactory_open(imdata)
    exiv2.Image_readMetadata(im)               
    iptc_data = exiv2.Image_iptcData(im)
    
    key = "Iptc.Application2.Copyright"
    datum = exiv2.IptcData_operator_bracket(iptc_data, key)
    result = exiv2.Iptcdatum_setValue(datum, "(c) 2019")
    assert result == 0
    
    exiv2.Image_writeMetadata(im)
    
    # write to file
    io = exiv2.Image_io(im)    
    size = exiv2.BasicIo_size(io)
    buffer = exiv2.BasicIo_read(io, size)
    with open("out2.jpg", "wb") as f:
        f.write(buffer)
        
    exiv2.Image_delete(im)


example1()
example2()
example3()






