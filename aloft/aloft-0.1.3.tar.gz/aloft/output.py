import yaml


def print_action(action):
    print(f'**** {action}\n')


def print_details(details):
    for line in iter(details.splitlines()):
        print_details_line(line)
    print('')


def print_details_line(line):
    print(f'     {line.rstrip()}')


def print_table(headings, rows, row_format):
    print(row_format.format(*headings))

    for row in rows:
        print(row_format.format(*row))


def print_list_as_yaml(output_list):
    print(list_as_yaml_file_data(output_list))


def list_as_yaml_file_data(output_list):
    return '\n---\n'.join(map(dump_yaml, output_list))


def dump_yaml(object_to_dump):
    output = yaml.dump(object_to_dump, default_flow_style=False)
    return output.rstrip()


def write_to_file(filename, content):
    with open(filename, 'a') as output_file:
        output_file.write(content)
