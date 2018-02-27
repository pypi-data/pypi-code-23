def _custom_for_suffix(suffix):
    import subprocess
    import shutil
    import os
    import sys
    import pathlib2
    custom_dir = pathlib2.os.path.join(subprocess.check_output('jupyter --config-dir',shell=True).strip(), b'custom')
    custom_css_path = pathlib2.os.path.join(custom_dir, b'custom.css')
    custom_css_sources_path = pathlib2.os.path.join(sys.prefix,'share/jupyterdevview/custom.css')
    if not os.path.exists(custom_dir):
        os.makedirs(custom_dir)
    shutil.copy('{}.{}'.format(custom_css_sources_path, suffix), custom_css_path)

def dev_view():
    """Switch jupyter to dev view"""
    _custom_for_suffix('dev')

def notebook_view():
    """Switch jupyter to notebook view"""
    _custom_for_suffix('notebook')
