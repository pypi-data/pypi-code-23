import requests
import json

from collabme import validations as vdme

def GetAPI(hostname, port, projectname, versionnumber, classification, test, source):
    if vdme.alph(projectname) and vdme.version(versionnumber) and vdme.alph(classification) and vdme.alph(test) and vdme.alph(source):
	data={}
	data['project']=projectname
	data['version']=versionnumber
	data['classification']=classification
	data['test']=test
	data['source']=source
	url='http://'+str(hostname)+':'+str(port)+'/genapi'
	api=requests.post(str(url) ,json=data)
	return api.json()['api']




def WriteData(hostname, port, api,dat):
    if type(dat) == dict:
        headers={'Custom-API':api}
	url='http://'+str(hostname)+':'+str(port)+'/storeme'
	data=requests.post(url ,json=dat, headers=headers)
        return data




