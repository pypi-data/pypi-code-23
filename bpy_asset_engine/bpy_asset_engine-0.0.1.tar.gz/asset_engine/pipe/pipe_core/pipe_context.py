#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Jared Webber
    jmw150530

:synopsis:
    Creates the Pipeline Context.

:description:
    This module creates the pipeline context using the formula manager to import
    formulas from a formulas.xml file. The asset_manager context is set by passing these
    formulas to the PathContext class which validates the path on disk and returns
    a completed path. The PipeContext class then has it's variables created with kwargs
    based upon the project formulas and the disk path.

:applications:
    Any applications that are required to run this script, i.e. Maya.

:see_also:
    Any other code that you have written that this module is similar to.

"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Built-in
import os
import re as re
from ..path_lib import formula_manager as fm
from ...utils.io import IO, Autovivification
getPreferences = None
sep = os.path.sep
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#
#Setting up os information
# path = ''
# # os = BaseEnumOS()
# # os_type = os.os
# os_drive = os.drive

def get_pcontext(path, pipe_base_dir, var=None) -> dict:
    """
    Get current Pipe Context
    * Not Tested
    :param path:
    :param pipe_base_dir:
    :param var:
    :return:
    """
    path = os.path.normpath(path)
    pipe_context = PipeContext()
    return pipe_context.examine_path(path, pipe_base_dir, var=var)

def get_path(formula, *args, **kwargs) -> str or list:
    """
    Evaluate a formula and return a path
    :param formula:
    :param args: positional arguments, e.g. parent_formula
    :param kwargs: keyword_arguments to pass to PipeContext
    :return: path
    """
    IO.info("--- Pipe Context Init ---")
    IO.debug("Formula: %s" % formula)
    argv = None
    if args:
        argv = args
    IO.debug("Positional Arguments: %s" % argv)
    IO.debug("Keywords: %s" % kwargs)
    pc = PipeContext(**kwargs)
    if isinstance(formula, list):
        # Evaluate Multiple Paths
        _eval = pc.eval_paths
    else:
        # Evaluate Single Path
        _eval = pc.eval_path
    # Evaluate
    path = _eval(formula, *args, **kwargs)
    return path

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#


class PipeContext(object):
    """
    this stores pipeline values
    """
    def __init__(self, **kwargs):
        global getPreferences
        if getPreferences is None:
            from ...bsetup.preferences import getPreferences
        preferences = getPreferences()
        self.drive = kwargs.setdefault('drive', preferences.pipe_base_dir)
        self.project = kwargs.setdefault('project', None)
        self.asset = kwargs.setdefault('asset', None)
        self.asset_type = kwargs.setdefault('asset_type', None)
        self.context_area = kwargs.setdefault('context_area', "pipeline")
        # self.disk_type = kwargs.setdefault('disk_type', None)


    def eval_path(self, formula, *args, **kwargs):
        """
        Evaluate a formula and return a path object
        :param formula: A string representing the formula to evaluate
        :param kwargs: Variables to pass to PipeContext
        :return: path
        """
        IO.info("Pipe Context - Evaluating Path")
        # Initialize PipeContext Instance in PathContext
        pipe_context_inst = PathContext(self)
        # get_path() returns a path object when formulas is a string
        path = pipe_context_inst.get_path(formula, *args, **kwargs)
        return path


    def eval_paths(self, formulas=list(), *args, **kwargs):
        """
        Evaluate multiple formulas and return a list of filepaths
        :param formulas: A list of string's representing formulas to evaluate
        :type formulas: list
        :param kwargs: Variables to pass to PipeContext
        :return: list of (formula, path)
        :rtype: list
        """
        # Initialize Re-usable PipeContext Instance in PathContext
        pipe_context_inst = PathContext(self)
        IO.info("Pipe Context - Evaluating Paths")
        # get_path() returns an generator when formulas is a list
        path = pipe_context_inst.get_path(formulas, *args, **kwargs)
        return path # yield generator


    def examine_path(self, path, pipe_base_dir=None, var=None) -> str or dict:
        """
        Examine a path on disk and derive the current context
        :param path: Current Path to evaluate
        :param pipe_base_dir: Pipeline Base Directory
        :param var: Specific formula/path
        :return: path_item or path_dict
        """
        pcontext_inst = PathContext(self)
        # Return a Single Path
        if var is None:
            path_item = pcontext_inst.examine_path(path, pipe_base_dir=pipe_base_dir, var=var)
            return path_item
        # Return the entire Path Context
        else:
            path_dict = pcontext_inst.examine_path(path, pipe_base_dir=pipe_base_dir, var=var)
            return path_dict



