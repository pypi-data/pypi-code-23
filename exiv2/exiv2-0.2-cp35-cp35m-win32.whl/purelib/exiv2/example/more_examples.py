import shutil
from exiv2 import ImageFactory, Iptcdatum

def example():
    image = ImageFactory.open(r"c:\test\test.jpg")
    image.readMetadata()
    ipc_data = image.iptcData()
    for datum in ipc_data:
        print(datum.key(), datum.value().toString())
    ipc_data[b'Iptc.Application2.Subject'] = b'subject'
    image.writeMetadata()

def example():
    with open(r"c:\test\test.jpg", "rb") as f:
        imdata = f.read()
    im = exiv2.ImageFactory.open(imdata)
    im.readMetadata()               

    new_iptc_data = exiv2.IptcData()                
    im.setIptcData(new_iptc_data)
    im.clearExifData()
    im.clearXmpData()
    im.writeMetadata()
        
    io = im.io()
    size = io.size()
    buffer = io.read(size)
    with open(path("c:\test\out.jpg"), "wb") as f:
        f.write(buffer)

def example3():
    shutil.copy("../test/test.jpg", "workfile.jpg")
    image = ImageFactory.open("workfile.jpg")
    image.readMetadata()
    ipc_data = image.iptcData()
    for datum in ipc_data:
        print(datum.key(), datum.value().toString())
    ipc_data[b'Iptc.Application2.Subject'] = b'subject'
    ipc_data[b'Iptc.Application2.Urgency'] = 1     	
    ipc_data[b'Iptc.Application2.Keywords'] = b'tag4'  # this will overwrite b'tag1'
    new_datum = Iptcdatum(b'Iptc.Application2.Keywords', b'tag5')
    ipc_data.add(new_datum)
    ipc_data.sortByKey()
    print()
    for datum in ipc_data:
        print(datum.key(), datum.value().toString())

    image.writeMetadata()
    
    
if __name__ == '__main__':
    example1()
    
    
