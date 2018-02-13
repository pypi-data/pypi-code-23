from lib.filters import get_filter


class Elem:
    def __init__(self, text, loc, size):
        self.text = text
        self.loc = loc
        self.size = size


e1 = Elem('foo', {'x': 10, 'y': 10}, {'width': 20, 'height': 90})
e2 = Elem('bar', {'x': 30, 'y': 50}, {'width': 25, 'height': 30})
frame = Elem('frame', {'x': 0, 'y': 0}, {'width': 50, 'height': 100})
elems = [e1, e2]

f = get_filter('within_frame', frame=frame)
filtered = filter(f, elems)
assert e1 in filtered
assert e2 not in filtered
for elem in filtered:
    print elem.text