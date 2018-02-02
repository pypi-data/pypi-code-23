import warnings

from bureaucracy.powerpoint.placeholders import (CONTEXT_KEY_FOR_PLACEHOLDER,
                                                 AlreadyRenderedException)
from bureaucracy.powerpoint.slides import (CONTEXT_KEY_FOR_SLIDE,
                                           StopSlideRender)
from bureaucracy.powerpoint.tables import CONTEXT_KEY_FOR_TABLE, TableContainer
from django import template
from django.template import TemplateSyntaxError

register = template.Library()


class PPTTagNode(template.Node):
    def render_in_place(self, context, placeholder):
        raise NotImplementedError

    def render(self, context):
        try:
            placeholder = context[CONTEXT_KEY_FOR_PLACEHOLDER]
            self.render_in_place(context, placeholder)
        except KeyError:
            warnings.warn("placeholder was not found in context passed to template tag {}. it will not be "
                          "rendered.".format(self.__class__))
        raise AlreadyRenderedException


class LinkNode(PPTTagNode):
    def __init__(self, url_expr, title_expr):
        self.url_expr = url_expr
        self.title_expr = title_expr

    def render_in_place(self, context, placeholder):
        url, title = self.url_expr.resolve(context), self.title_expr.resolve(context)
        placeholder.insert_link(url, title)


@register.tag
def link(parser, token):
    bits = token.split_contents()
    if len(bits) != 3:
        raise TemplateSyntaxError("The '%r' tag requires two arguments: url and title", bits[0])
    url_expr, title_expr = parser.compile_filter(bits[1]), parser.compile_filter(bits[2])
    return LinkNode(url_expr, title_expr)


class RepeatUntilEmptyNode(PPTTagNode):
    def __init__(self, objects_expr, stop_on_repeat=False):
        self.objects_expr = objects_expr
        self.stop_on_repeat = stop_on_repeat

    def render_in_place(self, context, placeholder):
        objects = self.objects_expr.resolve(context)

        placeholder.remove()

        if objects:
            context[CONTEXT_KEY_FOR_SLIDE].insert_another()
            # repeat happened, flagged to halt rendering here, so send the signal
            if self.stop_on_repeat:
                raise StopSlideRender


@register.tag
def repeatwhile(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("The '%r' tag requires one argument: an iterable to check.")
    if len(bits) == 3 and bits[-1] != 'stop_on_repeat':
        raise TemplateSyntaxError("The second argument to '%r' should be the flag stop_on_repeat", bits[0])
    objects_expr = parser.compile_filter(bits[1])
    return RepeatUntilEmptyNode(objects_expr, len(bits) == 3)


class PopNode(template.Node):
    def __init__(self, objects_expr, var_expr):
        self.objects_expr = objects_expr
        self.var_expr = var_expr

    def render(self, context):
        objects = self.objects_expr.resolve(context)
        varname = self.var_expr.var.var
        if len(objects) > 0:
            context[varname] = objects.pop(0)
        elif varname in context:
            del context[varname]
        return ''


@register.tag
def pop(parser, token):
    bits = token.split_contents()
    if len(bits) != 4:
        raise TemplateSyntaxError(
            "The %(tag)r tag requires an iterable and as-var: "
            "{% %(tag)r my_list as my_item %}", tag=bits[0]
        )

    if bits[2] != 'as':
        raise TemplateSyntaxError("The %r tag must assign with the 'as' token")

    objects_expr = parser.compile_filter(bits[1])
    var_expr = parser.compile_filter(bits[3])
    return PopNode(objects_expr, var_expr)


class TableNode(PPTTagNode):
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()

        if len(bits) != 2:
            raise TemplateSyntaxError("Table tag expected exactly one argument, got {}".format(len(bits)))

        return cls(parser.compile_filter(bits[1]))

    def __init__(self, contents_expr):
        self.contents_expr = contents_expr

    def render_in_place(self, context, _):
        table_contents = self.contents_expr.resolve(context)

        data_row_count = len(table_contents)

        if not data_row_count:
            return

        data_column_count = len(table_contents[0])

        table_being_rendered = context[CONTEXT_KEY_FOR_TABLE]

        if table_being_rendered.row_count != data_row_count:
            raise TemplateSyntaxError("Number of rows in data does not match number of rows in table on slide.")

        if table_being_rendered.column_count != data_column_count:
            raise TemplateSyntaxError("Number of columns in data does not match number of columns in table on slide.")

        for row_idx, row_values in enumerate(table_contents):
            for col_idx, cell_value in enumerate(row_values):
                table_being_rendered[row_idx, col_idx].text = str(cell_value)


@register.tag
def table(parser, token):
    return TableNode.handle_token(parser, token)


class DynamicTableNode(TableNode):

    def render_in_place(self, context, placeholder):
        table_contents = self.contents_expr.resolve(context)

        n_rows = len(table_contents)

        if not n_rows:
            return ""

        n_cols = len(table_contents[0])
        placeholder = placeholder.insert_table(n_rows, n_cols)

        table_being_rendered = TableContainer(placeholder.table)

        for row_idx, row_values in enumerate(table_contents):
            for col_idx, cell_value in enumerate(row_values):
                table_being_rendered[row_idx, col_idx].text = str(cell_value)

        context[CONTEXT_KEY_FOR_PLACEHOLDER] = placeholder


@register.tag
def dyn_table(parser, token):
    return DynamicTableNode.handle_token(parser, token)
