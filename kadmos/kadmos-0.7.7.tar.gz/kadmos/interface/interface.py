import tempfile
import os
import shutil
import ast

from flask import Flask, request, redirect, url_for, send_file, render_template

from kadmos.graph import *


def interface(debug=False, tempdir=None):

    # Initial settings
    app = Flask(__name__)
    if debug:
        app.debug = True
    if tempdir:
        tempfile.tempdir = tempdir

    # Initial variables
    file_types = ['cmdows', 'kdms', 'graphml']
    file_extensions = ['xml', 'kdms', 'graphml']

    # Index
    @app.route("/")
    def index(error=None, message=None, selection=False):
        # Check if error or message is send
        if request.values.get('error', False) and error is None:
            error = request.values['error']
        if request.values.get('message', False) and message is None:
            message = request.values['message']
        # Render index
        return render_template('index.html', types=file_types, error=error, message=message, selection=selection, page='start')

    # Upload
    @app.route("/", methods=['POST'])
    @app.route('/examples/', defaults={'path': ''})
    @app.route('/examples/<path:path>')
    def upload(path=None):
        # Get file
        if path is None:
            f = request.files['file']
            # Check file existence
            if not f:
                return index(error='Please select a KADMOS graph file for uploading.')
            # Get file type
            if request.values.get('file_type', 'auto') != 'auto':
                file_type = request.values.get('file_type')
            elif f.filename.lower().endswith(tuple(file_extensions)):
                file_type = file_types[file_extensions.index(os.path.splitext(f.filename)[1].lower()[1:])]
            else:
                return index(error='The file type could not be recognized. Please specify it.', selection=True)
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            # Move file in temporary directory
            path = os.path.join(temp_dir, 'input.' + file_extensions[file_types.index(file_type)])
            f.save(path)
        # Look for example files in case a path is provided
        else:
            module_path = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(module_path, 'examples', path)
            # Get file type
            file_extension = os.path.splitext(file_path)[1][1:]
            file_type = file_types[file_extensions.index(file_extension)]
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            # Move file in temporary directory
            path = os.path.join(temp_dir, 'input.' + file_extensions[file_types.index(file_type)])
            # Move file in temporary directory
            shutil.copy(file_path, path)
        # Get graph from file
        try:
            loaded = load(path)
        except Exception as error:
            shutil.rmtree(temp_dir)
            error_message = 'The file could not be loaded. Maybe it is not a valid file for storing KADMOS graphs? ' +\
                            '(' + type(error).__name__ + ': ' + str(error) + ')'
            return render_template('index.html', types=file_types,  error=error_message)
        # Save graph for further use
        if len(loaded) == 2:
            loaded[0].save('graph.kdms', destination_folder=temp_dir, mpg=loaded[1])
        else:
            loaded.save('graph.kdms', destination_folder=temp_dir)
        # Send user to view page
        message = 'Here we go! You just uploaded a KADMOS graph file. The graph was imported successfully.'
        return redirect(url_for('view', temp_id=os.path.basename(os.path.normpath(temp_dir)), message=message))

    # View
    @app.route('/<temp_id>')
    @app.route('/<temp_id>/<action>')
    def view(temp_id=None, action=None, error=None, message=None):
        # Check if error or message is send
        if request.values.get('error', False) and error is None:
            error = request.values['error']
        if request.values.get('message', False) and message is None:
            message = request.values['message']
        # Check if files exist
        temp_dir = str(os.path.join(tempfile.gettempdir(), temp_id))
        if not os.path.exists(temp_dir):
            return redirect(url_for('index', error='The requested graph not exist (anymore). Please upload a new file.'))
        # Load graph
        graph = load('graph.kdms', source_folder=temp_dir)
        # Load MPG if it exists
        mpg_path = os.path.join(temp_dir, 'graph_mpg.kdms')
        if os.path.exists(mpg_path):
            mpg = load(mpg_path)
        else:
            mpg = None
        # Get functions if appropriate
        if mpg is None:
            functions = graph.get_function_nodes()
            functions.sort()
        else:
            functions = False
        # Perform actions
        reset = bool(request.args.get('reset', False))
        compressed_labels = bool(request.args.get('compressed_labels', False))
        function_order = request.args.get('function_order', None)
        if function_order is not None:
            function_order = ast.literal_eval(function_order)
        if action == 'pdf':
            if not os.path.exists(os.path.join(temp_dir, 'graph.pdf')) or reset:
                graph.create_dsm('graph',
                                 summarize_vars=compressed_labels,
                                 destination_folder=temp_dir,
                                 mpg=mpg,
                                 function_order=function_order)
            return send_file(os.path.join(temp_dir, 'graph.pdf'))
        if action == 'cmdows':
            pretty_print = bool(request.args.get('pretty_print', False))
            if not os.path.exists(os.path.join(temp_dir, 'graph.xml')) or reset:
                graph.save('graph',
                           file_type='cmdows',
                           destination_folder=temp_dir,
                           description='CMDOWS file created with the KADMOS interface',
                           creator='KADMOS interface',
                           version='1.0',
                           pretty_print=pretty_print,
                           mpg=mpg)
            return send_file(os.path.join(temp_dir, 'graph.xml'), as_attachment=True)
        if action == 'vispack':
            os.chdir(temp_dir)
            if not os.path.exists(os.path.join(temp_dir, 'vispack.zip')) or reset:
                graph.vistoms_create(os.path.join(temp_dir, 'vispack'),
                                     mpg=mpg,
                                     compress=True,
                                     function_order=function_order)
            return send_file(os.path.join(temp_dir, 'vispack.zip'), as_attachment=True)
        if action == 'delete':
            try:
                shutil.rmtree(temp_dir)
            except OSError:
                pass
            return redirect(url_for('index', message='All files were deleted.'))
        return render_template('view.html', temp_id=temp_id, graph=graph, error=error, message=message, functions=functions)

    # Info
    @app.route('/info')
    def info():
        return render_template('info.html', page='info')

    # Acknowledgements
    @app.route('/acknowledgements')
    def acknowledgements():
        return render_template('acknowledgements.html', page='acknowledgements')

    # Return the interface
    return app

