#-*-coding:iso-8859-1-*-
#
"""
module managing one calculation
"""

from messages import CRITICAL, WARNING, signal, get_balises
from fichiers import grep

import os
import shutil




class Calcul:
    """
    class performing calculation
    """
    def __init__(self, description="f"):
        
        self.description = description
        self.input_files = {}
        self.results_files = []       
        self.balise_to_replace = {}
        self.results = {}
        
    def set_input_file(self, name, source, balises=None):
        """
        add a template for an input file
        """
        #
        #  name    --> name of the input file as it must be saved
        #              or the code to execute properly
        #  source  --> path of the file or the file template to
        #              copy as file 'name' before to execute the code
        #  balises --> list of mandatory balises to replace in
        #              'source' before saving it to 'name'
        #
        self.input_files[name] = source
        if balises:
            self.balise_to_replace[name] = balises
            
    def set_saved_files(self, files=None):
        """
        define the files to be saved in results directory
        at the end of the calculation
        """
        if files==None:
            self.results_files = []
            return
        if type(files) == "toto":
            self.results_files = [files]
        else:
            self.results_files = files
            
    def get_saved_files(self):
        """
        returns the list of file to save in result directory
        """
        return self.results_files
    
    def set_result(self, key, val):
        """
          save value 'val' in tab of results where result of the execution can be checked
          Result(key) = val
        """
        self.results[key] = val

    def set_results(self, vals):
        """
          save all values of the dictionary  'vals' in tab of results
          where result of the execution can be checked
          Result(key) = val
        """
        self.results.update(vals)
            
    def set_result_from_file(self, motif, file_name, key, \
                          value_if_found, value_if_not_found):
        """
          check if file 'file_name' contains pattern 'motif'
          si it does,  Result(key) = value_if_found
          si not      Result(key) = valueIfNotFound
        """
        #if (grep(motif, file_name, error_type = CRITICAL)):
	if (grep(motif, file_name, error_type = WARNING)):
            self.set_result(key,  value_if_found)
        else:
            self.set_result(key,  value_if_not_found)
    
    def get_result(self, key, error_type = WARNING):
        """
        return the result stored at the 'key' position in the directory
        """
        if not(key in self.results.keys()):
            signal(error_type,
                   "%s result not available for calculation '%s'" % \
                   (key, self.description))
            return None
        return self.results[key]   
    
    def get_results(self):
        """
            returns a dictionary containing all the results made public
        """
        return self.results
    
    def get_result_keys(self):
        """
            returns the keys of a dictionary containing all the results made public 
        """
        return self.results.keys()
     
    

    def prepare(self, **other_balises):
        """
        creates input filee from template file using balises
        """
        self.results = {}
        """
           Fonction qui copie les fichiers vers le repertoire courant
           et remplace les balises
        """

        # getting balises from the environment and from additional balises
        d_balises = get_balises()
        d_balises.update(other_balises)
        
        
        for fic in self.input_files.keys():
            # checking that source file exists
            if not os.path.isfile(self.input_files[fic]):
                signal(CRITICAL,
                       "file '%s' does not exist and\
                        is required to run '%s'!" %\
                       (self.input_files[fic], self.description))
            
            # if the file already exists,  it's deleted
            if os.path.isfile(fic):
                os.remove(fic)
            
            if not(fic in self.balise_to_replace.keys()): 
                # no balise to replace : a simple copy will do 
                shutil.copyfile(self.input_files[fic], fic)
            else:
                # balise to replace while copying the file
                # into the current directory
                balises_to_replace = self.balise_to_replace[fic]
                # 1. checking that every balise needed for this file is valued
                balise_values_unknown = ""
                for bal in balises_to_replace:
                    if not(bal in d_balises.keys()):
                        balise_values_unknown = \
                              balise_values_unknown+" '%s'" % bal
                if len(balise_values_unknown):
                    out = "Balises set at this point : \n"
                    for bal1 in d_balises.keys():
                        out = out+"%s : '%s'\n" % (bal1, d_balises[bal1])
                    signal(CRITICAL, "While preparing execution of '%s' \
                    \n\tMandatory following balises are not valued : %s\
                    \n\n\t%s"%(self.description, balise_values_unknown, out))
                
                # 2. replacing and saving.....
                template  =  open(self.input_files[fic], "r")
                input_file  =  open(fic, "w")
                for ligne in template.readlines():
                    if (len(ligne) >=  1):
                        for balise in d_balises.keys():
                            ligne  =  str.replace(ligne, balise,
                                                  str(d_balises[balise]))
                    input_file.write(ligne) 
                template.close() 
                input_file.close()
                         
    

class Maestro(Calcul):
    pass
