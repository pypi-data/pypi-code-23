import sys
a = sys.path
b = ''
for i in a:
    if i.endswith('site-packages'):
        b = i

print(b)
