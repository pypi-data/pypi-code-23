import csv
from numpy import genfromtxt


def read_csv(fnom):
    """
    takes a csv file that consists of one header row and many data rows
    and reads it into a numpy array.

    :returns: dictionary mapping header text to column data
    """
    with open(fnom, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
    data = genfromtxt('drivetrain.csv', delimiter=',', skip_header=1)
    assert len(headers) == data.shape[1]
    results = {}
    for i, header in enumerate(headers):
        results[header] = data[:, i]

    return results
