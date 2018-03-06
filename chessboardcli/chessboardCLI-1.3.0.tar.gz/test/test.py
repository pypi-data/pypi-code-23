def a():
    raise Exception()

def b():
    a()
    print('hi')

try:
    b()
except:
    print('fuck')
