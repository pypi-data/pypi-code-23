import click
import tqdm

from pytsv.pytsv import TsvReader, TsvWriter
import numpy.random
from collections import defaultdict


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
    '--sample-column',
    required=True,
    type=int,
    help="what column to sample by",
)
@click.option(
    '--size',
    required=True,
    type=int,
    help="what sample size do you need?",
)
@click.option(
    '--replace',
    required=True,
    type=bool,
    help="allow replacement",
)
@click.option(
    '--hits-mode',
    required=True,
    type=bool,
    help="sample size is hits",
)
@click.option(
    '--progress',
    required=False,
    default=True,
    type=bool,
    help="show progress",
    show_default=True,
)
def main(
        input_file,
        output_file,
        sample_column,
        size,
        replace,
        hits_mode,
        progress,
):
    # type: (str, str, int, int, bool, bool) -> None
    """
    This application will sample from a tsv file by a sample column
    The sample column must be convertible to a floating point number.
    """
    weights = []
    elements = []
    sum_weights = float(0)
    with TsvReader(input_file) as input_handle:
        if progress:
            input_handle = tqdm.tqdm(input_handle)
        for fields in input_handle:
            elements.append(fields)
            weight = float(fields[sample_column])
            sum_weights += weight
            weights.append(weight)
    # the following code will only work on python3.6 because the
    # random.choices API was only introduced then
    # from random import choices
    # results = choices(lines, weights, k=size)

    # this is the same code with numpy
    weights = [w/sum_weights for w in weights]
    if hits_mode:
        results_dict = defaultdict(int)
        for i in range(size):
            current_result = numpy.random.choice(
                a=len(elements),
                replace=replace,
                size=1,
                p=weights,
            )
            current_result = current_result[0]
            results_dict[current_result] += 1
        with TsvWriter(output_file) as output_handle:
            for result, hits in results_dict.items():
                record = list(elements[result])
                record.append(hits)
                output_handle.write(record)
    else:
        results = numpy.random.choice(
            a=len(elements),
            replace=replace,
            size=size,
            p=weights,
        )
        with TsvWriter(output_file) as output_handle:
            for result in results:
                output_handle.write(elements[result])


if __name__ == '__main__':
    main()
