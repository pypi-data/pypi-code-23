from pygments.lexer import RegexLexer, include
from pygments.token import *

class TigerLexer(RegexLexer):
    name = 'Tiger'
    aliases = ['tiger']
    filenames = ['*.tc', '*.tiger']

    keywords = (
        'break', 'class', 'do', 'else', 'end', 'extends', 'for', 'function',
        'if', 'import', 'in', 'let', 'method', 'new', 'of', 'primitive',
        'then', 'to', 'type', 'var', 'while',
    )

    operators = (
        ',', ':', ';', r'\(', r'\)', r'\[', r'\]', r'\{', r'\}', r'\.', r'\+',
        '-', r'\*', '/', '=', '<>', '<', '<=', '>', '>=', '&', r'\|', ':=',
    )

    identifier = r'([a-zA-Z][a-zA-Z_0-9]*|_main)'

    tokens = {
        'whitespace': [
            (r'[\n\r\s]+', Text),
        ],
        'comment': [
            (r'[^/*]+', Comment),
            (r'/\*', Comment, '#push'),
            (r'\*/', Comment, '#pop'),
        ],
        'escape-sequence': [
            (r'\\[abfnrtv]', String.Escape),
            (r'\\\\', String.Escape),
            (r'\\"', String.Escape),
            (r'\\[0-9]{3}', String.Escape),
            (r'\\x[0-9a-fA-F]{2}', String.Escape),
        ],
        'string': [
            (r'[^\\"]+', String),
            include('escape-sequence'),
            (r'"', String, '#pop'),
        ],
        'root': [
            include('whitespace'),
            (r'/\*', Comment, 'comment'),
            (r'\b({})\b'.format('|'.join(keywords)), Keyword),
            (r'({})'.format('|'.join(operators)), Operator),
            (r'(nil)', Keyword.Constant),
            (r'(array)', Keyword.Type),
            (r'\d+', Number),
            (identifier, Name),
            (r'"', String, 'string'),
            (r'\S+', Text),
        ],
    }
