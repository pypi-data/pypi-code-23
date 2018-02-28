class Comment:

    def __init__(self, filepath: str, text: str, line_num: int) -> None:
        self.filepath = filepath
        self.text = text
        self.line_num = line_num

    @staticmethod
    def extract_text(raw: str) -> str:
        if raw.startswith('#'):
            return raw.split('#', 1)[1].strip()
        if raw.startswith('//'):
            return raw.split('//', 1)[1].strip()
        if raw.startswith('*'):
            return raw.split('*', 1)[1].strip()
        if raw.startswith('/*'):
            return raw.split('/*', 1)[1].strip()
        if raw.endswith('*/'):
            return raw.split('*/', 1)[0].strip()

        return ''

    @staticmethod
    def can_ignore(text: str) -> bool:
        if text.startswith('TODO') or text.startswith('FIXME'):
            return True
        return False


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
