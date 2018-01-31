# -*- coding: utf-8 -*-

""" Image manipulation """

#Imported application modules
import logging
from PIL import Image
from .generator import *
from .bitmap import *
from .code import *

#########################################################################################
class yamglImage(yamglObject):
    """
    Image object
    """

#---------------------------------------------------------------------------------------#
    def __init__(self, name, path):
        """
        Constuctor
        name = object name
        path = file path
        """

        logging.debug("creating image: name = %s, path = %s" % (name, path))

        #Try to open the image file
        try:
            #Convert to RGB first to remove transparency
            image_handle = Image.open(path).convert('1')
            bitmap_handle = image_handle.load()
        except:
            logging.error("could not process file %s" % path)
            exit(1)

        logging.info("image '%s' processed" % name)    

        #Properties
        self.image_name = name  

        #Create the bitmap object
        local_width, local_heigth = image_handle.size
        self.bitmap_object = yamglBitmap(local_width, local_heigth)

        #Write pixels
        for w in range(local_width):
            for h in range(local_heigth):
                self.bitmap_object.add_pixel(h, w, (1 if bitmap_handle[h, w] != 0 else 0))

#---------------------------------------------------------------------------------------#
    def add_to_generator(self, generator):
        """
        Add self and all children to the generator
        """

        #Add self
        generator.add_object(self)

        #Add objects
        generator.add_object(self.bitmap_object)

#---------------------------------------------------------------------------------------#
    def get_dependecies(self):
        """
        Return a list of dependencies to be run before the class in question
        """
        #No dependency by default
        return [yamglBitmap]

#---------------------------------------------------------------------------------------#
    def __create_primitives(self, objlist, generator):
        """
        Create the afferent data for the image list
        """

        #Create for each object
        for l_obj in objlist:
            #Bitmaps
            v_type = yamglType("static const yamglBitmap")
            bmap_name = "bitmap" + l_obj.image_name                        
            generator.add_declaration(yamglDecl(v_type, bmap_name, l_obj.bitmap_object.get_init_list(), dependency = ["packed_bitmaps"]))

            #Image constructor
            init_object = yamglConstructor("yamglImage", [yamglReference(bmap_name)])
            generator.add_declaration(yamglDecl(yamglType("yamglImage"), l_obj.image_name, init_object, dependency = ["packed_bitmaps", bmap_name]))

#---------------------------------------------------------------------------------------#
    def run_steps(self, objlist, generator):
        """
        Run a list of classes through own's generator
        This is class related but does not require the class instance
        """
        
        logging.debug("running generator on class:%s" % self.__class__.__name__)

        self.__create_primitives(objlist, generator)   