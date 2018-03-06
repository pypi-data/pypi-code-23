from typing import List

import click
import tqdm
from pytsv import pytsv

from pytsv.pytsv import TsvReader, TsvWriter, CHECK_NON_ASCII, REMOVE_NON_ASCII, SUB_TRAILING, CLEAN_EDGES, LOWER_CASE


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
    '--fix-columns',
    required=True,
    type=str,
    help="columns to fix",
    show_default=True,
)
@click.option(
    '--clean-edges',
    required=False,
    default=CLEAN_EDGES,
    type=bool,
    help="remove space before and after",
    show_default=True,
)
@click.option(
    '--sub-trailing',
    required=False,
    default=SUB_TRAILING,
    type=bool,
    help="substitute consecutive white spaces with one single space",
    show_default=True,
)
@click.option(
    '--remove-non-ascii',
    required=False,
    default=REMOVE_NON_ASCII,
    type=bool,
    help="remove non ascii characters",
    show_default=True,
)
@click.option(
    '--lower-case',
    required=False,
    default=LOWER_CASE,
    type=bool,
    help="lower case the field",
    show_default=True,
)
@click.option(
    '--check-non-ascii',
    required=False,
    default=CHECK_NON_ASCII,
    type=bool,
    help="check non ascii",
    show_default=True,
)
def main(
        progress,
        input_file,
        output_file,
        fix_columns,
        clean_edges,
        sub_trailing,
        remove_non_ascii,
        lower_case,
        check_non_ascii,
):
    # type: (bool, str, str, str, bool, bool, bool, bool, bool) -> None
    """
    This script will fix a tsv file assuming that bad characters or tabs have been
left in one column of it.
    """
    fix_columns = [int(x) for x in fix_columns.split(',')]
    # We need to read the input file WITHOUT assuming that it hasn't problems
    with TsvReader(filename=input_file, check_non_ascii=check_non_ascii) as input_file_handle:
        if progress:
            input_file_handle = tqdm.tqdm(input_file_handle)
        with TsvWriter(filename=output_file) as output_file_handle:
            for fields in input_file_handle:  # type: List[str]
                for fix_column in fix_columns:
                    fields[fix_column] = pytsv.clean(
                        text=fields[fix_column],
                        clean_edges=clean_edges,
                        sub_trailing=sub_trailing,
                        remove_non_ascii=remove_non_ascii,
                        lower_case=lower_case,
                    )
                output_file_handle.write(fields)


if __name__ == '__main__':
    main()
