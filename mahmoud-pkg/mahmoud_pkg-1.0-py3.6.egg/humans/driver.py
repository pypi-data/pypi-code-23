from .person import Person


class Driver(Person):
    def __init__(self, name, age, address, licenseType, licenseNu):
        Person.__init__(self, name, age, address)
        self.licenseType = licenseType
        slef.licenseNu = licenseNu
    
    def get_licence_details(self):
        return((licenseType, licenseNu))
