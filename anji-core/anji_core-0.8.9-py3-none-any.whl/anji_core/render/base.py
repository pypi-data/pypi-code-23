import abc
from collections import OrderedDict
import logging

import humanize

from ..types import MessageType

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


_log = logging.getLogger(__name__)


class UnsupportedFeatureException(Exception):

    pass


class RenderEngineObject(metaclass=abc.ABCMeta):

    def __init__(self, render_engine):
        self.render_engine = render_engine

    @abc.abstractmethod
    def render_markdown(self):
        pass

    @abc.abstractmethod
    def render_plain(self):
        pass


class RenderEngineEnvironment(RenderEngineObject):  # pylint: disable=abstract-method

    def __init__(self, render_engine, title=None):
        super().__init__(render_engine)
        self.auto_inject_to_engine = True
        self.title = title

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.auto_inject_to_engine:
            self.render_engine.custom_objects.append(self)

    def start_makrdown(self):
        if not self.title:
            return ''
        return '*{}*\n\n'.format(self.render_engine.md_escape(self.title))

    def start_plain(self):
        if not self.title:
            return ''
        return '{}\n{}\n'.format(self.title, "".join(['-' for el in self.title]))


class EnumeratedList(RenderEngineEnvironment):

    def __init__(self, render_engine, title=None):
        super().__init__(render_engine, title=title)
        self.list = {}
        self.index = 1

    def _next_index(self):
        while True:
            next_index = self.index
            self.index += 1
            if self.list.get(next_index, None) is None:
                break
        return next_index

    def add(self, text, custom_index=None):
        if custom_index:
            if self.list.get(custom_index, None) is None:
                self.list[custom_index] = text
            else:
                old_element = self.list[custom_index]
                self.list[custom_index] = text
                self.list[self._next_index()] = old_element
        else:
            self.list[self._next_index()] = text

    def render_markdown(self):
        indexes = sorted(self.list.keys())
        result = self.start_makrdown()
        for index in indexes:
            result += '{}.{}\n'.format(index, self.render_engine.md_escape(self.list[index]))
        return result

    def render_plain(self):
        indexes = sorted(self.list.keys())
        result = self.start_plain()
        for index in indexes:
            result += '{}.{}\n'.format(index, self.list[index])
        return result


class BulletedList(RenderEngineEnvironment):

    def __init__(self, render_engine, title=None):
        super().__init__(render_engine, title=title)
        self.list = []

    def add(self, text):
        self.list.append(text)

    def render_markdown(self):
        result = self.start_makrdown()
        for el in self.list:
            result += '* {}\n'.format(self.render_engine.md_escape(el))
        return result

    def render_plain(self):
        result = self.start_plain()
        for el in self.list:
            result += '* {}\n'.format(el)
        return result


class FieldList(RenderEngineEnvironment):

    def __init__(self, render_engine, title=None, fields=None, without_tabs=False):
        super().__init__(render_engine)
        self.title = title
        if fields is None:
            fields = OrderedDict()
        self.fields = fields
        self.prefix = '' if without_tabs else "\t"

    def add(self, key, value):
        self.fields[key] = value

    def render_markdown(self):
        result = result = self.start_makrdown()
        for key, value in self.fields.items():
            result += f"\n{self.prefix}*{self.render_engine.md_escape(key)}*: {self.render_engine.md_escape(value)}"
        return result

    def render_plain(self):
        result = result = self.start_plain()
        for key, value in self.fields.items():
            result += f"\n{self.prefix}{key}: {value}"
        return result


class DetailedList(RenderEngineEnvironment):

    def __init__(self, render_engine, title=None):
        super().__init__(render_engine, title=title)
        self.elements = []

    def add(self, name, fields):
        field_list = FieldList(self.render_engine, title=name, fields=fields)
        field_list.auto_inject_to_engine = False
        self.elements.append(field_list)

    def element(self, name):
        el = FieldList(self.render_engine, title=name)
        el.auto_inject_to_engine = False
        self.elements.append(el)
        return el

    def start_plain(self):
        """
        Override default start_plain because underline with ---- is look very bad in this case
        """
        if not self.title:
            return ''
        return '{}\n'.format(self.title)

    def render_markdown(self):
        result = self.start_makrdown()
        # Pylint guess, that some of elements can be string
        # I guess, this is impossible
        result += "\n".join([el.render_markdown() for el in self.elements])  # pylint: disable=no-member
        return result

    def render_plain(self):
        result = self.start_plain()
        result += "\n".join([el.render_plain() for el in self.elements])
        return result


class Text(RenderEngineObject):

    def __init__(self, render_engine, text, md_escape):
        super().__init__(render_engine)
        self.text = text
        self.md_escape = md_escape

    def render_markdown(self):
        if self.md_escape:
            return self.render_engine.md_escape(self.text)
        return self.text

    def render_plain(self):
        return self.text


