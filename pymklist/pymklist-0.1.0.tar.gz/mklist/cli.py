# -*- coding: utf-8 -*-

"""Console script for pymklist."""
import sys
import click
import os

import re

from six.moves import input as six_input

from mklist.download_data import dowload_data
from mklist.generate_parts_lst import generate_parts_lst

ldraw = re.compile(r'ldraw', flags=re.IGNORECASE)
yes = re.compile(r'[y](?:es)?', flags=re.IGNORECASE)


@click.command(name='make-list')
@click.argument('input_directory', required=False)
@click.option('--description', default=False, is_flag=True)
@click.option('--number', default=False, is_flag=True)
def main(input_directory, description, number, ):
    """Console script for pymklist."""
    if input_directory is None:
        input_directory = os.getcwd()
        if re.match(ldraw, input_directory) and os.path.exists('parts'):
            print('operating from a LDraw folder, continuing...')
        elif not re.match(ldraw, input_directory):
            print('LDraw parts directory not found')
            print('Please specify the LDraw parts library directory location in the arguments of the make-list call')
            raise click.Abort()
        else:
            print('LDraw parts directory not found')
            answer = six_input('Do you want it downloaded to a ldraw directory in %s?' % input_directory)
            if re.match(yes, answer):
                dowload_data(input_directory)
            else:
                print('Can\'t continue without a LDraw parts directory')
                raise click.Abort()

    parts_lst_path = os.path.join(input_directory, 'parts.lst')
    parts_folder_path = os.path.join(input_directory, 'parts')
    if description:
        generate_parts_lst('description', parts_folder_path, parts_lst_path)
    else:
        generate_parts_lst('number', parts_folder_path, parts_lst_path)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
