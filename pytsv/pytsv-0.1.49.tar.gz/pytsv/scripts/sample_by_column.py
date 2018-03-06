import logging

import click

import pandas
import pylogconf.core


@click.command()
@click.option(
    '--input-file',
    required=True,
    type=str,
    help="input filename",
)
@click.option(
    '--output-file',
    required=True,
    type=str,
    help="output filename",
)
@click.option(
    '--weight-column',
    required=True,
    type=int,
    help="what column to sample by",
)
@click.option(
    '--value-column',
    required=True,
    type=int,
    help="what is the value column",
)
@click.option(
    '--size',
    required=True,
    type=int,
    help="what sample size do you need?",
)
@click.option(
    '--replace',
    required=False,
    type=bool,
    default=False,
    help="allow replacements?",
)
@click.option(
    '--check-unique',
    required=False,
    type=bool,
    default=True,
    help="check that the value_column has unique values?",
)
def main(
        input_file,
        output_file,
        weight_column,
        value_column,
        size,
        replace,
        check_unique,
):
    # type: (str, str, int, int, int, bool, bool) -> None
    """
    This application will create a weighted sample from a tsv file.
    To run this you must supply a 'value_column' (the column
    which will be sampled) and a 'weight_column' which must
    be convertible to a floating point number.
    """
    logger = logging.getLogger(__name__)
    logger.info("reading the data")
    df = pandas.read_csv(
        input_file,
        sep='\t',
        header=None,
    )
    logger.info("checking that the values are unique")
    unique_values_count = df[value_column].nunique()
    if check_unique and unique_values_count != df.shape[0]:
        logger.error("your data is not unique in the value_column")
        logger.error("unique values {} != number of rows {}".format(unique_values_count, df.shape[0]))
        return
    logger.info("sampling")
    sample = df.sample(
        n=size,
        replace=replace,
        weights=df[weight_column],
    )
    df_result = sample[value_column].value_counts()
    logger.info("writing the output")
    df_result.to_csv(
        output_file,
        sep='\t',
        index=True,
    )


if __name__ == '__main__':
    pylogconf.core.setup()
    main()
