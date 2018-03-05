#   This file is part of the program djaTeX.
#
#   Copyright (C) 2017 by Marc Culler and others. 
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   Project homepage: https://bitbucket.org/marc_culler/djatex
#   Author homepage: https://marc-culler.info

from . import LaTeXFile
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template

def render_latex(request, filename, template_name,
                 error_template_name=None, bib_template_name=None,
                 home_dir=None, context=None):
    """
    This shortcut function accepts a LaTeX template file and returns an HttpResponse.
    If the LaTeX compiles without error, the response will have content_type
    application/pdf and the content data will be the PDF rendering of the LaTeX source.
    The filename argument is the name of the PDF file.

    If the optional bib_template_name is provided then the LaTeX will be compiled with
    the usual pdflatex bibtex pdflatex pdflatex drill.  Otherwise, pdflatex will be run
    once and, if the output specifies undefined references, a second time.

    If the optional home_dir argument is supplied it should be an absolute path to
    a directory containing any files which are required to compile the LaTeX template.
    These will be symlinked into the temporary compilatin directory before running
    LaTeX.

    If there are errors then the response returned by this function will be a
    Server Error if no error_template_name is provided.  If an
    error_template_name is provided then that template will be rendered with a
    context dictionary having three keys.  The first, named 'stage' has value
    either 'latex' or 'bibtex' and specifies which TeX executable failed.  The
    other two, 'output' and 'source' contain the stdout of the TeX executable
    and the input LaTeX or BibTex.  The values are lists of strings, to enable
    the error template to display the results with the same line breaks,
    possibly including line numbers.
    """ 
    template = get_template(template_name)
    source = template.render(context).encode('utf8')
    if bib_template_name:
        bib_template = get_template(bib_template_name)
        bib_source = bib_template.render(context).encode('utf8')
    else:
        bib_source = None
    file = LaTeXFile(source, bibtex_source=bib_source, home_dir=home_dir)
    file.compile()
    error_context = file.errors()
    if error_context:
        if error_template_name:
            return render(request, error_template_name, context=error_context)
        else:
            return HttpResponseServerError()
    else:
        response = HttpResponse(file.pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"'%filename
        return response
