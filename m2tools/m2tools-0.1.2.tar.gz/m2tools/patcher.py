import re
import os


class Patcher(object):
    """
    In-place patcher for files.
    Walks recursive on files and patches them in-place
    """

    def __init__(self, path):
        self.path = os.path.abspath(path)

    def walk(self, match=None):
        """
        Walk through path
        :param match: match function against filename
        :return:
        """
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                if match and match(fp):
                    yield fp

    def patch_files(self, func, match=None):
        """
        In-place patch files by path with function
        :param filename:
        :param func:
        :return:
        """

        for filename in self.walk(match):
            with open(filename, 'r') as file:
                content = file.read()
                new_content = func(content)

            with open(filename, 'w') as file:
                file.write(new_content)


class PhpCode(object):
    def __init__(self, code):
        self.code = code

    def comment_block(self, comment):
        """
        Wrap block with comment
        :param comment:
        :return:
        """

        return "/**\n%s\n*/" % "\n".join(
            map(lambda x: "* %s" % x, [line for line in comment.strip("\n\r").split("\n")])
        )

    def sign(self, signature):
        """
        Insert comment in file header
        :param signature:
        :return:
        """

        comment = self.comment_block(signature)

        if self.code.startswith('<?'):
            # Existing comment
            return re.sub(r'<\?(php)?', "<?php\n%s\n" % comment, self.code, 1)

        return "<?php\n%s\n?>\n%s" % (comment, self.code)


class JsCode(object):
    def __init__(self, code):
        self.code = code

    def comment_block(self, comment):
        """
        Wrap block with comment
        :param comment:
        :return:
        """

        return "/**\n%s\n*/" % "\n".join(
            map(lambda x: "* %s" % x, [line for line in comment.strip("\n\r").split("\n")])
        )

    def sign(self, signature):
        """
        Insert comment in file header
        :param signature:
        :return:
        """

        comment = self.comment_block(signature)
        return "%s\n\n%s" % (comment, self.code)


class XmlCode(object):
    def __init__(self, code):
        self.code = code

    def comment_block(self, comment):
        """
        Wrap block with comment
        :param comment:
        :return:
        """

        return "<!--\n/**\n%s\n*/\n-->" % "\n".join(
            map(lambda x: "* %s" % x, [line for line in comment.strip("\n\r").split("\n")])
        )

    def sign(self, signature):
        """
        Insert comment in file header
        :param signature:
        :return:
        """

        comment = self.comment_block(signature)

        return re.sub(r'(<\?[^>]+>)', "\\1\n%s\n" % comment, self.code, 1)