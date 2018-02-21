"""
MIT License
Copyright (c) 2017 Roni Eliezer
"""

import datetime

timestamp = None

#======================================================================
def generate_timestamp():
    """ Generate a formated time stamp string. 
    e.g.: '2017-09-11-10-17-41-189150'
    
    This function must be called once in a test session
    It's used to sign the test run session 
    Local report directory name and pytest session ID are using it 
    
    Returns:
        The output will be saved at the global 'timestamp' variable
        call to get_timestamp() to get this global variable
    """
    global timestamp
    timestamp = datetime.datetime.now().__str__().replace(" ", "-").replace(":", "-").replace(".","-")


#======================================================================
def get_timestamp():
    """Return the value of the 'timestamp' global variable.
    
    generate_timestamp() must be called before calling current function
    """
    global timestamp
    
    if timestamp == None:
        generate_timestamp()
        
    return timestamp
