class Car():

    def __init__(self, color, type, make, license):
        self.color = color
        self.type = type
        self.make = make
        self.license = license


    def __str__(self):
        return( "A %s %s %s with license number %s" % (self.color, self.type, self.make, self.license) )



