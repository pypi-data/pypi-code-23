def get_line_count(file):
    """
    get the line count of a file
    :param file: file path
    :return: line count of input file
    """
    with open(file=file, mode="rb") as f:
        for i, l in enumerate(f):
            pass
        return i+1
