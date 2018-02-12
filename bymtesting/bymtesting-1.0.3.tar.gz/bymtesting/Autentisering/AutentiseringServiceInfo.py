from bymtesting.Lib.JsonBase import *


class ServiceRolle(JsonBase):

    def __init__(self, navn, prosessrolleId):
        self.navn = navn
        self.prosessrolleId = prosessrolleId


class AutentiseringServiceInfo():
    ServiceId = '1AEFFC5D-9D3E-4DB9-AEAD-525A33660B9C'
    AutentiseringAdmin = ServiceRolle(
        "AutentiseringAdmin", "D3CA222C-103C-44CE-9A96-D0745C6C545A")
    ServiceBruker = ServiceRolle(
        "ServiceBruker", "A5E8030F-268E-4C28-83F9-97205BA36D46")
    ServiceBrukerAdmin = ServiceRolle(
        "ServiceBrukerAdmin", "009BA9A2-F9E6-4320-B7DE-34672EDAA33B")
