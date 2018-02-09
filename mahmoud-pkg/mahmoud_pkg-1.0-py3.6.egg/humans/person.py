class Person():
     def __init__(self, name, age, address):
         self.name = name
         self.age = age
         self.address = address
    
     def __str__(self):
         return("%s is %s years old and lives in %s" % (self.name, self.age, self.address))
