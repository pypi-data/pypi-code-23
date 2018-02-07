import os
import readline
import glob
import sys


def err_input( prompt):
    t = tabCompleter()
    readline.set_completer_delims('\t')
    readline.parse_and_bind('tab: complete')
    readline.set_completer(t.pathCompleter)
    
    sys.stderr.write(prompt)
    inp = input('')
    return inp

def out_input( prompt):
    t = tabCompleter()
    readline.set_completer_delims('\t')
    readline.parse_and_bind('tab: complete')
    readline.set_completer(t.pathCompleter)
    
    inp = input(prompt)
    return inp



class tabCompleter(object):
    """ 
    From https://gist.github.com/iamatypeofwalrus/5637895
    Modified for use by David Danko
    """
    def pathCompleter(self,text,state):
        line   = readline.get_line_buffer().split()
        return [x for x in glob.glob(text+'*')][state]