class Report(RenderEngineObject):

    def __init__(self, render_engine, report_name, report_link):
        super().__init__(render_engine)
        self.report_name = report_name
        self.report_link = report_link

    def render_markdown(self):
        return '**{}**: {}'.format(
            self.render_engine.md_escape(self.report_name),
            self.render_engine.md_escape(self.report_link)
        )

    def render_plain(self):
        return '{}: {}'.format(
            self.report_name,
            self.report_link
        )


class Traceback(RenderEngineObject):

    def __init__(self, render_engine, traceback):
        super().__init__(render_engine)
        self.traceback = traceback

    def render_markdown(self):
        return '```\n{}\n```'.format(self.traceback)

    def render_plain(self):
        return self.traceback


def none_function() -> None:
    return None


class AbstractRenderEngine(metaclass=abc.ABCMeta):  # pylint: disable=too-many-public-methods

    defaut_escape_logic = False

    def __init__(self, bot):
        self.bot = bot
        self._message_title = ''
        self.custom_objects = None
        self._message_type = MessageType.none
        self._in_reply_to = None

    def __enter__(self):
        self._message_title = None
        self._in_reply_to = None
        self.custom_objects = []
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()

    @abc.abstractmethod
    def is_support(self, render_feature):
        pass

    @abc.abstractmethod
    def flush(self):
        pass

    @abc.abstractmethod
    def reply(self, message, target_message, escape_markdown=True):
        pass

    @abc.abstractmethod
    def send(self, message, escape_markdown=True, channel=None):
        pass

    @abc.abstractmethod
    def md_escape(self, txt):
        pass

    @abc.abstractmethod
    def add_reaction(self, message, reaction):
        pass

    @abc.abstractmethod
    def remove_reaction(self, message, reaction):
        pass

    @abc.abstractmethod
    def raw_reaction(self, reaction):
        pass

    def reply_to(self, message):
        self._in_reply_to = message

    def convert_datetime(self, value) -> str:
        return f"{humanize.naturaldate(value)} at {value.strftime('%H:%M:%S')}"

    def enumerated_list(self, title=None):
        return EnumeratedList(self, title=title)

    def bulleted_list(self, title=None):
        return BulletedList(self, title=title)

    def detailed_list(self, title=None):
        return DetailedList(self, title=title)

    def field_list(self, title=None):
        return FieldList(self, title=title, without_tabs=True)

    def text(self, text, md_escape=None):
        if md_escape is None:
            md_escape = self.defaut_escape_logic
        self.custom_objects.append(Text(self, text, md_escape))

    def traceback(self, traceback):
        self.custom_objects.append(Traceback(self, traceback))

    def report(self, report_name, report_link):
        self.custom_objects.append(Report(self, report_name, report_link))

    def title(self, title):
        self._message_title = title

    def message_type(self, type_):
        self._message_type = type_

    def auto_task_result(self, body='', title=None, message_type=MessageType.warning, in_reply_to=None, reports=(), **kwargs):
        with self as r:
            if title:
                r.title(title)
            if in_reply_to:
                r.reply_to(in_reply_to)
            r.text(body)
            r.message_type(message_type)
            with r.field_list() as lst:
                if 'created_timestamp' in kwargs:
                    lst.add(
                        'Last command start time',
                        self.convert_datetime(kwargs.get('created_timestamp'))
                    )
                if 'complete_timestamp' in kwargs:
                    lst.add(
                        'Last command finished time',
                        self.convert_datetime(kwargs.get('complete_timestamp'))
                    )
            for report_name, report_link in reports:
                r.report(report_name, report_link)

    def auto_detailed_list(self, elements, describe_function, title=None, text_function=str, in_reply_to=None):
        with self as r:
            if title:
                r.title(title)
            if in_reply_to:
                r.reply_to(in_reply_to)
            r.message_type(MessageType.info)
            with r.detailed_list() as lst:
                for el in elements:
                    lst.add(text_function(el), describe_function(el))

    def auto_enumerated_list(self, elements, title=None, index_function=None, text_function=str, in_reply_to=None):
        if not index_function:
            index_function = none_function
        with self as r:
            if title:
                r.title(title)
            if in_reply_to:
                r.reply_to(in_reply_to)
            r.message_type(MessageType.info)
            with r.enumerated_list() as lst:
                for el in elements:
                    lst.add(text_function(el), index_function(el))

    def auto_bulleted_list(self, elements, title=None, text_function=str, in_reply_to=None):
        with self as r:
            if title:
                r.title(title)
            if in_reply_to:
                r.reply_to(in_reply_to)
            r.message_type(MessageType.info)
            with r.bulleted_list() as lst:
                for el in elements:
                    lst.add(text_function(el))
