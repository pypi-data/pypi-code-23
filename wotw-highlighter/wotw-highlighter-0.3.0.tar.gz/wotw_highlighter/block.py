"""This file provides a class to build and run everything"""

from wotw_highlighter.block_options import BlockOptions
from wotw_highlighter.block_loader import BlockLoader
from wotw_highlighter.block_highlighter import BlockHighlighter
from wotw_highlighter.block_styler import BlockStyler
from wotw_highlighter.block_decorator import BlockDecorator


class Block(BlockOptions):
    """This class loads code, highlights, and returns a polished block"""

    def __init__(self, *args, **kwargs):
        super(Block, self).__init__(*args, **kwargs)
        self.compile()

    def load(self):
        """Loads the block"""
        loaded_block = BlockLoader(**self.full_options())
        loaded_block.load()
        self.update_options(**loaded_block.full_options())

    def highlight(self):
        """Highlights the block"""
        highlighted_block = BlockHighlighter(**self.full_options())
        highlighted_block.attach_lexer()
        highlighted_block.attach_formatter()
        highlighted_block.highlight()
        self.update_options(**highlighted_block.full_options())

    def style(self):
        """Styles the block"""
        styled_block = BlockStyler(**self.full_options())
        styled_block.set_styles()
        self.update_options(**styled_block.full_options())

    def decorate(self):
        """Applies any decorations"""
        decorated_block = BlockDecorator(**self.full_options())
        decorated_block.decorate()
        self.update_options(**decorated_block.full_options())

    def compile(self):
        """
        Runs all the block actions

        EXECUTION ORDER MATTERS
        """
        self.load()
        self.highlight()
        self.style()
        self.decorate()

    @property
    def rendered(self):
        """Returns the highlighted block"""
        return self.highlighted_blob
