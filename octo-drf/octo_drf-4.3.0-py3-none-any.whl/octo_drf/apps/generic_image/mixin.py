import sys
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


class ResizeImagesMixin:
    def save(self, *args, **kwargs):
        if self.image:
            #Opening the uploaded image
            base = 2000
            im = Image.open(self.image)
            w = im.width
            h = im.height
            if w > 2000 or h > 2000:
                output = BytesIO()
                if w > h:
                    wpercent = (base/float(w))
                    hsize = int((float(h)*float(wpercent)))
                    im = im.resize( (base,hsize), Image.ANTIALIAS )
                # wpercent = (basewidth/float(im.size[0]))
                # hsize = int((float(im.size[1])*float(wpercent)))
                else:
                    hpercent = (base/float(h))
                    wsize = int(float(w)*float(hpercent))
                    im = im.resize( (wsize,base), Image.ANTIALIAS )
                #Resize/modify the image
                
                #after modifications, save it to the output
                im.save(output, format='JPEG', quality=100)
                output.seek(0)
                #change the imagefield value to be the newley modifed image value
                self.image = InMemoryUploadedFile(output,'SorlImageField', "%s" % self.image.name, 'image/jpeg', sys.getsizeof(output), None)
        super().save(*args, **kwargs)


