import pickle

def save_object(obj, filename):
    with open(filename, "wb") as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
        
def load_object(filename):
    with open(filename, "rb") as input:
        return pickle.load(input)
        
class Company(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
c1 = Company("jo",32)

print(c1)
        
save_object(c1,"test")

del c1

c1 = load_object("test")

print(c1)
