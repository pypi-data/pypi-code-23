# -*- coding: utf-8 -*-

import unittest
import os

from exiv2 import lowlevel as exiv2

this_path = os.path.dirname(__file__)
if this_path:
    this_path += os.sep
    
def path(x):
    return this_path + x


        
class test_exiv2(unittest.TestCase):

    
    def test_1(self):
        with self.assertRaises(exiv2.Exiv2Exception):
            im = exiv2.ImageFactory_open("bad path")
    
        im = exiv2.ImageFactory_open(path("test.jpg"))
        exiv2.Image_delete(im)
        
        im = exiv2.ImageFactory_open(path("test2.jpg"))
        exiv2.Image_delete(im)
    
        with open(path("test.jpg"), "rb") as f:
            data = f.read()
            im = exiv2.ImageFactory_open(data)
            exiv2.Image_delete(im)
        
        with self.assertRaises(exiv2.Exiv2Exception):
            data = b'rubbish'
            im = exiv2.ImageFactory_open(data)
            
    def test2(self):
        with open(path("test.jpg"), "rb") as f:
            data = f.read()
        im = exiv2.ImageFactory_open(data)
        for i in range(10):
            exiv2.Image_readMetadata(im)        
            exiv2.Image_writeMetadata(im)
            exiv2.Image_clearExifData(im)
            exiv2.Image_clearIptcData(im)   
            exiv2.Image_clearXmpPacket(im)    
            exiv2.Image_clearXmpData(im)
            exiv2.Image_clearComment(im)
            exiv2.Image_clearIccProfile(im)
            exiv2.Image_clearMetadata(im)
        exiv2.Image_delete(im)

    def test3(self):
        with open(path("test.jpg"), "rb") as f:
            data = f.read()
        im = exiv2.ImageFactory_open(data)
        for i in range(10):
            exiv2.Image_exifData(im)        
            exiv2.Image_iptcData(im)        
            exiv2.Image_xmpData(im)        
        exiv2.Image_delete(im)

    def test4(self):
        for i in range(10):    
            data = exiv2.IptcData_new()
            exiv2.IptcData_delete(data)
            
        new_iptc_data = exiv2.IptcData_new()
        key = "Iptc.Application2.Caption"
        datum = exiv2.IptcData_operator_bracket(new_iptc_data, key)
        key2 = exiv2.Iptcdatum_key(datum)
        self.assertEqual(key,key2)   
        with self.assertRaisesRegex(exiv2.Exiv2Exception, "Value not set"):
            value = exiv2.Iptcdatum_value(datum)
        
        set_value = "Hi Mum!"
        result = exiv2.Iptcdatum_setValue(datum, "Hi Mum!")
        self.assertEqual(result,0)
        
        value = exiv2.Iptcdatum_value(datum)
        get_value = exiv2.Value_toString(value)
        self.assertEqual(get_value, set_value)

        get_value = exiv2.Value_toFloat(value, 3)
        self.assertEqual(get_value, float(ord(set_value[3])))
        get_value = exiv2.Value_toLong(value, 1)
        self.assertEqual(get_value, ord(set_value[1]))
                
        with open(path("test.jpg"), "rb") as f:
            imdata = f.read()
        im = exiv2.ImageFactory_open(imdata)
        exiv2.Image_readMetadata(im)               
        old_iptc_data = exiv2.Image_iptcData(im)
        key = "Iptc.Application2.Caption"
        old_datum = exiv2.IptcData_operator_bracket(old_iptc_data, key)
        value = exiv2.Iptcdatum_toString(old_datum)
        self.assertEqual(value, "*insert title here*")
                
        exiv2.Image_setIptcData(im, new_iptc_data)
        exiv2.Image_clearExifData(im)
        exiv2.Image_clearXmpData(im)
        exiv2.Image_writeMetadata(im)
        
        io = exiv2.Image_io(im)
        size = exiv2.BasicIo_size(io)
        buffer = exiv2.BasicIo_read(io, size)
        self.assertEqual(len(buffer),size)
        with open(path("out.jpg"), "wb") as f:
            f.write(buffer)
        
        exiv2.IptcData_delete(new_iptc_data)

    def test5(self):
        im = exiv2.ImageFactory_open(path("test.jpg"))
        with open(path("test.jpg"), "rb") as f:
            imdata = f.read()
        im = exiv2.ImageFactory_open(imdata)
        
        iptc_data = exiv2.Image_iptcData(im)
        exiv2.Image_readMetadata(im)               
        key = "Iptc.Application2.Caption"
        datum = exiv2.IptcData_operator_bracket(iptc_data, key)
        value = exiv2.Iptcdatum_toString(datum)
        

        # change metadata
        result = exiv2.Iptcdatum_setValue(datum, "Hi Mum!")
        assert result == 0
        exiv2.Image_clearExifData(im)
        exiv2.Image_clearXmpData(im)
        exiv2.Image_writeMetadata(im)

        # write to file
        io = exiv2.Image_io(im)
        size = exiv2.BasicIo_size(io)
        buffer = exiv2.BasicIo_read(io, size)       
        with open(path("out.jpg"), "wb") as f:
            f.write(buffer)
            
        exiv2.Image_delete(im)        
        
    
if __name__ == '__main__':
    unittest.main()