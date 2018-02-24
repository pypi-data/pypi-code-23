"""This file provides a class to decorate the base Pygments result"""

from re import sub

from premailer import Premailer

from wotw_highlighter.block_options import BlockOptions
from wotw_highlighter.block_header import BlockHeader


class BlockDecorator(BlockOptions):
    """This class decorates highlighted blobs"""

    header = None

    def validate(self):
        if not self.highlighted_blob:
            raise ValueError('Nothing to decorate')
        if self.inline_css and not self.highlighted_blob_styles:
            raise ValueError('No styles to inline')

    def remove_linenos(self):
        """Removes line numbers from a highlighted blob"""
        self.highlighted_blob = sub(
            r'<td[\s\S]*?linenos[\s\S]*?</td>',
            '',
            self.highlighted_blob
        )

    def compile_header(self):
        """Compiles a block header"""
        block_header = BlockHeader(**self.full_options())
        self.header = block_header.render_full_header()

    def insert_header(self):
        """Inserts the compiled header row in highlighted_blob"""
        self.highlighted_blob = sub(
            r'^(<table.*?>)(<tr)',
            r'\1%s\2' % (self.header),
            self.highlighted_blob
        )

    def inline_all_css(self):
        """Inlines block CSS"""
        premailer_input = (
            '<html>'
            '<head>'
            '<style>%s</style>'
            '</head>'
            '<body>%s</body>'
            '</html>'
            % (
                self.highlighted_blob_styles,
                self.highlighted_blob
            )
        )
        premailer_runner = Premailer(
            premailer_input,
            disable_validation=True
        )
        self.highlighted_blob = sub(
            r'^[\s\S]*?<body>([\s\S]*?)</body>[\s\S]*$',
            r'\1',
            premailer_runner.transform()
        )

    def apply_destructive_decorations(self):
        """Runs decorations that could possibly break others"""
        if self.inline_css:
            self.inline_all_css()

    def decorate(self):
        """Attempts to decorate the highlighted_blob"""
        if self.linenos:
            if not self.no_header and (self.blob_path or self.title):
                self.compile_header()
                self.insert_header()
        else:
            self.remove_linenos()
        self.apply_destructive_decorations()
