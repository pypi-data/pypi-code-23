import re
from docx import Document

class DocumentHandler:
    def __init__(self, path):
        with open(path, 'rb') as f:
            self.document = Document(f)

    def save(self, filename):
        self.document.save(filename)
