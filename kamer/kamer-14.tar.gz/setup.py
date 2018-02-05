#!/usr/bin/env python3
#
#

import os
import sys
import os.path

def j(*args):
    if not args: return
    todo = list(map(str, filter(None, args)))
    return os.path.join(*todo)

if sys.version_info.major < 3:
    print("you need to run kamer with python3")
    os._exit(1)

try:
    use_setuptools()
except:
    pass

try:
    from setuptools import setup
except Exception as ex:
    print(str(ex))
    os._exit(1)

target = "kamer"
upload = []

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir):
        print("%s does not exist" % dir)
        os._exit(1)
    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if not os.path.isdir(d):
            if file.endswith(".pyc") or file.startswith("__pycache"):
                continue
            upl.append(d)
    return upl

def uploadlist(dir):
    upl = []

    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if os.path.isdir(d):   
            upl.extend(uploadlist(d))
        else:
            if file.endswith(".pyc") or file.startswith("__pycache"):
                continue
            upl.append(d)

    return upl

setup(
    name='kamer',
    version='14',
    url='https://bitbucket.org/bthate/kamer',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description=""" Straffeloosheid verzekerende kamerleden de cel in !! """,
    license='MIT',
    zip_safe=False,
    scripts=["bin/kamer",],
    install_requires=["botlib"],
    packages=['kamer',
             ],
    long_description = """ 
    Geachte heer <Eerste kamer lid>,

ik wil u graag informeren dat uw commissies van VWS en J&V geinformeerd zijn dat de medcijnen gebruikt in de gedwongen zorg waar uw wet een wettelijk voorschrift voor gaat bieden gif blijken te zijn.

Er is bewijs dat de medcijnen gebruikt in de GGZ gif zijn, bewijs dat geleverd word door het ECHA agentschap van de Europeese Unie, wat bij houd welke chemicalien een gevaar zijn of niet. De ECHA laat bedrijven die stoffen willen transporteren testen doen wat hun dodelijkheid betreft, de zogenoemde LD-50 tests. Aan de hand van deze tests beoordeelt men dan of een stof onschadelijk, schadelijk, gif of dodelijk zijn. Deze tests resulteren in labels die men moet gebruiken als men de stof transporteert.


Voor de stof haloperiodol, de werkzame stof in Haldol, ziet u hier de waarschuwingen die te vinden zijn op https://echa.europa.eu/substance-information/-/substanceinfo/100.000.142

Haldol is het meest gebruikt medicijn als "nood medicatie" in de GGZ, een klassiek antipsychoticum.


bewijs dat haldol gif is:

.. image:: jpg/ECHAhaloperidol.png
    :width: 100%

Zoals u ziet is haloperidol geclassificeerd als "toxic as swallowed" en is een doodskop met beenderen noodzakelijk als men deze stof wil vervoeren.

Men gebruikt in de GGZ dus geen medicijnen die geen schade kunnen, maar een stof die giftig is als men hem inneemt.

De medicatie die u in uw wet toestaat om gedwongen toegedient te kunnen worden zijn gif en niet zoals men beweerd een medicijn dat geen schade kan.

Deze wet aannemen in de wetenschap dat het hier gif betreft maakt dat uw wettelijke voorschrift gebruikt word voor giftoedieningen en niet voor behandeling met medicijnen die geen schade kunnen.

U zekert hier de straffeloosheid voor deze gif toedieningen als u niet ook zorgt dat de medicatie waar uw wet aan refereert ook niet daadwerkelijk medicijnen zijn die geen schade kunnen.

Ik hoop dat u de wetenschap dat het hier gif betreft en niet medicatie zult gebruiken om de WvGGZ niet aan te nemen, hij word nu gebruikt in een poging gif toedieningen te legaliseren, te voorzien van een wettelijk voorschrift.


Hoogachtend,


Bart Thate


p.s. de commissies VWS en J&V van uw kamer zijn ook geinformeerd maar uw persoonlijk ook op de hoogte brengen voordat men hier over stemt verdient de voorkeur.


                       """, 
   data_files=[("docs", ["docs/conf.py","docs/index.rst"]),
               (j('docs', 'jpg'), uploadlist(os.path.join("docs","jpg"))),
               (j('docs', 'txt'), uploadlist(os.path.join("docs", "txt"))),
               (j('docs', '_templates'), uploadlist(os.path.join("docs", "_templates")))
              ],
   package_data={'': ["*.crt"],
                 },
   classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
)
