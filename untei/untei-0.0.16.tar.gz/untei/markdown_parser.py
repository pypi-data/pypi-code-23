from parsimonious.grammar import Grammar
import datetime

syntax = '''
document           = breakline* config breakline* body breakline*
_                  = (~"[ ]*") / breakline*
config             = settings
settings           = setting*
setting            = setting_key assignment_symbol setting_value breakline*
setting_key        = ~"[a-z_]+"
setting_value      = ~"[^ \\n][^\\n]+"
assignment_symbol  = ~"[ ]*" "=" ~"[ ]*"
body               = blocks
blocks             = block*
block              = self_defined_block / comment / list / image / horizontal / math_block / code_block / h1 / h2 / h3/ h4 / h5 / h6 / paragraph / breakline*
comment            = "<!--" content_comment "-->"
content_comment    = (!"-->" ~"." breakline?)*
list               = list_item+
list_item          = list_flag char_component breakline*
list_flag          = ("* ") / ("- ")
image              = "![" chars "](" chars ")"
horizontal         = ~"----*"
square_bracket     = "[" (!"]" ~".")+ "]"
round_bracket      = "(" (!")" ~".")+ ")"
h1                 = "# " char_components breakline?
h2                 = "## " char_components breakline?
h3                 = "### " char_components breakline?
h4                 = "#### " char_components breakline?
h5                 = "##### " char_components breakline?
h6                 = "###### " char_components breakline?
math_block         = "$$" math_expression "$$"
code_block         = "```" code_block_option code_chars "```"
code_block_option  = ~"[^\\n]*" breakline
paragraph          = char_components breakline+
char_components    = char_component*
char_component     = bold / italic / link / math_inline / inline_code / chars / _
bold               = "**" content_bold "**"
content_bold       = (!"**" !"\\n" ~".")*
italic             = "_" content_italic "_"
content_italic     = (!"_" !"\\n" ~".")*
link               = square_bracket round_bracket
math_inline        = "$" math_expression "$"
math_expression    = ~"[^$]+"
inline_code        = "`" (!"`" ~".")+ "`"
breakline          = ~"[\\r\\n]"
chars              = (!" **" !" _" !" `" !" $" !"[" ~".")+
code_chars         = ~"[^`]*"
self_defined_block = definition / table_of_content
definition         = "def. " chars breakline indented_line*
indented_line      = ~"[ ]+" char_components breakline
table_of_content   = "[toc]" / "[TOC]"
'''

grammar = Grammar(syntax)

def create_user_defined_box(blocktype, name, body):
     if (blocktype == "definition"):
        header  =  "<span class='definition_box_title'><span class='definition_box_flag'>def.</span> " + name + "</span><br>\n"
        boxbody =  "<p class='definition_box_body'>" + body + "</p>"
        return "<div class='common_box definition_box'>" + header + boxbody + "</div>"

class ParseResult:
    def __init__(self, operand):
        root = grammar.parse(operand + "\n")

        def default(node, children):
            return children

        def square_bracket(node, children):
            return node.text[1:len(node.text)-1]
        def round_bracket(node, children):
            return node.text[1:len(node.text)-1]

        def comment(node, children):
            return ""

        def config(node, children):
            return ""

        def image(node, children):
            return "<img alt='" + node.children[1].text + "' src='" + node.children[3].text + "'>"

        def horizontal(node, children):
            return "<hr>"

        def list(node, children):
            s = ""
            for child in children:
                s = s + child
            return s

        def list_item(node, children):
            return "<li>" + children[1] + "</li>"

        def h1(node, children):
            return "<h1>" + node.children[1].text + "</h1>"

        def h2(node, children):
            return "<h2>" + node.children[1].text + "</h2>"

        def h3(node, children):
            return "<h3>" + node.children[1].text + "</h3>"

        def h4(node, children):
            return "<h4>" + node.children[1].text + "</h4>"

        def h5(node, children):
            return "<h5>" + node.children[1].text + "</h5>"

        def h6(node, children):
            return "<h6>" + node.children[1].text + "</h6>"

        def chars(node, children):
            return node.text

        def blocks(node, children):
            s = ""
            for child in children:
                s = s + child
            return s

        def _(node, children):
            return " "

        def block(node, children):
            s = ""
            for child in children[0]:
                s = s + child
            return s

        def code_block(node, children):
            code = node.children[2].text.replace("<", "&lt;").replace(">", "&gt;")
            return "<div class='common_box code_block'><pre><code>" + code + "</code></pre></div>"

        def char_component(node, children):
            return children[0]


        def char_compomnents(node, children):
            return children[0]

        def content_bold(node, children):
            return node.text
        def content_italic(node, children):
            return node.text

        def content_link(node, children):
            return node.text

        def document(node, children):
            return children[3]

        def paragraph(node, children):
            s = ""
            for child in children[0]:
                s = s + child
            return "<p>" + s + "</p>"

        def bold(node,children):
            return "<strong>" + children[1] + "</strong>"

        def italic(node,children):
            return "<i>" + children[1] + "</i>"

        def math_block(node, children):
            return "$$" + node.children[1].text + "$$"

        def math_inline(node,children):
            return "$" + node.children[1].text + "$"

        def math_expression(node, children):
            return node.text

        def inline_code(node,children):
            return "<code class='common_box code_block'>" + node.children[1].text + "</code>"

        def link(node, children):
            return "<a href='" + children[1] + "'>" + children[0] + "</a>"

        def breakline(node,children):
            return "<br />"

        def self_defined_block(node, children):
            return children[0]

        def definition(node, children):
            return create_user_defined_box("definition", node.children[1].text, node.children[3].text)

        def indented_line(node, children):
            return node.children[1].text

        def table_of_content(node, children):
            return ""

        def chars_underlined(node, children):
            return "_" + children[1]

        parse_locals = locals()
        def visit(node):
            method = parse_locals.get(node.expr_name, default)
            return method(node, [visit(child) for child in node.children])

        self.content = visit(root)
        self.title = None
        self.tags = []
        self.authors = []
        self.date = None
        self.status = "ArticleStatusReady"

        config = root.children[1].children
        for setting in config:
            key = setting.children[0].text
            value = setting.children[2].text
            if key == "title":
                self.title = value
            elif key == "tags":
                self.tags = value.split(", ")
            elif key == "authors":
                self.authors = value
            elif key == "date":
                d = [int(x) for x in value.split("-")]
                self.date = datetime.date(d[0], d[1], d[2])
            elif key == "status":
                self.status = value
            else:
                print("Unknown key: ", key)
