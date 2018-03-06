def plol (lista):
	for each in lista:
		if isinstance (each, list):
			plol(each)
		else:
			print(each)
