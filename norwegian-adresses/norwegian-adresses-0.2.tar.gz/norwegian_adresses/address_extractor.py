# pylama:ignore=C0301,E501
"""
Extract data from kartverket's .csv-files
(http://data.kartverket.no/download/content/geodataprodukter?korttype=3637&aktualitet=All&datastruktur=All&dataskema=All)
and shrink it to only what is needed."""

import csv
import json
import os
import threading
from queue import Queue
from time import gmtime, strftime, time

from utm import to_latlon

if __name__ == '__main__':
    from helpers import Timer
else:
    from .helpers import Timer


def get_number_of_lines_in_file(file_name):
    """Return the number of lines in file."""
    with open(file_name) as f:
        for i, l in enumerate(f):  # noqa
            pass
        return max(i + 1, 1)


def csv_reader(file_name, timer, **kwargs):
    """Read a csv-file, and convert it to python-dictionary."""
    data_list = []
    data_set = set()

    with open(file_name) as csv_file:
        data = csv.reader(csv_file, **kwargs)
        for csv_row in data:
            postnumber = None
            try:
                postnumber = int(csv_row[27])
            except ValueError:
                if csv_row[27] != "POSTNUMMER":
                    print(csv_row[27])
                    raise ValueError('')
            this_data = {
                'vei': csv_row[4].lower(),
                'vei_formatted': csv_row[4],
                'tettsted': csv_row[24].lower(),
                'tettsted_formatted': csv_row[24],
                'postnummer': postnumber,
                'postnummeromrade': csv_row[28].lower(),
            }
            if postnumber:
                if str(this_data) not in data_set:
                    data_set.add(str(this_data))
                    zone = csv_row[16]
                    if zone == "23":
                        geo_north = csv_row[17]
                        geo_east = csv_row[18]
                        loc = to_latlon(float(geo_east), float(
                            geo_north), 33, northern=True, strict=False)
                        this_data['loc'] = loc
                        data_list.append(this_data)
                    else:
                        raise ValueError(
                            "Got a different geo-zone than excpected. See docomentation. got zone: '{}'".format(zone))
            timer.update(data.line_num)
    return data_list


def read_csv_from_list_of_files(list_of_files, timer):
    """Read a list of csv-files."""
    adresser = []
    for idx, county in enumerate(list_of_files):
        timer.keys['filename'] = county
        timer.keys['filename'] = county
        timer.keys['this_part'] = idx
        timer.keys['this_total'] = get_number_of_lines_in_file(county)
        a = csv_reader(
            county, timer, delimiter=';')
        adresser.extend(a)
        timer.starting_progress += timer.keys['this_total']
        if idx == len(list_of_files) - 1:
            print("{:0.1f} seconds elapsed total".format(
                (time() - timer.start_time)))
    return adresser


if __name__ == '__main__':
    directory = 'data'
    counties = []
    total_number_of_lines = 0
    data_file_size = 0
    for file_name in os.listdir(directory):
        if file_name.endswith(".csv"):
            path = os.path.join(directory, file_name)
            counties.append(path)
            total_number_of_lines += get_number_of_lines_in_file(path)
            data_file_size = os.path.getsize(path)

    timer = Timer(keys={
        'parts': len(counties),
        'total': total_number_of_lines
    })
    timer.output_string = \
        '\n{}/{} {} "{}"' +\
        '\nRead and shrinked {:0.1f}% of this county after {}' +\
        '\n{:0.1f}% total, calculating this prosess should finish in {}, with an average of {:0.0f} lines/second'
    timer.output_format = lambda timer: (
        timer.keys['this_part'] + 1,
        timer.keys['parts'],
        strftime("%H:%M:%S", gmtime(timer.total_time_spent)),
        timer.keys['filename'],
        timer.progress / timer.keys['this_total'] * 100,
        strftime("%H:%M:%S", gmtime(timer.now - timer.start_time)),
        timer.lines_cycled_real / timer.keys['total'] * 100,
        strftime("%H:%M:%S", gmtime(
            (timer.keys['total'] - timer.lines_cycled_real) / (
                (timer.lines_cycled_real - timer.last_lines_cycled_real) / (timer.now - timer.last_time))
        )),
        (timer.lines_cycled_real - timer.last_lines_cycled_real) /
        (timer.now - timer.last_time),)
    # counties = [
    #     'data/P13_10_VEST-AGDER_Adresse.csv',
    #     # counties[12],
    #     # counties[18],
    #     # counties[18],
    # ]
    # print(counties)

    print('''Converting and shrinking data from Kartverket, total {} counties.
           '''.format(len(counties)))

    def read_and_shrink(queue_, timer):
        """Description."""
        output_file = 'data/adresser.json'
        # open(output_file, 'w').close()
        adresser = []
        adresser.append(read_csv_from_list_of_files(
            counties, timer))
        with open(output_file, 'w') as fout:
            json.dump(adresser[0], fout)
        print('Data saved in "{}"'.format(output_file))
        os.system('say "your program has finished"')
        json_size = os.path.getsize(output_file)
        print('Original data was {} bytes.\nNew json is {} bytes. \nShrinked to {:0.0f}%.'
              .format(
                  data_file_size,
                  json_size,
                  json_size / total_number_of_lines
              ))
        queue.put('')

    queue = Queue()
    thread = threading.Thread(
        target=read_and_shrink,
        name='Thread1',
        args=[queue, timer]
    )
    thread.daemon = True
    thread.start()
    queue.get()
