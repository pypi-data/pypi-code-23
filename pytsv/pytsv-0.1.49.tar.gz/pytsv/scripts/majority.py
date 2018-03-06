from collections import defaultdict

import click
import tqdm
from typing import Dict

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
    help="input file (can be compressed)",
    show_default=True,
)
@click.option(
    '--input-first-column',
    required=True,
    type=int,
    help="first column",
    show_default=True,
)
@click.option(
    '--input-second-column',
    required=True,
    type=int,
    help="second column",
    show_default=True,
)
@click.option(
    '--input-multiplication-column',
    required=True,
    type=int,
    help="multiplication column",
    show_default=True,
)
@click.option(
    '--output-file',
    required=True,
    type=str,
    help="output file (can be compressed)",
    show_default=True,
)
def main(
        progress,
        input_file,
        input_first_column,
        input_second_column,
        input_multiplication_column,
        output_file,
):
    # type: (bool, str, int, int, int, str) -> None
    """ reduce two columns to a majority. This means that if x1 appears more
    with y2 than any other values in column Y then x1, y2 will be in the output
    and no other entry with x1 will appear """
    d = defaultdict(dict)  # type: Dict[Dict[str, int]]
    with TsvReader(filename=input_file) as input_file_handle:
        if progress:
            input_file_handle = tqdm.tqdm(input_file_handle)
        for fields in input_file_handle:
            p_first = fields[input_first_column]
            p_second = fields[input_second_column]
            p_multiplication = int(fields[input_multiplication_column])
            if p_second not in d[p_first]:
                d[p_first][p_second] = 0
            d[p_first][p_second] += p_multiplication
    with TsvWriter(filename=output_file) as output_file_handle:
        for p_first, p_dict in d.items():
            p_second = max(p_dict.keys(), key=lambda x: p_dict[x])
            p_count = p_dict[p_second]
            output_file_handle.write([
                p_first,
                p_second,
                str(p_count),
            ])


if __name__ == '__main__':
    main()
