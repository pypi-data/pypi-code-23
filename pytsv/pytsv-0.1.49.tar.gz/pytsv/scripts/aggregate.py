import click
from typing import List

import pytsv.pytsv


@click.command()
@click.option(
    '--output-file',
    required=True,
    type=str,
    help="output file to generate",
    show_default=True,
)
@click.option(
    '--match-columns',
    required=True,
    type=str,
    help="column to match by (list of numbers separated by comma)",
    show_default=True,
)
@click.option(
    '--aggregate-columns',
    required=True,
    type=str,
    help="column to aggregate by (list of numbers separated by comma)",
    show_default=True,
)
@click.option(
    '--floating-point',
    required=False,
    type=bool,
    default=True,
    help="aggregate with floating point numbers?",
    show_default=True,
)
@click.argument(
    'input-files',
    nargs=-1,
    required=True,
)
def main(
        output_file,
        match_columns,
        aggregate_columns,
        floating_point,
        input_files,
):
    # type: (str, str, str, bool, List[str]) -> None
    """ aggregate tsv files """
    match_columns = [int(x) for x in match_columns.split(",")]
    aggregate_columns = [int(x) for x in aggregate_columns.split(",")]
    pytsv.pytsv.aggregate(
        input_file_names=input_files,
        match_columns=match_columns,
        aggregate_columns=aggregate_columns,
        output_file_name=output_file,
        floating_point=floating_point,
    )


if __name__ == '__main__':
    main()
