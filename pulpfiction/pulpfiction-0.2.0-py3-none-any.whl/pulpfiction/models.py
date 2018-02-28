class Comment:

    def __init__(self, filepath: str, text: str, line_num: int) -> None:
        self.filepath = filepath
        self.text = text
        self.line_num = line_num


class File:

    def __init__(self, path: str) -> None:
        self.path = path


class FileExtension:

    SUPPORTED = [
        'go',
        'js',
        'php',
        'py',
        'rb'
    ]
