import io
import os
from typing import Iterable

from pygments.lexers import get_lexer_for_filename
from pygments.token import Token
import pygments.util

from .models import Comment, File, FileExtension


class Directory:

    def __init__(self, path: str) -> None:
        self.path = path

    def filepaths(self, path=None) -> Iterable[File]:
        """Yields File recursively from this directory."""
        if not path:
            path = self.path
        for dirpath, dirs, files in os.walk(path):
            for name in files:
                    filename = os.path.join(dirpath, name)
                    yield File(os.path.abspath(filename))
                    if not dirs:
                        continue
                    else:
                        for d in dirs:
                            self.filepaths(os.path.join(dirpath, d))

    def __iter__(self) -> Iterable[File]:
        return self.filepaths()


class File:

    def __init__(self, path: str) -> None:
        self.path = path
        try:
            self.lexer = get_lexer_for_filename(path)
        except pygments.util.ClassNotFound:
            self.lexer = None

    def is_supported(self) -> bool:
        filename, ext = os.path.splitext(self.path)
        return ext[1:] in FileExtension.SUPPORTED

    def comments(self, path=None) -> Iterable[Comment]:
        """Yields Comments in this file."""
        if not self.lexer:
            return

        with io.open(self.path, 'r', encoding='utf8') as f:
            try:
                for (idx, Class, value) in self.lexer.get_tokens_unprocessed(
                        f.read()
                ):
                    if Class in (
                            Token.Comment.Multiline,
                            Token.Comment.Single
                    ):
                        text = Comment.extract_text(value)
                        if not text or Comment.can_ignore(text):
                            continue

                        yield Comment(self.path, text, idx)

            except UnicodeDecodeError:
                pass

    def __iter__(self) -> Iterable[Comment]:
        return self.comments()
