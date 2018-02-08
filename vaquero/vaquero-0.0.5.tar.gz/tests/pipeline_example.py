def f(items):
    items.append(100)

def g(items):
    items.append(items.pop() * 2)

def h(items):
    items.extend([items.pop()] * 10)
