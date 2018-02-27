def photo_tiling(photo_path, tile_max_width, tile_max_height, ignore_input_file_exception = True):
	'''
	Given a photo in 'photo_path', will create a pyramid of tiles (maximum size of
	'tile_max_width' x 'tile_max_height' pixels) split into different photo resolution levels,
	represented in a folder hierarchy. If 'ignore_input_file_exception' is true, exceptions when
	trying to load files that are not images will be ignored.
	'''
	
	import os
	import sys
	sys.path.append(os.path.dirname(__file__))
	from math import log, ceil
	from photo import Photo

	try:
		img = Photo(photo_path)

		# Find expected number of resolution levels
		resolution_levels = 1 + ceil(log(max(img.width, img.height),2))

		# Iterate over resolution levels, from higuest to lowest
		for level in range(resolution_levels - 1, -1, -1):
			# Initiate the tiling process for the current level
			img.extract_tiles(level, tile_max_width, tile_max_height)

			# Resize photo to half the current size, if photo is larger than 1 x 1 pixels
			if img.width > 1 or img.height > 1:
				img.shrink(0.5)

	# The provided path does not reference a supported image type
	except OSError as e:
		if not ignore_input_file_exception:
			raise

def batch_photo_tiling(dir_path, tile_max_width, tile_max_height):
	'''
	Given a directory in 'dir_path', will orchestrate the tiling process for each photo in the
	provided directory, considering supplied tile maximum dimensions in pixels. This method uses
	parallel processing for performance improvement
	'''

	import os
	from multiprocessing import Pool 

	photo_paths = [os.path.join(dir_path, photo_name) for photo_name in next(os.walk(dir_path))[2]]
	params = [(photo_path, tile_max_width, tile_max_height) for photo_path in photo_paths]

	# Create a pool os processes (as many as the number of cores in the processing machine) and run 
	# tiling method in a multiprocessed fashion
	with Pool() as pool:
		pool.starmap(photo_tiling, params)

def prepare_argparse():
	import argparse

	argument_parser = argparse.ArgumentParser(
		description = 'Writes a pyramid of configurable tile sizes for one or more N x M pixels photos, at different resolution levels'
	)
	required_arg_group = argument_parser.add_argument_group('required arguments')
	required_arg_group.add_argument('-p', required = True, help = 'Path to a photo or a directory containing photos')
	required_arg_group.add_argument('-w', type = int, required = True, help = 'Maximum width for a tile')
	required_arg_group.add_argument('-e', type = int, required = True, help = 'Maximum height for a tile')
	return argument_parser

def main(args = None):
	'''
	Entry method for command line calls. Will trigger multiprocessed tiling if provided path
	is a directory. Single-processed tiling will be used otherwise (-p argument is a single file)
	'''

	import os

	argument_parser = prepare_argparse()
	args = argument_parser.parse_args()

	if os.path.isdir(args.p):
		batch_photo_tiling(args.p, args.w, args.e)
	else:
		photo_tiling(args.p, args.w, args.e)

if __name__ == '__main__':
	main()
