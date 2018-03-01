import ruamel.yaml as yaml
from typing import Any


def loadfile(
    file: str,
    keep_order: bool = False
) -> dict:
    """
    Load yaml file.
    """
    with open(file, 'r') as stream:
        if keep_order:
            return yaml.load(stream.read(), Loader=yaml.RoundTripLoader)
        else:
            return yaml.safe_load(stream.read())


def savefile(
    data: Any,
    file: str,
    default_style: str = '"'
) -> None:
    """
    Save data to yaml file.
    """
    with open(file, 'w') as yaml_file:
        yaml.dump(data, yaml_file, Dumper=yaml.RoundTripDumper,
                  default_style=default_style)


def pprint_yaml(data: Any) -> None:
    lines: list = yaml.round_trip_dump(
        data, indent=4,
        block_seq_indent=4,
    ).splitlines(True)
    print(''.join([line for line in lines]))
