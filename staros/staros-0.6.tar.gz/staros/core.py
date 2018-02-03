from connection import _getsshdata
import connection
import outputparsing


class StarClient:
    def __init__(self, username, password, host, port):
        self.username = username
        self.password = password
        self.host = host
        self.port = port

    def getsubscrmsisdn(self, msisdn):
        data = connection._getsshdata3(self.host, self.port, self.username, self.password, "show subscribers msisdn " + msisdn+"\n")
        return outputparsing._getsubscribermsisdn(str(data))

    def getsubssessionmain(self):
        data = connection._getsshdata1(self.host, self.port, self.username, self.password, "show subscribers summary\n")
        return outputparsing._parseshowsess(str(data))

    def getsubsfullimsi(self,imsi):
        data = _getsshdata(self.host, self.port, self.username, self.password, "show subscribers msisdn " + imsi + "\n")

    def getEnodebAssociatNum(self):
        data = connection._getsshdata2(self.host, self.port, self.username, self.password, "show mme-service enodeb-association summary\n")
        return outputparsing._parseEnodebAssoc(str(data))

    def clearSubsMsisdn(self, msisdn):
        data = connection._getsshdata1(self.host, self.port, self.username, self.password, "clear subscribers msisdn "+msisdn+" -noconfirm\n")
        return outputparsing._parseClearSubsc(str(data))

    def clearSubsImsi(self, imsi):
        data = connection._getsshdata1(self.host, self.port, self.username, self.password, "clear subscribers imsi "+imsi+" -noconfirm\n")
        return outputparsing._parseClearSubsc(str(data))