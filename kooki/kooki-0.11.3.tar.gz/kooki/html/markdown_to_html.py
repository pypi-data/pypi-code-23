import mistune

def markdown_to_html(content):
    renderer = HTMLRenderer()
    markdown = mistune.Markdown(renderer=renderer)
    return markdown(content)


class HTMLRenderer(mistune.Renderer):

    def block_code(self, code, language):
        result = '<pre><code>{}</code></pre>'.format(code)
        return result

    def block_quote(self, text):
        return '<blockquote>{}</blockquote>'.format(text)

    def block_html(self, html):
        return html

    def header(self, text, level, raw):
        return '<h{0}>{1}</h{0}>'.format(level, text)

    def hrule(self):
        return '<hr/>'

    def list(self, body, ordered):
        if ordered:
            return '<ol>{}</ol>'.format(body)
        else:
            return '<ul>{}</ul>'.format(body)

    def list_item(self, text):
        return '<li>{}</li>'.format(text)

    def paragraph(self, text):
        return '<p>{}</p>'.format(text)

    def autolink(self, link, is_email=False):
        return '<a href="{0}">{0}</a>'.format(link)

    def codespan(self, text):
        return '<code>{}</code>'.format(text)

    def double_emphasis(self, text):
        return '<strong>{}</strong>'.format(text)

    def emphasis(self, text):
        return '<em>{}</em>'.format(text)

    def image(self, src, title, alt_text):
        from kooki.image import get_image
        image = get_image(src)
        return '<img src="{}" title="{}" alt="{}"/>'.format(image, title, alt_text)

    def link(self, link, title, content):
        return '<a href="{}" title="{}">{}</a>'.format(link, title, content)

    def strikethrough(self, text):
        return '<strike>{}</strike>'.format(text)

    def text(self, text):
        return text

    def inline_html(self, text):
        return text

    def linebreak(self):
        return ''

    def newline(self):
        return ''
