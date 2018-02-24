"""
Package wotw-highlighter creates editor-esque (Sublime, VS Code) blocks via
the amazing Pygments and some opinionated markup
"""

from .__version__ import __version__
from .block_options import BlockOptions
from .block_header import BlockHeader
from .block_loader import BlockLoader
from .block_highlighter import BlockHighlighter
from .block_decorator import BlockDecorator
from .block_styler import BlockStyler
from .block import Block
