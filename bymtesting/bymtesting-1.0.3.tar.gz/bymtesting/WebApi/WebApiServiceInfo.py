
class WebApiServiceInfo:

    webapiServiceId = "cd995ee7-0d05-452f-9b36-99d5668be594"
    webapiServiceName = "WebApi"
    webapiAdminId = '13dd529a-ffa6-4d0e-962f-7463034e8fb4'
    webapiAdminNavn = 'WebApiAdmin'
    webapiAdminEpost = "webapiadmin@bym.no"

    def getRolleByNavnMap(self):
        rolleMap = {}
        rolleMap[self.webapiAdminNavn] = self.webapiAdminId
        return rolleMap

    def GetUsergivenRolle(self, rolle):
        if(rolle == self.webapiAdminNavn):
            return self.webapiAdminEpost
