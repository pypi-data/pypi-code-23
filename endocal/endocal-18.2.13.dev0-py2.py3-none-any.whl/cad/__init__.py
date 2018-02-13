#!/usr/bin/env python

from argparse import ArgumentParser
import cad.dxf as dxf


def generate_dxf():
    """Entry point for generating DXF files.

    """
    parser = ArgumentParser()
    parser.add_argument('--laser-beam-width', type=float,
                        help='Laser beam width in microns',
                        required=True)
    parser.add_argument('--diameter', type=float,
                        help='Circular blob diameter in mm',
                        required=True)
    parser.add_argument('--output-file', type=str,
                        help='DXF file for saving generated grid',
                        required=True)
    args = parser.parse_args()

    laser_beam_width = args.laser_beam_width / 1000.0  # now in mm
    grid_header_str = dxf.grid_header()
    grid_str = dxf.grid(laser_beam_width=laser_beam_width,
                        diameter=args.diameter)
    grid_footer_str = dxf.grid_footer()

    legend_header_str = dxf.legend_header()
    legend_str = dxf.legend(laser_beam_width=laser_beam_width,
                            circle_diameter=args.diameter)
    legend_footer_str = dxf.legend_footer()

    print('Saving grid to file ' + args.output_file)
    with open(args.output_file, 'w') as output_file:
        output_file.write(grid_header_str)
        output_file.write(grid_str)
        output_file.write(grid_footer_str)

    legend_file = dxf.legend_filename(args.output_file)
    print('Saving legend to file ' + legend_file)
    with open(legend_file, 'w') as legend_file:
        legend_file.write(legend_header_str)
        legend_file.write(legend_str)
        legend_file.write(legend_footer_str)
