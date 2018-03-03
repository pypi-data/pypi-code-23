from .base import BaseProcessor

import markdown2

template = """
{{% extends('{template}') %}}
{{% block article %}}
{content}
{{% endblock %}}
"""

class MarkdownProcessor(BaseProcessor):

    def process(self, input, vars):
        result = markdown2.markdown(input, extras=['footnotes','fenced-code-blocks'])
        template_result = template.format(template='article.html', content=result)
        return template_result