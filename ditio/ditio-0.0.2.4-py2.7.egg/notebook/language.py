

class Python:
    COMMENT="#"
    EXTENSION=".py"


class Java:
    COMMENT="//"
    EXTENSION=".java" 

class Clojure:
    COMMENT=";;"
    EXTENSION=".cjs"

class Groovy:
    COMMENT="//"
    EXTENSION=".groovy" 

class Javascript:
    COMMENT="//"
    EXTENSION=".js" 

__language__ = None 
def set(l):
    global __language__ 
    __language__  = l
def get():
    global __language__ 
    return __language__ 

   
