import yaml


def print_table(headings, rows, row_format):
    print(row_format.format(*headings))

    for row in rows:
        print(row_format.format(*row))


def print_list_as_yaml(output_list):
    print('\n---\n'.join(map(dump_yaml, output_list)))


def dump_yaml(object_to_dump):
    output = yaml.dump(object_to_dump)
    return output.rstrip()
