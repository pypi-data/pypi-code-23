# -*- coding: utf-8 -*-

import unittest
import os, shutil

import exiv2


this_path = os.path.dirname(__file__)
if this_path:
    this_path += os.sep
    
def path(x):
    return this_path + x

TEST_PNG = path("test.png")
TEST_JPG = path("test.jpg")
UNICODE_JPG = path("蛙飛び込む.jpg")

shutil.copy(TEST_JPG,UNICODE_JPG)
        
class test_exiv2(unittest.TestCase):
    
    def test1(self):
    
        self.assertTrue(os.path.exists(TEST_PNG))
        self.assertTrue(os.path.exists(TEST_JPG))
        self.assertTrue(os.path.exists(UNICODE_JPG))

        exiv2.ImageFactory.open
        exiv2.Iptcdatum

        with self.assertRaisesRegex(exiv2.Exiv2Exception, "bad path: Failed to open the data source"):
            im = exiv2.ImageFactory.open("bad path")
    
        im = exiv2.ImageFactory.open(TEST_JPG)
        
        im = exiv2.ImageFactory.open(TEST_PNG)        
                  
        with open(TEST_JPG, "rb") as f:
            data = f.read()
            im = exiv2.ImageFactory.open(data)
            im.readMetadata()   
            self.assertEqual(im.pixelWidth(), 1024)
            self.assertEqual(im.pixelHeight(), 1024)
            self.assertIs(im.good(), True)

        with self.assertRaisesRegex(exiv2.Exiv2Exception, "The memory contains data of an unknown image type"):            
            data = b'rubbish'*100
            im = exiv2.ImageFactory.open(data)

    def test2(self):
        with open(TEST_JPG, "rb") as f:
            data = f.read()
        im = exiv2.ImageFactory.open(data)
        for i in range(5):
            im.readMetadata()        
            im.writeMetadata()
            im.clearExifData()
            im.clearIptcData()   
            im.clearXmpPacket()    
            im.clearXmpData()
            im.clearComment()
            im.clearIccProfile()
            im.clearMetadata()
            
    def test3(self):
        for path in (TEST_JPG, TEST_PNG):
            with open(path, "rb") as f:
                data = f.read()
            im = exiv2.ImageFactory.open(data)
            for c in range(5):
                e = im.exifData()        
                i = im.iptcData()        
                x = im.xmpData()                 
                io = im.io()                 
                self.assertEqual(io.path(), b'MemIo')
                self.assertEqual(e.__class__.__name__,"ExifData")

    def test3b(self):            
        new_iptc_data = exiv2.IptcData()
        self.assertEqual(0, len(new_iptc_data))
        for d in new_iptc_data:
            print(d)        

    def test4(self):
        for i in range(10):    
            data = exiv2.IptcData()
            
        new_iptc_data = exiv2.IptcData()
        
        new_iptc_data.empty()
        new_iptc_data.count()
        new_iptc_data.size()
        new_iptc_data.detectCharset()
        
        key = b"Iptc.Application2.Caption"
        datum = new_iptc_data[key]
        datum.recordName()
        datum.recordName()
        datum.groupName()
        datum.familyName()
        datum.tagName()
        datum.tagLabel()
        self.assertEqual(datum.key(), key)
        datum.record()
        datum.tag()
        datum.typeId()
        datum.typeName()
        datum.typeSize()
        datum.count()
        datum.size()
        datum.toString()
        datum.toLong()
        datum.toFloat()
        datum.toRational()
        datum.toString(0)
        datum.toLong(0)
        datum.toFloat(0)
        datum.toRational(0)
        with self.assertRaisesRegex(exiv2.Exiv2Exception, "Value not set"):
            datum.value()
        datum.setValue(b"foo")

        key = b"Iptc.Application2.CountryName"
        value = b'ok'*200
        new_iptc_data[key] = value
        self.assertEqual(new_iptc_data[key].toString(), value)
        
        key = b"Iptc.Application2.Caption3"
        with self.assertRaisesRegex(exiv2.Exiv2Exception, "Invalid dataset name `Caption3'"):
            new_iptc_data[key] = b'ok'

        key = b"Iptc.Application2.CountryName"
        datum = new_iptc_data[key]
        self.assertEqual(2, len(new_iptc_data))
                            
        set_value = b"Belgium"
        result = datum.setValue(set_value)
        self.assertEqual(result,0)
        
        value = datum.value()
        get_value = value.toString()
        self.assertEqual(get_value, set_value)

        get_value = value.toFloat(3)
        self.assertEqual(get_value, float(set_value[3]))
        get_value = value.toLong(1)
        self.assertEqual(get_value, set_value[1])
                
        with open(TEST_JPG, "rb") as f:
            imdata = f.read()
        im = exiv2.ImageFactory.open(imdata)
        im.readMetadata()               
        old_iptc_data = im.iptcData()
        key = b"Iptc.Application2.Caption"
        old_datum = old_iptc_data[key]
        value = old_datum.toString()
        self.assertEqual(value, b"*insert title here*")
                
        im.setIptcData(new_iptc_data)
        im.clearExifData()
        im.clearXmpData()
        im.writeMetadata()
        
        io = im.io()
        size = io.size()
        buffer = io.read(size)
        self.assertEqual(len(buffer),size)
        with open(path("out.jpg"), "wb") as f:
            f.write(buffer)
        
    def test4b(self):
        shutil.copy(TEST_JPG, "workfile.jpg")
        image = exiv2.ImageFactory.open("workfile.jpg")
        image.readMetadata()
        ipc_data = image.iptcData()
        for datum in ipc_data:
            datum.key(), datum.value().toString()
        ipc_data[b'Iptc.Application2.Subject'] = b'subject'
        ipc_data[b'Iptc.Application2.Urgency'] = 1     	
        ipc_data[b'Iptc.Application2.Keywords'] = b'tag4'  # this will overwrite b'tag1'
        new_datum = exiv2.Iptcdatum(b'Iptc.Application2.Keywords', b'tag5')
        ipc_data.add(new_datum)
        ipc_data.sortByKey()
        for datum in ipc_data:
            (datum.key(), datum.value().toString())
        image.writeMetadata()
        del image

        image = exiv2.ImageFactory.open("workfile.jpg")
        image.readMetadata()
        ipc_data = image.iptcData()
        self.assertEqual(ipc_data[b'Iptc.Application2.Keywords'].value().toString(), b'tag4')


    def atest5(self):
        im = exiv2.ImageFactory.open(TEST_JPG)
        with open(TEST_JPG, "rb") as f:
            imdata = f.read()
        im = exiv2.ImageFactory.open(imdata)
        
        iptc_data = exiv2.Image_iptcData(im)
        exiv2.Image_readMetadata(im)               
        key = b"Iptc.Application2.Caption"
        datum = exiv2.IptcData_operator_bracket(iptc_data, key)
        value = exiv2.Iptcdatum_toString(datum)
        

        # change metadata
        result = exiv2.Iptcdatum_setValue(datum, b"Hi Mum!")
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
        
    def atest6(self):
        for path in (TEST_JPG, TEST_PNG):
            with open(TEST_JPG, "rb") as f:
                data = f.read()
            im = exiv2.ImageFactory.open(data)
            exiv2.Image_readMetadata(im)                           
            exifdata = exiv2.Image_exifData(im)        
            iptcdata = exiv2.Image_iptcData(im)        
            xmpdata = exiv2.Image_xmpData(im)      
            exif_iterator = exiv2.ExifData_begin(exifdata)        
            exif_end = exiv2.ExifData_end(exifdata)        
            while not exiv2.ExifDataIterator_operator_compare(exif_iterator, exif_end):
                exif_datum = exiv2.ExifDataIterator_operator_dereference(exif_iterator)
                #print(exiv2.Exifdatum_key(exif_datum))
                #print(exiv2.Exifdatum_familyName(exif_datum))
                #print(exiv2.Exifdatum_tagName(exif_datum))
                #print(exiv2.Exifdatum_tagLabel(exif_datum))
                #print()
                exiv2.ExifDataIterator_operator_increment(exif_iterator)
            exiv2.Image_delete(im)
            
if __name__ == '__main__':
    unittest.main()
    
    