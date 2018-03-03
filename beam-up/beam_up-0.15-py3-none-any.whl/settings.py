from .processors import JinjaProcessor, MarkdownProcessor, PlainProcessor
from .loaders import FileLoader

SETTINGS = {
    'defaults' : {
        'src-dir' : 'src',
        'build-dir' : 'build',
    },
    'loaders' : [
        {
            'scheme' : 'file',
            'loader' : FileLoader
        }
    ],
    'processors' : [
        {
            'type' : 'html',
            'processors' : [JinjaProcessor],
            'name' : 'HTML'
        },
        {
            'type' : 'md',
            'processors' : [MarkdownProcessor, JinjaProcessor],
            'name' : 'Markdown'
        },
        {
            'type' : 'plain',
            'processors' : [PlainProcessor],
            'name' : 'Plain'
        }
    ],
}