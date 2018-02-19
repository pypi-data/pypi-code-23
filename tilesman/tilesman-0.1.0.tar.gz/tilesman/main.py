import os
import argparse
from math import log, ceil
from photo import Photo, InputFileException, InvalidResizingException, TilingException


def run(photo_path, tile_max_width, tile_max_height):
	'''
	Main application method. Given a photo in 'photo_path', will create a pyramid of tiles (maximum size of
	'tile_max_width' x 'tile_max_height' pixels) split into different photo resolution levels, represented
	in a folder hierarchy.
	'''
	
	try:
		img = Photo(photo_path)

		# Find expected number of resolution levels
		resolution_levels = 1 + ceil(log(max(img.width, img.height),2))

		# Iterate over resolution levels, from higuest to lowest
		for level in range(resolution_levels - 1, -1, -1):
			# Initiate the tiling process for the current level
			img.extract_tiles(level, tile_max_width, tile_max_height)

			# Resize photo to half the current size
			img.shrink(0.5)

	except (InputFileException, TilingException, InvalidResizingException) as ke:
		print(ke)
		return False
	except Exception as ue:
		print('Terminating due to an unknown exception\n')
		print(str(ue))
		return False
	else:
		return True

def prepare_argparse():
	argument_parser = argparse.ArgumentParser(
		description = 'Writes a pyramid of configurable tile sizes for an N x M pixels photo, at different resolution levels'
	)
	required_arg_group = argument_parser.add_argument_group('required arguments')
	required_arg_group.add_argument('-p', required = True, help = 'Valid input photo path')
	required_arg_group.add_argument('-w', type = int, required = True, help = 'Maximum width for a tile')
	required_arg_group.add_argument('-e', type = int, required = True, help = 'Maximum height for a tile')
	return argument_parser

if __name__ == '__main__':
	argument_parser = prepare_argparse()
	args = argument_parser.parse_args()

	if run(args.p, args.w, args.e):
		print('Photo %s tiled successfully' % args.p)
	else:
		print('Attempt to tile photo %s was not successfull' % args.p)
