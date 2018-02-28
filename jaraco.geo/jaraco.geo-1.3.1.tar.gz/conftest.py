import platform

collect_ignore = [
	'jaraco/geo/geotrans.py',
	'jaraco/geo/geotrans2_lib.py',
]

if platform.system() != 'Windows':
	collect_ignore.extend([
		'tests',
	])
