# -*- coding: utf-8 -*-

import re
import os
import collections

from coupling import fs
from .misc import ClosingContextManager

import logging
logger = logging.getLogger(__name__)


class TextEditor(ClosingContextManager):
    def __init__(self, source=None):
        self.__source = source
        self.__lines = []
        if source:
            self.load(source)

    def load(self, source):
        if not hasattr(source, "readlines"):
            logger.info("load from path: %s", source)
            with open(source, "r") as f:
                self.__lines = f.readlines()
        else:
            self.__lines = source.readlines()
        self.__source = source
        return self

    def save(self, filename=None):
        if filename is not None:
            logger.info("save to path: %s", filename)
            if not os.path.exists(filename):
                fs.touch(filename)
            with open(filename, 'w') as f:
                f.writelines(self.__lines)
        else:
            if not hasattr(self.__source, "writelines"):
                with open(self.__source, 'w') as f:
                    f.writelines(self.__lines)
            else:
                self.__source.writelines(self.__lines)

    open = load
    close = save

    def as_string(self):
        return "".join(self.__lines)

    def as_lines(self):
        return self.__lines

    def insert(self, text, linenum=None):
        logger.info("insert: linenum=%s, text=%s", linenum, text)
        text = str(text)+"\n"
        if linenum:
            self.__lines.insert(text, linenum-1)
        else:
            self.__lines.append(text)
       
    def delete(self, pattern):
        logger.info("delete: pattern=%s", pattern)
        self.__lines = filter(lambda line: not re.search(pattern, line), self.__lines)
    
    def search(self, pattern, ignore_lines_with_comment_prefix='#'):
        logger.info("search: pattern=%s", pattern)
        return filter(
            lambda line: not re.match(r'[ \t]*%s' % ignore_lines_with_comment_prefix, line) and re.search(pattern, line),
            self.__lines
        )
    
    def replace(self, pattern, replace):
        logger.info("replace: pattern=%s, replace=%s", pattern, replace)
        self.__lines = map(lambda line: re.sub(pattern, replace, line), self.__lines)

    def get_all(self, delimiter='=', comment_prefix='#'):
        params = collections.OrderedDict()
        pattern = r'(.*)%s(.*)' % delimiter
        lines = self.search(pattern)
        for line in lines:
            if re.match("[ \t]*%s" % comment_prefix, line):
                continue
            else:
                match = re.search(pattern, line)
                k = match.group(1).strip()
                v = match.group(2).strip()
                params[k] = v
        return params

    def get(self, name, delimiter='=', comment_prefix='#'):
        return self.get_all(delimiter, comment_prefix).get(name, None)

    def set(self, name, value, delimiter='='):
        logger.info("set: name=%s, value=%s", name, value)
        pattern = r"^[ \t]*%s[ \t]*%s.*" % (name, delimiter)

        replace = "%s%s%s" % (name, delimiter, value)
        if self.search(pattern):
            self.replace(pattern, replace)
        else:
            self.insert(replace)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
