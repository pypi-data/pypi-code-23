# -*- coding: utf-8 -*-

""" Font manipulation """

#Imported application modules
import logging
import freetype
from .generator import *
from .code import *
from .bitmap import yamglBitmap

#########################################################################################
class yamglFontMap(yamglObject):
    """
    Unicode map object
    """

#---------------------------------------------------------------------------------------#
    def __init__(self, maps):
        """
        Constructor
        """

        self.maps = maps
        self.packed_index = 0

#---------------------------------------------------------------------------------------#
    def __reduce_update_make(self, objlist, generator):
        """
        Compresses the values into a singlke list,
        Updates class indexes,
        Calls the generator to create the Declaration
        """  

        #Reduce the list
        pack_ls = self.reduce_list([b.maps for b in objlist])

        logging.info("unicode map data packed")

        #update the indexes
        for l_obj in objlist:
            l_obj.packed_index = self.find_index(pack_ls, l_obj.maps)

        #Create the packed list
        values = yamglInitList([yamglInitList([yamglConstant(a[0]), yamglConstant(a[1])]) for a in pack_ls])
        generator.add_declaration(yamglDecl(yamglType("static const yamglUnicodeMap []"), "packed_unicode_maps", values))

#---------------------------------------------------------------------------------------#
    def run_steps(self, objlist, generator):
        """
        Run a list of classes through own's generator
        This is class related but does not require the class instance
        """
        
        logging.debug("running generator on class:%s" % self.__class__.__name__)

        #Start generating stuff
        self.__reduce_update_make(objlist, generator)

#########################################################################################
class yamglGlyph(yamglObject):
    """
    Glyph object
    """

#---------------------------------------------------------------------------------------#
    def __init__(self, face, index):
        """
        Constructor
        """

        slot_index = face.get_char_index(index)
        face.load_glyph(slot_index, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
        glyph_bitmap = face.glyph.bitmap
		
		#Properties
        self.glyph_left = face.glyph.bitmap_left
        self.glyph_top = face.glyph.bitmap_top
        self.glyph_advance = face.glyph.advance.x // 64
        self.unicode_id = index
        self.glyph_name = face.get_glyph_name(slot_index).decode("utf-8") 
        self.glyph_bitmap_object = yamglBitmap(glyph_bitmap.width, glyph_bitmap.rows)

		#Decompress pixels
        for y_coord in range(glyph_bitmap.rows):
            for x_coord in range(glyph_bitmap.width):
                byte_loc = x_coord % 8
                index_loc = x_coord // 8
                #Add pixel to bitmap
                pixelValue = 0 if ((glyph_bitmap.buffer[glyph_bitmap.pitch * y_coord + index_loc] & (0x80 >> byte_loc)) != 0x00) else 1
                self.glyph_bitmap_object.add_pixel(x_coord, y_coord, pixelValue)

#---------------------------------------------------------------------------------------#
    def add_to_generator(self, generator):    
        """
        Add self and all children to the generator
        """
        
        #Add self
        generator.add_object(self)

        #Add objects
        generator.add_object(self.glyph_bitmap_object)

#---------------------------------------------------------------------------------------#
    def get_dependecies(self):
        """
        Return a list of dependencies to be run before the class in question
        """
        #No dependency by default
        return [yamglBitmap]

#---------------------------------------------------------------------------------------#
    def get_init_list(self):
        """
        Return a  generator init list
        """

        return yamglInitList([self.glyph_bitmap_object.get_init_list(), 
                                    yamglConstant(self.glyph_left),
                                    yamglConstant(self.glyph_top),
                                    yamglConstant(self.glyph_advance)])
       

#########################################################################################
class yamglFont(yamglObject):
    """
    Font object
    """

#---------------------------------------------------------------------------------------#
    def __init__(self, name, path, size, maps):
        """
        Constuctor
        name = object name
        path = file path
        size = point size
        maps = list of tuples containing character mappings [(0, 1), (2, 3), ...]
        """

        logging.debug("creating font: name = %s, path = %s, size = %d, maps = %s" % (name, path, size, maps))

        #Try to open the font file
        try:
            #Open and convert
            font_face = freetype.Face(path)
            font_face.set_pixel_sizes(0, size)
        except:
            logging.error("could not process file %s" % path)
            exit(1)

        logging.info("font '%s' processed" % name) 

        #Properties
        self.vertical_space = font_face.size.height // 64
        self.object_name = name
        self.font_size = size

        #Objects
        self.unicode_map_object = yamglFontMap(maps)
        self.glyph_objects = []

        #Go throgh all maps
        for map_set in maps:
            for char_index in range(map_set[0], map_set[1] + 1):
                self.glyph_objects.append(yamglGlyph(font_face, char_index))

        #Add unknown glyph		
        self.glyph_objects.append(yamglGlyph(font_face, 65533))

#---------------------------------------------------------------------------------------#
    def add_to_generator(self, generator):    
        """
        Add self and all children to the generator
        """
        
        #Add self
        generator.add_object(self)

        #Add objects
        generator.add_object(self.unicode_map_object)
        for glyph_object in self.glyph_objects:
            glyph_object.add_to_generator(generator)

#---------------------------------------------------------------------------------------#
    def get_dependecies(self):
        """
        Return a list of dependencies to be run before the class in question
        """
        #No dependency by default
        return [yamglGlyph, yamglBitmap, yamglFontMap]

#---------------------------------------------------------------------------------------#
    def __make(self, objlist, generator):
        """
        Add the required data
        """

        for l_obj in objlist:
            #Create glyph structure
            g_name = "glyphs_font_" + l_obj.object_name
            generator.add_declaration(yamglDecl(yamglType("static const yamglGlyph []"), 
                                    g_name, 
                                    yamglInitList([a.get_init_list() for a in l_obj.glyph_objects]), 
                                    dependency = ["packed_bitmaps"]))

            #Constructor 
            init_object = yamglConstructor("yamglFont", [yamglReference(g_name),
                                                        yamglReference("packed_unicode_maps", index = l_obj.unicode_map_object.packed_index),
                                                        yamglConstant(len(l_obj.glyph_objects)),
                                                        yamglConstant(len(l_obj.unicode_map_object.maps)),
                                                        yamglConstant(l_obj.vertical_space)])
            generator.add_declaration(yamglDecl(yamglType("yamglFont"), l_obj.object_name, init_object, dependency = ["packed_bitmaps", g_name, "packed_unicode_maps"]))                      

#---------------------------------------------------------------------------------------#
    def run_steps(self, objlist, generator):
        """
        Run a list of classes through own's generator
        This is class related but does not require the class instance
        """
        
        logging.debug("running generator on class:%s" % self.__class__.__name__)

        #Start generating stuff
        self.__make(objlist, generator)