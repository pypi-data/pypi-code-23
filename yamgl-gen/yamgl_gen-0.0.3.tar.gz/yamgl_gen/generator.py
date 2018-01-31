# -*- coding: utf-8 -*-

""" Code generator utilities """

#Used modules
import logging
from .code import *

#########################################################################################
class yamglObject:
    """
    Generic inherited class for all objects containing data
    """

#---------------------------------------------------------------------------------------#
    def add_to_generator(self, generator):
        """
        Adds itself to a given generator
        """
        
        #Add self
        generator.add_object(self)

#---------------------------------------------------------------------------------------#
    def get_dependecies(self):
        """
        Return a list of dependencies to be run before the class in question
        """
        #No dependency by default
        return [None]

#---------------------------------------------------------------------------------------#
    def __lt__(self, other):
        """
        Used for sorting priorities
        """

        logging.debug("evaluating: %s against: %s" % (self.__class__, other.get_dependecies()))

        #Just return True if object class is in the dependency list of the other object
        return True if self.__class__ in other.get_dependecies() else False

#---------------------------------------------------------------------------------------#
    def run_steps(self, objlist, generator):
        """
        Run a list of classes through own's generator
        This is class related but does not require the class instance
        """
        
        logging.debug("running DEFAULT generator on class:%s" % self.__class__.__name__)

#---------------------------------------------------------------------------------------#
    def find_common(self, la, lb):
        """
        Finds a list containing both ordered elements of la and lb
        """
        #lengths
        alen = len(la)
        blen = len(lb)    

        #Find rounds count
        tot = (alen + blen - 1)
        sec = (blen - 1)
        pri = tot - (2 * sec) 

        #Run the primary loop
        for x in range(pri):
            if lb == la[x : x + blen]:
                return (blen, la)
            
        #Secondary rounds
        for y in range(sec, 0, -1):
            #print(y)
            #Right comparison
            if lb[ : y] == la[-y : ]:
                return (y, la + lb[y : ])

            #Left comparison
            if lb[-y : ] == la[ : y]:
                return (y, lb + la[y : ])

        #Not a match
        return (0, la + lb)

#---------------------------------------------------------------------------------------#
    def find_index(self, master, piece):
        """
        Return a master index of the list location in the big list
        """
        for x in range(len(master) - len(piece) + 1):
            if piece == master[x : x + len(piece)]:
                return x

        logging.debug(piece)
        logging.warning("wrong index computed, result may be erroneous")

        #Only when a error was encountered. Continue though
        return 0    

#---------------------------------------------------------------------------------------#
    def reduce_list(self, given_list):
        """
        Reduces a list of lists to a single list containing all the possible values
        """
        #Sort by size
        ls = sorted(given_list, key=lambda given_list: len(given_list), reverse = True)

        #Actual number of elements pre-reduction
        real_len = sum([len(a) for a in ls])
        
        #Iterate over all
        while len(ls) > 1:
            #Bigget number of common elements found
            lcomm = 0
            #Last list index with the greatest differences
            lind = len(ls) - 1
            #Last common
            lcom = ls[0]

            #Iterate over the whole list minus the first element(accumulator)
            for n in range(lind, 0, -1):
                #Find common
                (comm, als) = self.find_common(ls[0], ls[n])

                #See if greater
                if comm >= lcomm:
                    #Update greateset and indexs
                    lcomm = comm
                    lind = n
                    lcom = als

            #Remove the element with most in common
            del(ls[lind])
            #Update the accumulator
            ls[0] = lcom

        #Just print how many percents did the packing reduce
        logging.info("packing reduction: %d%%" % (100.0 - ((len(ls[0]) * 100.0) // real_len)))    

        #Just return the accumulator
        return(ls[0])

#########################################################################################
class yamglGenerator:
    """
    Source generator class
    """

#---------------------------------------------------------------------------------------#
    def __init__(self, src, inc):
        """
        Constructor
        """

        self.data_objects = {}
        self.src = src
        self.inc = inc
        self.declarations = []

#---------------------------------------------------------------------------------------#
    def add_object(self, object):
        """
        Add a data object to the generator
        """

        #Get class name
        obj_name = object.__class__.__name__
        
        #Instantiate the list if empty
        if obj_name not in self.data_objects:    
            self.data_objects[obj_name] = []

        self.data_objects[obj_name].append(object)

        logging.debug("object added to generator %s" %  object)

#---------------------------------------------------------------------------------------#
    def add_declaration(self, declaration):
        """
        Add a declaration to the code generator
        """

        logging.debug("added declaration:%s" % declaration)

        if declaration.__class__ == yamglDecl:     
            self.declarations.append(declaration)
        else:
            logging.warning("tried adding a non declaration to the generator, discarding")    

#---------------------------------------------------------------------------------------#
    def run(self):
        """
        Run the final step of the code generation
        """
        
        #Sort objects
        obj_run_order = sorted([self.data_objects[a] for a in self.data_objects], key = lambda x: x[0])

        logging.debug("objects run order: %s" % obj_run_order)

        logging.info("starting data generators, might take a while")

        #Run lists
        for objentry in obj_run_order:
            objentry[0].run_steps(objentry, self)

        #Sort declarations
        decl_run_order = sorted([a for a in self.declarations], key = lambda x: x)

        logging.debug("declarations run order: %s" % decl_run_order)

        #Add include
        self.src.write("#include \"yamgl_types.h\"\n")
        self.src.write("#include \"yamgl_data.h\"\n\n")
        
        #Add guards
        self.inc.write("#ifndef _YAMGL_DATA_H_\n")
        self.inc.write("#define _YAMGL_DATA_H_\n\n")

        #Add data
        for decl in decl_run_order:
            (inc, src) = decl.get_value()
            
            if src is not None:
                self.src.write(src + "\n")

            if inc is not None:
                self.inc.write(inc + "\n")

        self.inc.write("\n#endif\n")

        #Final
        logging.info("code generated")




