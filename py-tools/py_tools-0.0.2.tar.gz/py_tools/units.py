import os
import pint
import pandas as pd

unit_registry = pint.UnitRegistry(system='mks', autoconvert_offset_to_baseunit=True)
