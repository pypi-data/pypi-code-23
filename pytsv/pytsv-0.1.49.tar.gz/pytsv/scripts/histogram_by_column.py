import click
import numpy

from pytsv.pytsv import TsvReader, TsvWriter


@click.command()
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
    '--column-number',
    required=True,
    type=int,
    help="what column to histogram",
    show_default=True,
)
@click.option(
    '--bucket-number',
    required=False,
    default=10,
    type=int,
    help="what column to histogram",
    show_default=True,
)
def main(
        input_file,
        output_file,
        column_number,
        bucket_number,
):
    # type: (str, str, int, int) -> None
    """ Create a histogram from a field in a tsv file """
    a = []
    total = 0
    with TsvReader(input_file) as input_handle:
        for fields in input_handle:
            a.append(float(fields[column_number]))
            total += 1
    count_in_bucket, bucket_edges = numpy.histogram(a, bins=bucket_number)
    with TsvWriter(output_file) as output_handle:
        current_sum = 0
        for i, count in enumerate(count_in_bucket):
            current_sum += count
            edge_from = bucket_edges[i]
            edge_to = bucket_edges[i+1]
            output_handle.write([
                str(edge_from),
                str(edge_to),
                str(count),
                str(int(100.0*current_sum/total)),
            ])


if __name__ == '__main__':
    main()
