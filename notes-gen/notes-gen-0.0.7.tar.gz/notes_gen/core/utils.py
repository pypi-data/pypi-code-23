import subprocess
import os
from bs4 import BeautifulSoup

from notes_gen.core.exceptions import PandocException


class Pandoc:

    @classmethod
    def __excute_command(cls, command, get_output=False, cwd=None):

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, cwd=cwd)
        return_value = process.wait()
        if return_value != 0:
            raise PandocException()

        # Return output
        if get_output is True:
            return process.stdout.read()

    @classmethod
    def file_to_pdf(cls, markdown_file_path, pdf_file_path):
        '''Convert a markdown_file to pdf
        '''

        command = 'pandoc {markdown_file} -o {pdf_file} --mathjax --toc'.format(markdown_file=markdown_file_path, pdf_file=pdf_file_path)
        cls.__excute_command(command, cwd=os.path.dirname(markdown_file_path))

    @classmethod
    def file_to_latex(cls, markdown_file_path, late_file_path):
        '''Convert a markdown_file to latex
        '''

        command = 'pandoc {markdown_file} -o {latex_file} --mathjax --toc'.format(markdown_file=markdown_file_path, latex_file=late_file_path)
        cls.__excute_command(command, cwd=os.path.dirname(markdown_file_path))

    @classmethod
    def to_html_string(cls, markdown_file_path):
        '''Convert markdown to html string
        '''
        command = 'pandoc -f markdown -t html {markdown_file} --mathjax --toc --standalone'.format(markdown_file=markdown_file_path)
        output = cls.__excute_command(command, get_output=True, cwd=os.path.dirname(markdown_file_path)).decode('utf-8')

        html = BeautifulSoup(output, 'html.parser')
        body = BeautifulSoup(''.join(map(str, html.body.contents)), 'html.parser')
        # Remove header from the body
        body.find('div', id='header').decompose()

        # Add content header in TOC
        content_header = BeautifulSoup('<h1>Contents</h1>', 'html.parser')
        body.find('div', id='TOC').insert(1, content_header)

        return str(body)
