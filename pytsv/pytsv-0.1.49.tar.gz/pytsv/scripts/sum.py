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
@click.option(
    '--sum-fields',
    required=True,
    type=str,
    help="fields to cut",
    show_default=True,
)
@click.option(
    '--input-file',
    required=True,
    type=str,
    help="input file (can be compressed)",
    show_default=True,
)
def main(
        progress,
        sum_fields,
        input_file,
):
    # type: (bool, str, str) -> None
    """ sum some columns """
    sum_fields = [int(x) for x in sum_fields.split(',') if x != ""]
    sums = [0] * len(sum_fields)
    with TsvReader(filename=input_file) as input_file_handle:
        if progress:
            input_file_handle = tqdm.tqdm(input_file_handle)
        for fields in input_file_handle:  # type: List[str]
            for n, i in enumerate(sum_fields):
                sums[n] += float(fields[i])
    print(sums)


if __name__ == '__main__':
    main()
