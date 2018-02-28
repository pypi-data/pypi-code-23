import sys
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


class ResizeImagesMixin:
    def save(self, *args, **kwargs):
        if self.image:
            #Opening the uploaded image
            basewidth = 1400
            im = Image.open(self.image)
            output = BytesIO()

            wpercent = (basewidth/float(im.size[0]))
            hsize = int((float(im.size[1])*float(wpercent)))

            #Resize/modify the image
            im = im.resize( (basewidth,hsize), Image.ANTIALIAS )

            #after modifications, save it to the output
            im.save(output, format='JPEG', quality=100)
            output.seek(0)
            #change the imagefield value to be the newley modifed image value
            self.image = InMemoryUploadedFile(output,'SorlImageField', "%s" % self.image.name, 'image/jpeg', sys.getsizeof(output), None)
        super().save(*args, **kwargs)