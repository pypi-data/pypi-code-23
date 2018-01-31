# -*- coding: utf-8 -*-

""" Code generator utilities """

#Used modules
import logging

#########################################################################################
class yamglPrimitive:
    """
    Code generation primitives base class
    """

    #---------------------------------------------------------------------------------------#
    def __lt__(self, other):
        """
        Used for sorting priorities
        """

        #Just return True if the name is in the list of the other object
        logging.debug("evaluating: %s against: %s" % (self.get_name(), other.get_dependecies()))

        return True if self.get_name() in other.get_dependecies() else False

#---------------------------------------------------------------------------------------#
    def get_dependecies(self):
        """
        Return a list of dependencies to be run before the class in question
        """
        #No dependency by default
        return [None]

#---------------------------------------------------------------------------------------#
    def get_name(self):
        """
        Gets the declaration name. Should only be implemented inside the Decl class
        """
        #No name by default
        return None  

#---------------------------------------------------------------------------------------#
    def get_value(self):
        """
        Get the value for the element.
        Should be implemented in all code generation classes
        """
        return ""

#########################################################################################
class yamglDecl(yamglPrimitive):
    """
    A declaration (variable) object
    """

#---------------------------------------------------------------------------------------#
    def __init__(self, v_type, name, value, dependency = [None]):
        """
        Constructor
        """
        self.v_type = v_type
        self.name = name
        self.value = value
        self.dependencies = dependency

#---------------------------------------------------------------------------------------#
    def get_name(self):
        """
        Gets the declaration name. Should only be implemented inside the Decl class
        """
        return self.name

#---------------------------------------------------------------------------------------#
    def get_dependecies(self):
        """
        Return a list of dependencies to be run before the class in question
        """
        return self.dependencies    

#---------------------------------------------------------------------------------------#
    def get_value(self):
        """
        Get the value for the element.
        """
        l_type = self.v_type.get_value()

        if "[" in l_type:
            new_str = l_type.replace("[", ("%s[" % (self.name)))
            data = "%s = %s;" % (new_str, self.value.get_value())
        else:
            data = "%s %s = %s;" % (self.v_type.get_value(), self.name, self.value.get_value())   

        #Make Null as default
        extern = None
        if "static" not in l_type:
            extern = "extern %s %s;" % (l_type, self.name)

        return (extern, data)    

#########################################################################################
class yamglInitList(yamglPrimitive):  
    """
    A Init list primitive (arrays and structures)
    """

#---------------------------------------------------------------------------------------#
    def __init__(self, children):
        """
        Constructor
        """  
        self.children = children

#---------------------------------------------------------------------------------------#
    def get_value(self):
        """
        Get the value for the element.
        """
        return "{%s}" % (", ".join(a.get_value() for a in self.children))      

#########################################################################################
class yamglConstant(yamglPrimitive):  
    """
    A constant (a number)
    """

#---------------------------------------------------------------------------------------#
    def __init__(self, value):
        """
        Constructor
        """  
        self.value = value

#---------------------------------------------------------------------------------------#
    def get_value(self):
        """
        Get the value for the element.
        """
        return str(self.value)

#########################################################################################
class yamglReference(yamglPrimitive):  
    """
    A reference (an address &)
    """

#---------------------------------------------------------------------------------------#
    def __init__(self, reference, index = None):
        """
        Constructor
        """  
        self.reference = reference
        self.index = index

#---------------------------------------------------------------------------------------#
    def get_value(self):
        """
        Get the value for the element.
        """
        if self.index is None:
            return "&%s" % (self.reference)
        else:
            return "&%s[%d]" % (self.reference, self.index)     

#########################################################################################
class yamglConstructor(yamglPrimitive):  
    """
    A constructor E.G.:
    n = Class(a, b, c);
    """

#---------------------------------------------------------------------------------------#
    def __init__(self, classname, values):
        """
        Constructor
        """  
        self.classname = classname
        self.values = values

#---------------------------------------------------------------------------------------#
    def get_value(self):
        """
        Get the value for the element.
        """
        return "%s(%s)" % (self.classname, ", ".join(a.get_value() for a in self.values)) 

#########################################################################################
class yamglType(yamglPrimitive):  
    """
    A type of variable (like a cast string) 
    E.G.
    "static const unsigned char []"
    """

#---------------------------------------------------------------------------------------#
    def __init__(self, designator):
        """
        Constructor
        """  
        self.designator = designator

#---------------------------------------------------------------------------------------#
    def get_value(self):
        """
        Get the value for the element.
        """
        return str(self.designator)