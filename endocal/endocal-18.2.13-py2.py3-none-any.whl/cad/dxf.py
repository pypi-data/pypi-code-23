from os.path import join, splitext
from pkg_resources import resource_filename
from math import atan2, cos, sin, sqrt
from numpy import linspace, pi


def __header():
    """Read header in from package data.

    :return:
    """
    header_filename = resource_filename(
        'cad', join('data/dxf', 'header.dxf'))
    with open(header_filename, 'r') as header_file:
        return header_file.read()


def __footer():
    """Read footer in from package data.

    :return:
    """
    footer_filename = resource_filename(
        'cad', join(join('data', 'dxf'), 'footer.dxf'))
    with open(footer_filename, 'r') as footer_file:
        return footer_file.read()


def __polyline():
    """Read polyline in from package data.

    :return:
    """
    polyline_filename = resource_filename(
        'cad', join(join('data', 'dxf'), 'polyline.dxf'))
    with open(polyline_filename, 'r') as polyline_file:
        return polyline_file.read()


def __seqend():
    """Read seqend in from package data.

    :return:
    """
    seqend_filename = resource_filename(
        'cad', join(join('data', 'dxf'), 'seqend.dxf'))
    with open(seqend_filename) as seqend_file:
        return seqend_file.read()


def __format_float(value):
    """Format float in scientific notation, 6 decimal places.

    :param value:
    :return:
    """
    return '{:.6e}'.format(float(value))


def grid_header():
    """Generate grid header text for DXF file.

    :return:
    """
    return __header()


def grid(laser_beam_width, diameter):
    """Generate DXF text describing asymmetrical circles grid.

    :param laser_beam_width:
    :param diameter:
    :return:
    """
    width = 3
    height = 11

    # now we shift paradigm: width becomes rows, height cols
    num_rows = 2 * width
    num_cols_even = height // 2
    num_cols_odd = num_cols_even + 1

    # first and last line coordinates
    x0 = laser_beam_width / 2.0
    y0 = 0.0
    xn = diameter / 2.0

    # number of laser application trajectories (i.e. lines)
    num_lines = int(round(diameter / (2.0 * laser_beam_width)) + 1)

    # step size for lines
    dx = (xn - x0) / (num_lines - 1)

    grid_str = ''
    for row in range(num_rows):
        if row % 2 == 0:  # even row
            num_cols = num_cols_even
            offset = diameter
        else:  # odd row
            num_cols = num_cols_odd
            offset = 0

        for col in range(num_cols):
            for line in range(num_lines):
                grid_str += 'CIRCLE' + '\n'
                for value in [8, 0, 62, 7, 10]:
                    grid_str += str(value) + '\n'
                grid_str += __format_float(
                    x0 + col * (2 * diameter) + offset) + '\n'
                grid_str += str(20) + '\n'
                grid_str += __format_float(
                    y0 + (row + 1) * (1.5 * diameter)) + '\n'
                for value in [30, 0, 40]:
                    grid_str += str(value) + '\n'
                grid_str += __format_float(x0 + dx * line) + '\n'
                grid_str += str(0) + '\n'

    return grid_str


def grid_footer():
    """Generate grid footer text for DXF file.

    :return:
    """
    return __footer()


def legend_filename(grid_filename):
    """Generate legend filename corresponding to `grid_filename`.

    :param grid_filename:
    :return:
    """
    split_buffer = splitext(grid_filename)
    return split_buffer[0] + '-legend' + split_buffer[1]


def legend_header():
    """Generate legend text for DXF file.

    :return:
    """
    return __header()


def legend(laser_beam_width, circle_diameter):
    """Generate DXF text describing legend.

    :param laser_beam_width:
    :param circle_diameter: diameter of circles in
    spanned circles grid, used for scaling legend
    :return:
    """

    # Coordinates of the two vertices of ellipse major axis
    x1 = circle_diameter * -1.26978
    x2 = circle_diameter * 15.6187
    y1 = circle_diameter * 1.68651
    y2 = circle_diameter * 13.8027
    tilt_angle = atan2(y2 - y1, x2 - x1)

    # Centre of ellipse
    xc = (x1 + x2) / 2
    yc = (y1 + y2) / 2

    # Short radius
    b = circle_diameter * 7.84016

    # Total number of passes required
    total_line_width = circle_diameter / 2
    num_lines = int(round(total_line_width / laser_beam_width) + 1)
    mutual_line_distance = total_line_width / (num_lines - 1)

    polyline = __polyline()
    legend_str = ''
    for line in range(num_lines):
        legend_str += polyline

        line_offset = line * mutual_line_distance
        line_offset_x = line_offset * cos(tilt_angle)
        line_offset_y = line_offset * sin(tilt_angle)
        new_x1 = x1 - line_offset_x
        new_x2 = x2 + line_offset_x
        new_y1 = y1 - line_offset_y
        new_y2 = y2 + line_offset_y

        new_a = 0.5 * sqrt((new_x2 - new_x1) ** 2 +
                           (new_y2 - new_y1) ** 2)
        new_b = b + line_offset

        angles = linspace(start=0, stop=2 * pi, num=100)
        for angle in angles:
            pre_tilt_x = new_a * cos(angle)
            pre_tilt_y = new_b * sin(angle)
            x = xc +\
                pre_tilt_x * cos(tilt_angle) -\
                pre_tilt_y * sin(tilt_angle)
            y = yc +\
                pre_tilt_x * sin(tilt_angle) +\
                pre_tilt_y * cos(tilt_angle)

            legend_str += 'VERTEX' + '\n'
            for value in [8, 0, 10]:
                legend_str += str(value) + '\n'
            legend_str += __format_float(x) + '\n'
            legend_str += str(20) + '\n'
            legend_str += __format_float(y) + '\n'
            legend_str += str(0) + '\n'

        legend_str += __seqend()

    return legend_str


def legend_footer():
    """Generate legend footer text for DXF file.

    :return:
    """
    return __footer()
