# coding: utf8

from .core.log import logger  # 触发 logging 配置

from .task import Task
from .template import TemplateBase
from .writer import CsvWriter, ExcelWriter
from .core import init_fastgets_env
from .parse import (
    parser, parse_doc, Site, ParseItem,
    parse_node_text, parse_node_html, parse_time,
    parse_float, parse_int,
)


__version__ = '0.3.4'
