"""
files.py
Manipulate files
"""


def does_file_exist(file_location, make = True):
    """
    Check if file exists

    :param file_location: Path to file (str)
    :param make: Make file if it does not exist (bool)
    """
    try:
        open(file_location, "r")
    # File does not exist
    except FileNotFoundError:
        # Write file
        if make:
            open(file_location, "w")

