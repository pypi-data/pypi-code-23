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
    '--columns',
    required=False,
    type=int,
    default=-1,
    help="columns to match",
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
def main(
        progress,
        columns,
        input_file,
        output_file,
):
    # type: (bool, int, str, str) -> None
    """
    Remove lines from a tsv file that do not have the right number of
    columns
    """
    with TsvReader(filename=input_file, validate_all_lines_same_number_of_fields=False) as input_file_handle:
        with TsvWriter(filename=output_file) as output_file_handle:
            if progress:
                input_file_handle = tqdm.tqdm(input_file_handle, desc=input_file)
            for fields in input_file_handle:
                if columns == -1:
                    columns = len(fields)
                    continue
                if len(fields) == columns:
                    output_file_handle.write(fields)


if __name__ == '__main__':
    main()
