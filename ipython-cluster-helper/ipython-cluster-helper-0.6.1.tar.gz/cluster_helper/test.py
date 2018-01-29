# sample.py
myGlobal = 5

def func1():
    myGlobal = 42

def func2():
    print myGlobal

func1()
func2()

def func1():
    global myGlobal
    myGlobal = 42

func1()

print myGlobal
