from ipykernel.kernelbase import Kernel
from problog.program import PrologString
from problog.engine import DefaultEngine
from problog.errors import ProbLogError
from problog import get_evaluatable

class ProbLogKernel(Kernel):
    implementation = 'ProbLog'
    implementation_version = '1.0'
    language = 'problog'
    language_version = '2.1'
    codemirror_mode = 'prolog'
    pygments_lexer = 'prolog'
    
    language_info = {
        'name': 'ProbLog',
        'mimetype': 'text/x-prolog',
        'file_extension': '.pl',
    }
    banner = "ProbLog - Probabilistic Logic Programming"

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
            
        try:                   
            pl = PrologString(code)
            db = DefaultEngine().prepare(pl)
            
            result = get_evaluatable().create_from(db).evaluate()
            if not silent:
                stream_content = {'name': 'stdout', 'text': str(result)}
                self.send_response(self.iopub_socket, 'stream', stream_content)
            return {'status': 'ok',
                    # The base class increments the execution count
                    'execution_count': self.execution_count,
                    'payload': [],
                    'user_expressions': {},
                   }

        except ProbLogError as err:
            stream_content = {'name': 'stderr', 'text': str(err)}
            self.send_response(self.iopub_socket, 'stream', stream_content)
            return {
                'status': 'error',
                'ename': err.__class__.__name__,
                'evalue': str(err)
            }
                   

