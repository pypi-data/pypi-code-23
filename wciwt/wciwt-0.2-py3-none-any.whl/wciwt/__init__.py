#!/usr/bin/env python
import requests, json, sys

def wciwt():

	query = '+'.join(sys.argv[1:]).replace(" ", "+")
	if len(sys.argv) == 1:
		print ('Usage: wciwt "movie or show title"')
		return (1)

	try:
		json = (requests.get("https://wciwt.in/api/?format=json&query=" + query))
		if (json.status_code) != 200:
			print ("Error in request.")
			return (1)
	except:
		print("Error during requesting, try again after sometime.")
		return (1)

	json = json.json()

	if not (json['total_results']):
		print ("No such title in our database.")
	else:
		for service in json['results']:
			if (json['results'][service]):
				print ("\n{}:\n{}\n".format(service.upper(), '\n'.join(str(x.encode('utf-8')) for x in json['results'][service])))
	return (0)

if __name__ == "__main__":
	wciwt()