# -*- coding: utf-8 -*-

""" Bitmap manipulation """

#Imported application modules
import logging
from .generator import *
from .code import *

#########################################################################################
class yamglBitmap(yamglObject):
    """
    Bitmap object class
    """

#---------------------------------------------------------------------------------------#
    def __init__(self, width, heigth):
        """
        Constructor
        """

        #Parameters
        self.bitmap_width = width
        self.bitmap_heigth = heigth
        self.packed_index = 0

        #Create pixel map
        number_of_pixels = (self.bitmap_width * self.bitmap_heigth)
        number_of_bytes = (((number_of_pixels - 1) // 8) + 1) if number_of_pixels != 0 else 0
        self.pixel_map = [0] * number_of_bytes

#---------------------------------------------------------------------------------------#
    def add_pixel(self, locx, locy, value):
        """
        Add a pixel to the bitmap
        """

        assert locx < self.bitmap_width
        assert locy < self.bitmap_heigth

        #Compute indexes
        bit_offset = (self.bitmap_width * locy) + locx
        byte_index = bit_offset // 8
        byte_offset = 7 - (bit_offset % 8)

        #RMW pixel location
        temp = self.pixel_map[byte_index]
        if (value != 0):
            temp = temp & ~(1 << byte_offset)
        else:    
            temp = temp | (1 << byte_offset)
        self.pixel_map[byte_index] = temp

#---------------------------------------------------------------------------------------#
    def get_init_list(self):
        """
        Return a  generator init list
        """    
        return yamglInitList([yamglReference("packed_bitmaps", index = self.packed_index), 
                                    yamglConstant(self.bitmap_width), 
                                    yamglConstant(self.bitmap_heigth)])

#---------------------------------------------------------------------------------------#
    def __reduce_update_make(self, objlist, generator):
        """
        Compresses the values into a single list,
        Updates class indexes,
        Calls the generator to create the Declaration
        """  

        #Reduce the list
        pack_ls = self.reduce_list([b.pixel_map for b in objlist]) 

        logging.info("bitmap data packed")

        logging.debug(pack_ls)    

        #Update indexes inside the yamglBitmap objects
        for l_obj in objlist:
            l_obj.packed_index = self.find_index(pack_ls, l_obj.pixel_map)

        #Create and add declaration
        generator.add_declaration(yamglDecl(yamglType("static const unsigned char []"), "packed_bitmaps", yamglInitList([yamglConstant(a) for a in pack_ls])))

#---------------------------------------------------------------------------------------#
    def run_steps(self, objlist, generator):
        """
        Run a list of classes through own's generator
        This is class related but does not require the class instance
        """
        
        logging.debug("running generator on class:%s" % self.__class__.__name__)

        #Start generating stuff
        self.__reduce_update_make(objlist, generator)
