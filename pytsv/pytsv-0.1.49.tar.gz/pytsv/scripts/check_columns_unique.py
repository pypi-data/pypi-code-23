from typing import List

import click
import tqdm

from pytsv.pytsv import TsvReader


@click.command()
@click.option(
    '--progress',
    required=False,
    default=True,
    type=bool,
    help="show progress",
    show_default=True,
)
@click.argument(
    'input-files',
    nargs=-1,
    required=True,
)
@click.option(
    '--columns',
    required=True,
    type=str,
    help="columns to match",
)
def main(
        progress,
        input_files,
        columns,
):
    # type: (bool, List[str], str) -> None
    """
    This script checks that for certain columns every value in the files
    is unique.
    """
    columns = [int(x) for x in columns.split(',')]
    dicts = [dict() for _ in range(len(columns))]
    errors = False
    for input_file in input_files:
        with TsvReader(
            filename=input_file,
        ) as input_file_handle:
            if progress:
                input_file_handle = tqdm.tqdm(input_file_handle, desc=input_file)
            for line_number, fields in enumerate(input_file_handle):
                for i, column in enumerate(columns):
                    value = fields[column]
                    if value in dicts[i]:
                        line = dicts[i][value]
                        print("value [{}] is duplicate on lines [{}, {}]".format(
                            value,
                            line,
                            line_number,
                        ))
                        errors = True
                    else:
                        dicts[i][value] = line_number
    assert errors is False, "found errors"


if __name__ == '__main__':
    main()
