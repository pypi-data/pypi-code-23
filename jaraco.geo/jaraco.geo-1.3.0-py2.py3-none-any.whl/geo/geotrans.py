import ctypes

from . import geotrans2_lib

engine_errors = [key for key in dir(geotrans2_lib) if key.startswith('ENGINE')]


def handle_status(status):
	errors = [
		error
		for error in engine_errors
		if getattr(geotrans2_lib, error) & status
	]
	if errors:
		if len(errors) == 1:
			errors = errors[0]
		raise Exception(errors)


def initialize_engine():
	handle_status(geotrans2_lib.Initialize_Engine())


def get_datum_index(datum_code):
	index = ctypes.c_long()
	handle_status(geotrans2_lib.Get_Datum_Index(datum_code, index))
	return index.value
