from enum import Enum

import click
import tqdm

from pytsv.pytsv import TsvReader, TsvWriter


class MyEventTypes(Enum):
    key_not_found = 0
    key_found = 1
    unknown_added = 2


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
    '--hash-file',
    required=True,
    type=str,
    help="hash file",
)
@click.option(
    '--hash-key-column',
    required=True,
    type=int,
    help="column to match on in the hash file",
)
@click.option(
    '--hash-value-column',
    required=True,
    type=int,
    help="value to get from the hash file",
)
@click.option(
    '--input-file',
    required=True,
    type=str,
    help="file to work on",
)
@click.option(
    '--input-key-column',
    required=True,
    type=int,
    help="column to match on in the input file",
)
@click.option(
    '--output-file',
    required=True,
    type=str,
    help="name of the output file",
)
@click.option(
    '--output-insert-column',
    required=True,
    type=int,
    help="column to insert at in the first file to create the output file",
)
@click.option(
    '--output-add-unknown',
    required=True,
    type=bool,
    help="add UNKNOWN when there is no match or drop",
)
def main(
        progress,
        hash_file,
        hash_key_column,
        hash_value_column,
        input_file,
        input_key_column,
        output_file,
        output_insert_column,
        output_add_unknown,
):
    # type: (bool, str, int, int, str, int, str, int, bool) -> None
    """ join two tsv files by column """
    d = dict()
    event_found = 0
    event_unknown_added = 0
    event_discarded = 0
    with TsvReader(hash_file) as hash_file_handle:
        if progress:
            hash_file_handle = tqdm.tqdm(hash_file_handle, desc="reading hash")
        for fields in hash_file_handle:
            key = fields[hash_key_column]
            value = fields[hash_value_column]
            d[key] = value
    with TsvReader(input_file) as input_file_handle, \
            TsvWriter(output_file) as output_file_handle:
        if progress:
            input_file_handle = tqdm.tqdm(input_file_handle, desc="reading input and writing output")
        for fields in input_file_handle:
            key = fields[input_key_column]
            if key in d:
                event_found += 1
                new_value = d[key]
                fields.insert(output_insert_column, new_value)
                output_file_handle.write(fields)
            else:
                if output_add_unknown:
                    event_unknown_added += 1
                    fields.insert(output_insert_column, "unknown")
                    output_file_handle.write(fields)
                else:
                    event_discarded += 1
    print("event_found {}".format(event_found))
    print("event_unknown_added {}".format(event_unknown_added))
    print("event_discarded {}".format(event_discarded))


if __name__ == '__main__':
    main()
