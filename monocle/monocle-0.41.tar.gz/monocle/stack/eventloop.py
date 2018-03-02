import monocle
import os
if monocle._stack_name == 'twisted' or os.getenv('MONOCLE_STACK') == 'twisted':
    from monocle.twisted_stack.eventloop import *
elif monocle._stack_name == 'tornado' or os.getenv('MONOCLE_STACK') == 'tornado':
    from monocle.tornado_stack.eventloop import *
elif monocle._stack_name == 'asyncore' or os.getenv('MONOCLE_STACK') == 'asyncore':
    from monocle.asyncore_stack.eventloop import *
else:
    raise ImportError(
        "Could not import stack.\n"
        "Ensure you have called monocle.init()\n"
        "or defined MONOCLE_STACK=<stack> in the environment")