class PathContext(object):
    """
    this class resolves a real path on disk
    """

    # Setting the pipe context from the passed in PipeContext Object
    def __init__(self, pipe_context):
        self.pipe_context = pipe_context
        self.path = None
        self.path_dict = None


    def get_path(self, formula, *args, **kwargs):
        """
        Return or Yield a formula path
        :param formula: formula to evaluate
        :param args: positional_arguments
        :param kwargs: keyword_arguments
        :return:
        """
        # Get User Preferences
        global getPreferences
        if getPreferences is None:
            from ...bsetup.preferences import getPreferences
        preferences = getPreferences()
        # Load Formula manager
        IO.debug("Starting Formula Manager \n")
        formula_manager = fm.FormulaManager()
        if isinstance(formula, list):
            formula_pieces = []
            formula_pieces = formula_manager.get_formula(formula)
            return self._yield_form_paths(formula_pieces, **kwargs)

        else:
            if args:
                IO.warning("Arguments Passed In")
                parent_formula = args[0]
                formula_manager.get_formula(parent_formula)
            formula_pieces = formula_manager.get_formula(formula)
            return self._get_form_path(formula_pieces, **kwargs)


    def examine_path(self, path, pipe_base_dir=None, var=None):
        """

        :param path: Current context path we want to examine
        :param pipe_base_dir: Pipeline Base Directory Path
        :param var: Variable we want to examine in this path
        :return:
        """

        drive_value = None
        project_value = None
        asset_type_value = None
        asset_value = None

        IO.info("Generating Context: %s" % path)
        # Get User Preferences
        global getPreferences
        if getPreferences is None:
            from ...bsetup.preferences import getPreferences
        preferences = getPreferences()
        if pipe_base_dir is None:
            pipe_base_dir = preferences.pipe_base_dir

        # Start Formula Manager


        formula_manager = fm.FormulaManager()
        # Get Formulas default=all
        formula_manager.get_formula()
        form_dict = formula_manager.formulas_dict
        # Iterate through Formula Dict and replace variables
        for form_key, form_val in form_dict.items():
            # form_key, form_val = formula[0], os.path.normpath(formula[1])
            # Update the path in dict with normalized path
            form_dict[form_key] = form_val
            IO.debug("Form Key: %s" % form_key)
            IO.debug("Form Value: %s" % form_val)
            # Get all Variables eg. {asset}
            variables = re.findall(r'\{(.*?)\}', form_val)
            IO.debug("Variables: %s" % variables)
            if not variables:
                continue
            # Loop through each found variable
            for var in variables:
                # If variable is found in the formula, we need to replace it
                if var in form_val:
                    # Variable = drive
                    if var == 'drive':
                        # Replace "drive" variable with pipe_base_dir
                        items = form_val.split(" ")
                        real_val = val.replace(var, pipe_base_dir)
                        clean_val = real_val.strip("{}")
                        var_val = form_val.strip()
                        var_val = (var_val.replace(val, clean_val)).strip(" ")
                        IO.debug("Value: %s" % form_val)
                        IO.debug("Extended Value: %s" % e_val)
                        IO.debug("Real Value: %s" % real_val)
                        IO.debug("Clean Value: %s" % clean_val)
                        IO.debug("Var Value: %s \n" % "".join(var_val))
                        for value in e_val:
                            path = os.path.join("", e_val)
                        IO.debug(path)


                        var_val = var_val.rsplit(sep, 1)[0]
                        # Put the formula with replaced variable back in the dict
                        form_dict[form_key] = var_val
                        self.pipe_context.drive = var_val

                    elif var == 'project':
                        # Get the Pipeline Project Dir: "projects"
                        pipe_pr_dir = self.get_path("pipe_pr_dir", drive=self.pipe_context.drive)
                        # Split original path on pipe_pr_dir, then remove
                        project_path = path.rsplit(pipe_pr_dir, 1)[1]
                        project_name = project_path.split(sep)[0]
                        project_dir = os.path.join(pipe_pr_dir, project_name)
                        var_val = form_val.replace(var, project_name)
                        # Put the formula with replaced variable back in the dict
                        form_dict[form_key] = var_val
                        self.pipe_context.project = var_val
                    elif var =='asset_type':
                        pr_as_dir = self.get_path('pr_as_dir',
                                                  drive=self.pipe_context.drive,
                                                  project=self.pipe_context.project)
                        as_type_path = path.rsplit(pr_as_dir, 1)[1]
                        as_type_name = as_type_path.split(sep)[0]
                        as_type_dir = os.path.join(pr_as_dir, as_type_name)
                        var_val = form_val.replace(var, as_type_name)
                        form_dict[form_key] = var_val
                        self.pipe_context.asset_type = var_val

                    elif var == 'asset':
                        pr_as_type_dir = self.get_path('pr_as_type_dir',
                                                       drive=self.pipe_context.drive,
                                                       project=self.pipe_context.project,
                                                       asset_type=self.pipe_context.asset_type)
                        as_base_path = path.rsplit(pr_as_type_dir, 1)[1]
                        as_base_name = as_base_path.split(sep)[0]
                        as_base_dir = os.path.join(pr_as_type_dir, as_base_name)
                        var_val = form_val.replace(var, as_base_name)
                        form_dict[form_key] = var_val
                        self.pipe_context.asset = as_base_name

        self.path_dict = form_dict

        # Return Logic
        if var is None:
            # Get all variables
            self.path_dict = form_dict
            return self.path_dict

        elif var is not None:
            # Get specific variable
            return (str(var), self.path_dict[var])



    def _get_form_path(self, formula_pieces, **kwargs):
        """Return a single formula using the passed in formula pieces"""
        IO.debug("Returning Formula Path")
        IO.debug("Keywords: %s" % kwargs)
        return self._iter_form_pieces(formula_pieces, y=False, **kwargs)


    def _yield_form_paths(self, formula_pieces, **kwargs):
        """Return a formula generator using the passed in formula pieces"""
        IO.debug("Yielding Formula Path")
        IO.debug("Keywords: %s" % kwargs)
        return self._iter_form_pieces(formula_pieces, y=True, **kwargs)


    def _iter_form_pieces(self, formula_pieces, y=False, **kwargs):
        """Iterate through each formula piece"""
        pipe_path = []
        if y is False:
            # Y (yield is false)
            return self._return_path(pipe_path, formula_pieces, y=False, **kwargs)

        elif y is True:
            # (Yield is true)
            return self._yield_path(set(pipe_path), formula_pieces, y=True, **kwargs)


    def _return_path(self, path, pieces, y=False, **kwargs) -> str :
        """
        Return a normalized path by pulling values of formula pieces out of a dict
        :param path: list or set
        :param pieces: formula pieces
        :param y: yield
        :param kwargs: keyword arguments
        :return:
        """
        # Iterate over each piece
        for piece in pieces:
            # No Bracketed Values to clean, put in path
            if not '{' in piece:
                path.append(piece)
                continue
            # Regex to find all bracketed values and clean them
            cleaned = re.findall(r'\{(.*?)\}', piece, 0)
            # Check if the cleaned value is in kwargs
            if cleaned[0] in kwargs:
                value = kwargs[cleaned[0]]
                path.append(value)
            # Check if the cleaned value is in PipeContext
            elif cleaned[0] in self.pipe_context.__dict__.keys():
                value = self.pipe_context.__dict__[cleaned[0]]
                path.append(value)

        return os.path.normpath((os.path.sep).join(path))


    def _yield_path(self, path, pieces, y=True, **kwargs):
        """
        Iterate over multiple formulas and their pieces and yield a normalized path
        :param path: list or set
        :param pieces: formulas
        :param y: yield
        :param kwargs: keyword arguments
        :return:
        """
        # Iterate over each formula
        for p in pieces:
            # Iterate over each piece
            for piece in p:
                if not '{' in piece:
                    path.add(piece)
                    continue
                cleaned = re.findall(r'\{(.*?)\}', piece, 0)
                if cleaned[0] in kwargs:
                    value = kwargs[cleaned[0]]
                    path.add(value)

                elif cleaned[0] in self.pipe_context.__dict__.keys():
                    value = self.pipe_context.__dict__[cleaned[0]]
                    path.add(value)
            # Yield Generator
            yield os.path.normpath((os.path.sep).join(path))




    @staticmethod
    def create_path(path):
        os.makedirs(path, exist_ok=True)



# def get_project_context(path, project):
#     pipe_context = PipeContext(drive=path, project=project)
#     path_context = PathContext(pipe_context)
#     path_context.examine_path(path)
#     return path_context
# context = get_pipe_context(path)
