

debug_level= False 

def set_debug(flag):
    global debug_level
    debug_level = flag 

def log(line):
    global debug_level 
    if debug_level == True:
        print line 

trace_level = False 

def set_trace(flag):
    global trace_level
    trace_level = flag 

def trace(line): 
    trace_header = "" 
    if trace_level == True:
        print "%s" % (line) 
