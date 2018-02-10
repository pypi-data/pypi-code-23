from timeit import timeit


y = 'y'
x = 'x'
z = 'z'
print(timeit("y if not y else x if not x else z", globals=globals(), number=10**7))
print(timeit("y and x and z", globals=globals(), number=10**7))

if not y:
    y
else:
    if not x:
        x
    else:
        z
