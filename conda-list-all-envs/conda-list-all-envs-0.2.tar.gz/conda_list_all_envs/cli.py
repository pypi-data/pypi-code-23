import subprocess,json

def cli():
	myJSON = subprocess.check_output(["conda", "env", "list", "--json"])
	
	myDict = json.loads(myJSON)

	myPaths = myDict['envs']

	for i in myPaths:
		print (subprocess.check_output(['conda', 'list', '-p', i]).decode("utf-8"))
		print ("")

if __name__=="__main__":
	cli()

