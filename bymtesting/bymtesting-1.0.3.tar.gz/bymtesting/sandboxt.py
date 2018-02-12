import bymtesting.Autentisering as Autentisering
import bymtesting.Lib as Lib
import bymtesting.Cache as Cache
import bymtesting.Autorisasjon as Autorisasjon
import os
from os.path import dirname


def listModules(package):
    print("======================================")
    print(package.__package__)
    arr = []
    for a in dir(package):
        if "__" not in a:
            arr.append(a)
    print(arr)
    print("")

################## list packages and their modules ##########
listModules(Autentisering)
listModules(Lib)
listModules(Cache)
listModules(Autorisasjon)

currentFolder = dirname(__file__)
for c in os.listdir(currentFolder):
    if os.path.isdir(os.path.join(currentFolder, c)) and "__" not in c:
        print(c)
