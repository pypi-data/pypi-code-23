import os
from jinja2 import FileSystemLoader, Environment

TEMPLATE_DIR = os.path.abspath(os.path.join(__file__, '..', 'templates'))
ENV = Environment(loader = FileSystemLoader(TEMPLATE_DIR))
