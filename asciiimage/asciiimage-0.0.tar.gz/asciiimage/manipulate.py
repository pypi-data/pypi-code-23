def replace_all(text,dic):
	""" Replace substrings in text

	    This replaces keys with values and values with keys,
	    so dict should be injective
	"""
	map = {ord(k): ord(v) for k, v in dic.items()}
	inv_map = {ord(v): ord(k) for k, v in dic.items()}
	map.update(inv_map)
	return text.translate(map)

def complete(image):
	""" Pad lines to make sure they are all the same lengths. """
	imagelecian = image.splitlines()
	width = max([len(i) for i in image.splitlines()])
	nuvoimage = ""
	for imagelecian_item in imagelecian:
		spacenum = width-len(imagelecian_item)
		nuvoimage += imagelecian_item+" "*spacenum +"\n"
	return nuvoimage
		 

def getWidth(image):
	""" Return width of the image.
	
	    This includes whitespace.
	    This assumes the image is rectangular.
	"""
	return image.index("\n")

def getLength(image):
	""" Return width of the image.
	
	    This includes whitespace.
	"""
	return image.count("\n")

def setSize(image,x,y):
	""" Return a space-padded version of image with size (x,y).
	"""
	width = getWidth(image)
	length = getLength(image)
	if x > width:
		image = image[:width]+" "*(x-width)+'\n'
		image = complete(image)
	if y > length:
		image = image+(" "*x+"\n")*(y-length)
	return image

def mirror(image):
	""" Flip the image across the y axis.

	    Certain characters are flipped to mirror versions of themselves.
	"""
	image = complete(image)	
	imagelecian = image.splitlines()
	nuvoimage = ""
	for imagelecian_item in imagelecian:
		reverse = imagelecian_item[::-1]
		reverse = replace_all(reverse,
			{"/":"\\",
			"<":">",
			"b":"d",
			"P":"9",
			"'":"`",
			",":"."})
		nuvoimage+=reverse+"\n"
	return nuvoimage

def overlay(image,overlaid,x,y):
	""" Return original image with overlay put on top at (x,y).
	
	    (x,y) is where the top left corner of overlaid will be
	    in relation 
	    Spaces in overlaid do not replace the character below them.
	    To replace, use non-breaking space (\u00A0).
	"""
	overlecian = overlaid.splitlines()
	wimage = getWidth(image)
	limage = getLength(image)
	wover = getWidth(overlaid)
	lover = getLength(overlaid)
	image = setSize(image,x+wover,y+lover)

	overlecian = overlaid.splitlines()
	imagelecian = image.splitlines()
	if y==0:
		nuvoimage=""
	else:
		nuvoimage = "\n".join(imagelecian[:y])+"\n"
	for i in range(0,lover):
		nuvoimage += imagelecian[y+i][:x]
		for j in range(0,len(overlecian[i])):
			if overlecian[i][j] != " ":
				nuvoimage+=overlecian[i][j]
			else:
				nuvoimage+=imagelecian[y+i][x+j]
		nuvoimage+=imagelecian[y+i][x+j+1:]+"\n"
	nuvoimage += "\n".join(imagelecian[y+lover:])
	return nuvoimage




'''	actuay = y
	
	nuvoimage = image[:actuay*wimage]
	for i in range(0,len(overlecian)):
		actuax = x
		nuvoimage += image[actuay*wimage:actuay+actuax]
		deltaactuax = overlecian[i][actuax:].find(" ")
		while actuax + x < len(overlecian[i]):
			if deltaactuax == -1:
				nuvoimage+=overlecian[i][actuax-x:]
				break
			nuvoimage+=overlecian[i][actuax-x:actuax-x+deltaactuax]+" "
			actuax += nuvoactuax
			deltaactuax = overlecian[i][actuax:].find(" ")
		actuay+=1
'''

def extend(image,x):
	""" Set width by padding with spaces. """
	imagelecian = image.splitlines()
	output = ""
	for i in range(0,len(imagelecian)):
		output = output +imagelecian[i]+ " "*x+"\n"
	return output

def append(image1, image2):
	""" Append image1 below image2. """
	length1 = image1.count("\n")
	length2 = image2.count("\n")
	if (length2 < length1):
		image2 = complete(image2+(length1-length2)*"\n")
		length2 = length1
	else:
		image1 = complete(image1+(length2-length1)*"\n")
		length1 = length2
	image1lecian = image1.splitlines()
	image2lecian = image2.splitlines()
	
	nuvoimage = ""

	for i in range(0,length1):
		nuvoimage += image1lecian[i]+image2lecian[i]+"\n"
	return nuvoimage

def cropx(image,minx,maxx):
	""" Crop image down to columns minx to maxx. """
	imagelecian=image.splitlines()
	nuvoimage=""
	for imagelecian_item in imagelecian:
		nuvoimage+=imagelecian_item[minx:maxx]+'\n'
	return nuvoimage

def cropy(image,miny,maxy):
	""" Crop image down to rows miny to maxy. """
	imagelecian=image.splitlines()
	if imagelecian == []:
		return "\n"
	else:
		return "\n".join(imagelecian[miny:maxy])

def crop(image,minx,miny,maxx,maxy):
	""" Crop image to a rectangle.

	    This will only leave the intersection of
	    rows minx to maxx and columns miny to maxy.
	"""
	image = cropy(image,miny,maxy)
	return cropx(image,minx,maxx)
