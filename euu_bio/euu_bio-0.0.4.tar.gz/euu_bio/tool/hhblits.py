#! /usr/bin/env python
#################################################################################
#     File Name           :     hhblits.py
#     Created By          :     qing
#     Creation Date       :     [2018-02-20 09:55]
#     Last Modified       :     [2018-02-21 10:28]
#     Description         :      
#################################################################################
import subprocess
from euu.common.schedule import schedule_bar

_settings = {
    'database': None,
    'n_iters': 3,
    'maxfilt': 500000,
    'diff': 'inf',
    'cov': 50,
    'e_value': 0.001,
    'n_threads': 20,
    'id': 99,
    'command': 'hhblits'
}

def config(**kwargs):
    for key, value in kwargs.items():
        if key not in _settings:
            raise Exception("Unknown HHBlits parameter {:}".format(key))
        if value:
            _settings[key] = value

def run_worker(args):
    input_file, output_file = args
    for key, value in _settings.items():
        if not value:
            raise Exception("HHBlits parameter {:} not set".format(key))
        _settings[key] = str(value)
    run_args = [_settings['command'],
                '-i', input_file,
                '-d', _settings['database'],
                '-oa3m', output_file,
                '-n', _settings['n_iters'],
		'-maxfilt', _settings['maxfilt'],
                '-diff', _settings['diff'],
                '-id', _settings['id'],
                '-cov', _settings['cov'],
                '-e', _settings['e_value'],
                '-cpu', _settings['n_threads']]
    print(" ".join(run_args))
    p = subprocess.Popen(run_args)
    p.wait()
    
def run(input_file, output_file):
    run_worker((input_file, output_file))

def par_run(input_files, output_files, n_process=4):
    result = schedule_bar(run_worker, list(zip(input_files, output_files)), n_process)
    for r in result:
        pass
