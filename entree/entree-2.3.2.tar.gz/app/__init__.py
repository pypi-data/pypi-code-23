#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
.. module:: entree.app
.. moduleauthor:: Julien Spronck
.. created:: March 2018
'''

# Import dependencies
import datetime
import io
import os
import re
import shutil
import time
import traceback
import zipfile

from flask import Flask, render_template, url_for
from flask import jsonify, request, redirect, send_file, send_from_directory

from entree.projects import CLASSES, CLASS_LONG_NAMES
from entree.utils import (
    copy_file_structure,
    create_single_file,
    get_all_dirs_and_files,
    filemap
)

__version__ = '1.0'

app = Flask(__name__)

FILEROOT, FILEBASE = os.path.split(__file__)
FILES_TO_IGNORE = ['.DS_Store']


# Routes
# Main route
@app.route('/')
def home():
    '''Main flask route
    '''
    error = request.args.get('error', default='')
    # if error is None:
    #     error = ''
    return render_template('index.html', project_types=CLASS_LONG_NAMES,
                           error=error)


# form submission route
@app.route('/submit', methods=['POST'])
def submit():
    try:
        accepted_fields = ['email', 'name', 'projectname', 'projecttype',
                           'url']
        fields = sorted(list(request.form.keys()))
        for field in fields:
            if (field not in accepted_fields and
                    not field.startswith('cb_')):
                raise ValueError('Wrong fields in request')

        # Get data from form
        # Project name and type
        modname = request.form['projectname']

        if not re.match('^[a-zA-Z][a-zA-Z0-9_]*$', modname):
            return redirect(url_for('home', error='Wrong format for '
                                                  'project name'))

        project_type = request.form['projecttype']
        if project_type not in CLASS_LONG_NAMES:
            return redirect(url_for('home', error='Project type unsupported'))

        # Author information
        config = {}
        config['author'] = request.form['name']

        if '@' in request.form['email']:
            emailsplit = request.form['email'].split('@')
        else:
            emailsplit = ['', '']

        config['author_email_prefix'] = emailsplit[0]
        config['author_email_suffix'] = emailsplit[1]

        config['author_url'] = request.form['url']

        creation_date = datetime.datetime.now()

        # Get the class corresponding to the given project type
        project_cls = [class_ for class_ in CLASSES.values()
                       if class_.project_long_name == project_type][0]

        partial = [os.path.join(project_cls.template_path(), tname[3:])
                   for tname in request.form
                   if tname.startswith('cb_')]

        # Create a zip file with the content
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zipf:
            # Copy entire file structure from template directory to the project
            # directory
            copy_file_structure('.', project_cls.template_path(),
                                replace=project_cls.replace, zipf=zipf,
                                files_to_ignore=FILES_TO_IGNORE,
                                partial=partial,
                                modname=modname, config=config,
                                creation_date=creation_date)

        memory_file.seek(0)
        return send_file(memory_file, attachment_filename=modname+'.zip',
                         as_attachment=True)
    except:
        traceback.print_exc()
        return redirect(url_for('home', error='Oh no! Looks like '
                                'there was a problem.'))
    # return send_from_directory(directory=rootdir,
    #                            filename=modname+'.zip')
    # # Redirect to home page
    # return redirect('/')


# form submission route
@app.route('/filestructure/<project_type>', methods=['GET'])
def filestructure(project_type='Python'):
    '''Returns file structure for a given project type
    '''
    if project_type not in CLASS_LONG_NAMES:
        return redirect(url_for('home', error='Project type unsupported'))

    modname = request.args.get('projectname', default='')
    if modname == '':
        modname = 'src'

    # Get the class corresponding to the given project type
    project_cls = [class_ for class_ in CLASSES.values()
                   if class_.project_long_name == project_type][0]

    dirs, files = get_all_dirs_and_files(project_cls.template_path(),
                                         files_to_ignore=FILES_TO_IGNORE)
    dirs = filemap(dirs, replace=project_cls.replace, modname=modname)
    files = filemap(files, replace=project_cls.replace, modname=modname)

    return jsonify({
        'dirs': dirs,
        'files': files
    })

if __name__ == "__main__":
    app.run()
