from bymtesting.WebApi.WebApiServiceBasePayload import *


class SeedDataTemplate:

    def __init__(self):
        self.developers = []

    def createGrunnDataTemplate(self):
        # ProsesskodeEnhet
        #self.prosesskodeenheter[ProsesskodeEnhetKeys.stk] = ProsesskodeEnhet( "stk", "MULTIPLY")
        print("GrunndataTemplate")

    def createTestDataTemplate(self):
        for i in range(1, 10):
            self.developers.append(Developer("Amanda {}".format(i)))
