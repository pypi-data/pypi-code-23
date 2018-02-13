#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Jared Webber
    jmw150530

:synopsis:
    Interprets formulas in formula files to generate disk paths

:description:
    This module looks at asset and project formulas, reads them, strips, cleans and
    expands them to for the purpose of creating path's on disk to pipeline assets

:applications:
    Any applications that are required to run this script, i.e. Maya.

:see_also:
    Any other code that you have written that this module is similar to.

"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Built-in
import re
import os
import sys
from ...utils.io import IO
# Third party

# Internal

# External

#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

class FormulaManager(object):
    """
    This class manages all of the project and asset formulas for the pipeline
    Finds, Reads, Cleans, Expands and returns project formulas for read XML Files.
    """
    def __init__(self):
        self.all_formulas = []
        self.formulas_dict = {}
        self.formulas = []
        #TODO: Search for forumlas in Asset Engine Library instead of locally
        self.file_location = os.path.normpath(os.path.realpath(__file__) + '/../pipeline_formulas.txt')
        self.project_file = os.path.normpath(os.path.realpath(__file__) + '/../project_formulas.txt')
        self.asset_file = os.path.normpath(os.path.realpath(__file__) + '/../asset_formulas.txt')
        self.formula_disk = None

# Get Formulas
    def get_formula(self, formula=None):
        if formula is not None:
            if isinstance(formula, list):
                # One or Multiple forumlas
                form_vals = []
                IO.debug("Parse Multiple Formulas")
                for form in formula:
                    form_val = self._get_formula(formula=form)
                    # print(form_val)
                    form_vals.append(form_val)
                # Return Multiple Forumlas
                return form_vals

            elif isinstance(formula, str):
                # Return One Forumla
                IO.debug("Parse One Formula")
                return self._get_formula(formula=formula)
        elif formula is None:
            # Return All Forumlas
            IO.debug('Parse All Formula')
            return self._get_all_formulas()
        # Return None if Formula isn't in the dictionary:
        return None

    def _get_formula(self, formula=None):
        # Read Pipeline Forumlas
        self.read_formulas()
        # Conditional Read Project Formulas
        if 'pr_' in formula:
            self.read_projects()
        # Conditional Read Asset Formulas
        if 'as_' in formula:
            self.read_assets()
        # Parse Forumlas
        self.split_formulas()
        self.clean_formulas()
        self.expand_formulas()
        # IO.info("Formula Dict")
        # IO.debug(self.formulas_dict)
        # Return Formula Values
        if formula is not None:
            if formula in self.formulas_dict:
                formula_vals = self.formulas_dict[formula]
                return formula_vals.split()


    def _get_all_formulas(self):
        # Read All Forumlas
        self.read_formulas()
        self.read_projects()
        self.read_assets()
        # Parse Forumlas
        self.split_formulas()
        self.clean_formulas()
        self.expand_formulas()
        # Return Forumla Values
        formula_vals = self.formulas_dict
        return formula_vals

        
    # Reads the formulas and strip out excess lines and characters
    def read_formulas(self):
        keep = []
        with open(self.file_location, 'r') as fh:
            for line in fh:
                line = line.strip()
                if ',' in line:
                    keep.append(line)
                    if '#' in line:
                        keep.remove(line)
        self.all_formulas = keep


    # called if 'pr_' is in formula name
    def read_projects(self):
        with open(self.project_file, 'r') as fh:
            for line in fh:
                line = line.strip()
                if 'pr_' in line:
                    self.all_formulas.append(line)
                    if '#' in line:
                        self.all_formulas.remove(line)
        return self.all_formulas


    # called if 'as_' is in formula name
    def read_assets(self):
        with open(self.asset_file, 'r') as fh:
            for line in fh:
                line = line.strip()
                if 'as_' in line:
                    self.all_formulas.append(line)
                    if '#' in line:
                        self.all_formulas.remove(line)
        return self.all_formulas

    # Split on equals signs and append the correct pieces
    def split_formulas(self):
        all_formulas = self.all_formulas
        for formula_line in all_formulas:
            formula_pieces = formula_line.split(' = ')
            self.formulas_dict[formula_pieces[0]] = formula_pieces[1]
            self.formulas.append(formula_pieces[0])

        return self.formulas


    # Clean up the formulas from any unused characters
    def clean_formulas(self):
        for formula in self.formulas:
            clean_formula = self.formulas_dict[formula]
            clean_formula = clean_formula.replace(',', '')
            clean_formula = clean_formula.replace('\'', '')
            clean_formula = clean_formula.replace('(', '')
            clean_formula = clean_formula.replace(')', '')
            clean_formula = clean_formula.strip()
            self.formulas_dict[formula] = clean_formula
        return self.formulas_dict


    # Expand all the formulas using regex
    def expand_formulas(self):
        import re
        for formula in self.formulas:
            # Let's see if 'pr_' is in the value.
            if not 'pipe_' in self.formulas_dict[formula]:
                if not 'pr_' in self.formulas_dict[formula]:
                    if not 'as_' in self.formulas_dict[formula]:
                        continue

            # Let's get the formula that we want to inherit values from.
            bracketed_values = re.findall(r'\{(.*?)\}', self.formulas_dict[formula])
            formula_to_switch = bracketed_values[0]
            if not formula_to_switch:
                continue
            # Get the formula with that value.
            #TODO: What if we don't have the value
            '''
            Let's keep our context open, and use what have
            We are missing one specific path, that we can use our current context to 
            generate. 
            '''
            legit_values = self.formulas_dict[formula_to_switch]
            replacement_str = "{%s}" % formula_to_switch
            if formula_to_switch in self.formulas_dict.keys():
                # Replace the 'pr_' value with the legit_values.
                current_value = self.formulas_dict[formula]
                current_value = current_value.replace(replacement_str, legit_values)
                self.formulas_dict[formula] = current_value


    def get_formula_disk(self, formula):
        # checks the 'disk_type' key in the formula dict and then returns the value
        if formula in self.formulas_dict:
            formula_disk = self.formulas_dict['disk_type']
            self.formula_disk = formula_disk
            return self.formula_disk


