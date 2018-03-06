from typing import List

import click
import tqdm

from pytsv.pytsv import TsvReader, TsvWriter


@click.command()
@click.option(
    '--progress',
    required=False,
    default=True,
    type=bool,
    help="show progress",
    show_default=True,
)
@click.option(
    '--input-file',
    required=True,
    type=str,
    help="input file",
    show_default=True,
)
@click.option(
    '--output-file',
    required=True,
    type=str,
    help="output file",
    show_default=True,
)
@click.option(
    '--match-columns',
    required=True,
    type=str,
    help="columns to match",
    show_default=True,
)
def main(
        progress,
        input_file,
        output_file,
        match_columns,
):
    # type: (bool, str, str, str) -> None
    """
    This script will fix a tsv file assuming that bad characters or tabs have been
left in one column of it.
    """
    match_columns = [int(x) for x in match_columns.split(',')]
    with TsvReader(filename=input_file) as input_file_handle:
        if progress:
            input_file_handle = tqdm.tqdm(input_file_handle)
        saw = set()
        with TsvWriter(filename=output_file) as output_file_handle:
            for fields in input_file_handle:  # type: List[str]
                match = frozenset([fields[match_column] for match_column in match_columns])
                if match not in saw:
                    saw.add(match)
                    output_file_handle.write(fields)


if __name__ == '__main__':
    main()
