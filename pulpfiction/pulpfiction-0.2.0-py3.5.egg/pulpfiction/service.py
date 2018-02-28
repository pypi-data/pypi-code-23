from .exceptions import LanguageUnsupported
from .parser import Directory as DirectoryParser
from .validator import Comment as Validator


def evaluate(path: str) -> None:
    parser = DirectoryParser(path)

    for _file in parser:
        if not _file.is_supported():
            continue

        for comment in _file:
            try:
                validate = Validator(comment)
                assert bool(validate)
            except AssertionError:
                raise LanguageUnsupported.from_validator(validate)
