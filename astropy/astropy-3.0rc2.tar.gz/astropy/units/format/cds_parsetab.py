# Licensed under a 3-clause BSD style license - see LICENSE.rst


# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = '6FC211F72F2851FC3FF7D2BFF951FE7A'
    
_lr_action_items = {'UINT':([0,2,3,14,15,16,19,23,],[1,-21,20,-20,28,29,30,32,]),'PRODUCT':([2,12,13,18,30,31,],[-18,-10,27,-17,-19,-11,]),'CLOSE_PAREN':([2,7,8,12,13,18,22,25,30,31,33,34,],[-18,-4,-5,-10,-7,-17,31,-8,-19,-11,-9,-6,]),'UNIT':([0,1,5,6,10,11,17,20,21,26,27,28,35,36,],[2,-15,2,-16,2,2,-14,-23,-24,2,2,-22,-13,-12,]),'OPEN_PAREN':([0,1,5,6,10,11,17,20,21,26,27,28,35,36,],[5,-15,5,-16,5,5,-14,-23,-24,5,5,-22,-13,-12,]),'$end':([1,2,4,6,7,8,9,10,12,13,17,18,20,21,24,25,28,30,31,33,34,35,36,],[-15,-18,-2,-16,-4,-5,0,-3,-10,-7,-14,-17,-23,-24,-1,-8,-22,-19,-11,-9,-6,-13,-12,]),'DIVISION':([0,1,2,5,6,10,12,13,17,18,20,21,26,27,28,30,31,35,36,],[11,-15,-18,11,-16,11,-10,26,-14,-17,-23,-24,11,11,-22,-19,-11,-13,-12,]),'UFLOAT':([0,3,14,],[-21,21,-20,]),'X':([1,6,20,21,],[16,23,-23,-24,]),'SIGN':([0,1,2,29,32,],[14,15,14,15,15,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'division_of_units':([0,5,10,26,27,],[8,8,8,8,8,]),'main':([0,],[9,]),'combined_units':([0,5,10,26,27,],[4,22,24,33,34,]),'factor':([0,],[10,]),'signed_float':([0,],[6,]),'unit_with_power':([0,5,10,11,26,27,],[12,12,12,12,12,12,]),'product_of_units':([0,5,10,26,27,],[7,7,7,7,7,]),'signed_int':([1,29,32,],[17,35,36,]),'numeric_power':([2,],[18,]),'unit_expression':([0,5,10,11,26,27,],[13,13,13,25,13,13,]),'sign':([0,2,],[3,19,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> main","S'",1,None,None,None),
  ('main -> factor combined_units','main',2,'p_main','cds.py',150),
  ('main -> combined_units','main',1,'p_main','cds.py',151),
  ('main -> factor','main',1,'p_main','cds.py',152),
  ('combined_units -> product_of_units','combined_units',1,'p_combined_units','cds.py',162),
  ('combined_units -> division_of_units','combined_units',1,'p_combined_units','cds.py',163),
  ('product_of_units -> unit_expression PRODUCT combined_units','product_of_units',3,'p_product_of_units','cds.py',169),
  ('product_of_units -> unit_expression','product_of_units',1,'p_product_of_units','cds.py',170),
  ('division_of_units -> DIVISION unit_expression','division_of_units',2,'p_division_of_units','cds.py',179),
  ('division_of_units -> unit_expression DIVISION combined_units','division_of_units',3,'p_division_of_units','cds.py',180),
  ('unit_expression -> unit_with_power','unit_expression',1,'p_unit_expression','cds.py',189),
  ('unit_expression -> OPEN_PAREN combined_units CLOSE_PAREN','unit_expression',3,'p_unit_expression','cds.py',190),
  ('factor -> signed_float X UINT signed_int','factor',4,'p_factor','cds.py',199),
  ('factor -> UINT X UINT signed_int','factor',4,'p_factor','cds.py',200),
  ('factor -> UINT signed_int','factor',2,'p_factor','cds.py',201),
  ('factor -> UINT','factor',1,'p_factor','cds.py',202),
  ('factor -> signed_float','factor',1,'p_factor','cds.py',203),
  ('unit_with_power -> UNIT numeric_power','unit_with_power',2,'p_unit_with_power','cds.py',220),
  ('unit_with_power -> UNIT','unit_with_power',1,'p_unit_with_power','cds.py',221),
  ('numeric_power -> sign UINT','numeric_power',2,'p_numeric_power','cds.py',230),
  ('sign -> SIGN','sign',1,'p_sign','cds.py',236),
  ('sign -> <empty>','sign',0,'p_sign','cds.py',237),
  ('signed_int -> SIGN UINT','signed_int',2,'p_signed_int','cds.py',246),
  ('signed_float -> sign UINT','signed_float',2,'p_signed_float','cds.py',252),
  ('signed_float -> sign UFLOAT','signed_float',2,'p_signed_float','cds.py',253),
]
