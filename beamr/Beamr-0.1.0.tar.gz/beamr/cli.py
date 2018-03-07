#!/usr/bin/env python3
# encoding: utf-8
'''
Beamr

@author:     Teodor Gherasim Nistor

@copyright:  2018 Teodor Gherasim Nistor

@license:    MIT License
'''

import sys
import beamr.debug as debug
from beamr.interpreters.config import Config
from docopt import docopt
from subprocess import run, PIPE

_cli_name = 'beamr'

arg = {
    'name': 'Beamr',
    'version': '0.1.0',
    'description': 'A tool for easily creating LaTeX-powered slide shows from plain text',
    'long_description': 'TBC',
    'keywords': 'TBC',
    'url': 'https://teonistor.github.io/beamr',
    'project_urls': {
        'Documentation': 'https://teonistor.github.io/beamr',
        'Source': 'https://github.com/teonistor/beamr/'},
    'author': 'Teodor G Nistor',
    'author_email': 'tn1g15@ecs.soton.ac.uk',
    'license': 'MIT',
    'classifiers': ['Programming Language :: Python :: 3', 'Development Status :: 4 - Beta'],
    'install_requires': ['ply', 'pyaml', 'docopt'],
    'python_requires': '>=3',
    'entry_points': {
        'console_scripts': [
            '%s=beamr.cli:main' % _cli_name,
        ],
    }
}

def main():
    global arg
    halp = '''%s - %s

    Usage:
        %s [-n|-p <cmd>] [-q|-v] [-u|-s] [-c <cfg>] [--] [- | <input-file>] [- | <output-file>]
        %s (-h|-e [<editor>]) [-v]
        %s --version

    Options:
        -p <cmd>, --pdflatex=<cmd>  Specify pdflatex executable name and/or path to [default: pdflatex]
        -c <cfg>, --config=<cfg>    Override configuration. <cfg> must be valid Yaml
        -e, --edit-config     Open user configuration file for editing. An editor must be specified if configuration doesn't exist or doesn't mention one
        -n, --no-pdf   Don't create PDF output file (just generate Latex source)
        -u, --unsafe   Trust certain user input which cannot be verified
        -s, --safe     Don't trust user input which cannot be verified
        -v, --verbose  Print inner workings of the lexer-parser-interpreter cycle to stderr
        -q, --quiet    Print nothing except fatal errors to stderr
        -h, --help     Show this message and exit.
        --version      Print version information
''' % (arg['name'], arg['description'], _cli_name, _cli_name, _cli_name)

    # Parse arguments nicely with docopt
    arg = docopt(halp,  version=arg['version'])

    # Set logging level
    if arg['--verbose']:
        debug.verbose = True
    if arg['--quiet']:
        debug.quiet = True

    # Docopt arguments themselves need debugging sometimes...
    debug.debug('args:', str(arg).replace('\n', ''))

    # If configuration editing mode, delegate to Config
    if arg['--edit-config']:
        return Config.editUserConfig(arg['<editor>'])

    # Decode other configuration

    # Establish pdflatex command and parameters if required
    pdflatex = None
    if not arg['--no-pdf']:
        pdflatex = [arg['--pdflatex'], '-shell-escape']
        if arg['<output-file>']:
            outFile = arg['<output-file>']
            arg['<output-file>'] = None
            i = outFile.rfind('/') + 1
            if (i > 0):
                pdflatex.append('-output-directory=' + outFile[:i])
            pdflatex.append('-jobname=' + outFile[i:])

    # Open I/O files where relevant
    if arg['<input-file>']:
        sys.stdin = open(arg['<input-file>'], 'r')
    if arg['<output-file>']:
        sys.stdout = open(arg['<output-file>'], 'w')

    # Only after setting logging level import our interpreters
    from beamr.interpreters import Document

    with sys.stdin:
        with sys.stdout:

            # Parse document
            doc = Document(sys.stdin.read())
            tex = str(doc)

            # Run pdflatex on obtained tex source
            if pdflatex:
                runkwarg = {'input': tex, 'encoding': 'utf-8'} # TODO Investigate encoding gotchas

                # If quiet mode enabled, pipe output of pdflatex to this process, where it can be ignored
                if debug.quiet:
                    runkwarg.update({'stdout': PIPE, 'stderr': PIPE})
                
                sp = run(pdflatex, **runkwarg)
                if sp.returncode:
                    debug.err('Fatal: pdflatex exited with nonzero status', sp.returncode)
                    return sp.returncode

            # Just output tex source
            else:
                print(tex)


if __name__ == "__main__":
    sys.exit(main())
