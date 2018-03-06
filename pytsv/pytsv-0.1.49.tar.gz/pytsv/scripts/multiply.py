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
    help="input file (can be compressed)",
    show_default=True,
)
@click.option(
    '--input-field-number',
    required=True,
    type=int,
    help="fields according to which to multiply",
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
        input_field_number,
        output_file,
):
    # type: (bool, str, int, str) -> None
    """ multiply a tsv file according to column """
    with TsvReader(filename=input_file) as input_file_handle:
        with TsvWriter(filename=output_file) as output_file_handle:
            if progress:
                input_file_handle = tqdm.tqdm(input_file_handle)
            for fields in input_file_handle:
                current_number = int(fields[input_field_number])
                for _ in range(current_number):
                    output_file_handle.write(fields)


if __name__ == '__main__':
    main()
