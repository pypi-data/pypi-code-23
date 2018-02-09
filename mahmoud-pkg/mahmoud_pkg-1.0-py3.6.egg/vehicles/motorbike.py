class MotorBikes():

    def __init__(self, color, make, license):
        self.color = color
        self.make = make
        self.license = license


    def __str__(self):
        return("A %s %s motorbike with license number %s." % (self.color, self.make, self.license))
