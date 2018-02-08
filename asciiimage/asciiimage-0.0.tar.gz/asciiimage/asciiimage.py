from . import manipulate as man

class ASCIIImage:
	""" An ASCII-art image

	    Contains a rectangular text (the image)
	    and an 'origin' which is used to position the object
	    (when overlaying two objects for example).
	"""
	
	def __init__(self, content,origin = [0,0]):
		""" Create an image """
		self.origin = origin
		self.content = man.complete(content)

	def __str__(self):
		return self.content

	def c(self):
		""" Return the image as an ASCIIImage """
		return self

#	def complete(self):    #TODO: remove?
#		return ASCIIImage(man.complete(str(self),self.origin))

	def getWidth(self):
		""" Return the width of the image, including whitespace. """
		return str(self).index("\n")

	def getLength(self):
		""" Return the length of the image, including whitespace. """
		return str(self).count("\n")

	def minx(self):
		""" Return the position of the horizontal beginning of the image. """
		return -self.origin[0]

	def maxx(self):
		""" Return the position of the horizontal end of the image. """
		return self.getWidth()-self.origin[0]

	def miny(self):
		""" Return the position of the vertical beginning of the image. """
		return -self.origin[1]

	def maxy(self):
		""" Return the position of the vertical end of the image. """
		return self.getLength()-self.origin[1]

	def expandBounds(self,minx,miny,maxx,maxy):
		""" Pad image with whitespace to set its new size. """
		image = str(self)
		minxi = -self.origin[0]
		minyi = -self.origin[1]
		maxxi = minxi+self.getWidth()
		maxyi = minyi+self.getLength()
		
		dminx = minx-minxi
		dminy = miny-minyi
		dmaxx = maxx-maxxi
		dmaxy = maxy-maxyi

		if dminx < 0: prex = -dminx
		else: prex = 0
		if dminy < 0: prey = -dminy
		else: prey = 0
		if dmaxx > 0: postx = dmaxx
		else: postx = 0
		if dmaxy > 0: posty = dmaxy
		else: posty = 0
		
		imagelecian = image.splitlines()
		nuvoimagelecian = [(prex+self.getWidth()+postx)*" "]*prey
		nuvoimagelecian.extend([prex*" "+
			imagelecian_item+
			postx*" " 
			for imagelecian_item in imagelecian])
		nuvoimagelecian.extend([(prex+self.getWidth()+postx)*" "]*posty)
		return ASCIIImage('\n'.join(nuvoimagelecian),[self.origin[0]+prex,self.origin[1]+prey])

	def mirror(self):
		""" Mirror image over the x axis. """
		image = str(self)
		mirrorimage = man.mirror(image)
		return ASCIIImage(image,
			[self.getWidth()-self.origin[0],
			self.getLength()-self.origin[1]])

	def overlay(self,overlaid,x,y):
		r""" Return a new image with overlaid put on top of the image.

		     (x,y) is the position of the origin of overlaid
		     in relation to the origin of the original image.
		"""
		nuvoimage = self.expandBounds(
			x-overlaid.origin[0],
			y-overlaid.origin[1],
			x-overlaid.origin[0]+overlaid.getWidth(),
			y-overlaid.origin[1]+overlaid.getLength()
		)
		offsetx = x + nuvoimage.origin[0] - overlaid.origin[0]
		offsety = y + nuvoimage.origin[1] - overlaid.origin[1]

		return ASCIIImage(
			man.overlay(
				str(nuvoimage),str(overlaid),
				offsetx,offsety
			),
			nuvoimage.origin
		)

	def cropx(self,minx,maxx):
		""" Crop image down to columns minx to maxx. """
		image = str(self)
		x = self.origin[0]
		image=man.cropx(image,minx+x,maxx+x)

		return ASCIIImage(image,[x-minx,self.origin[1]])

	def cropy(self,miny,maxy):
		""" Crop image down to rows miny to maxy. """
		image = str(self)
		y = self.origin[1]
		image=man.cropy(image,miny+y,maxy+y)

		return ASCIIImage(image,[self.origin[0],y-miny])

	def crop(self,minx,miny,maxx,maxy):
		""" Crop image to a rectangle.

		     This will only leave the intersection of
		     rows minx to maxx and columns miny to maxy.
		"""
		image = self.cropy(miny,maxy)
		return image.cropx(minx,maxx)
	
	def setBounds(self,minx,miny,maxx,maxy):
		""" Set the new bounds of the image. 

		    Crop image if necessary,
		    but also pad with whitespace if necessary.
		"""
		image = self.expandBounds(minx,miny,maxx,maxy)
		image = image.crop(minx,miny,maxx,maxy)
		return image

	def fill(self,minx,miny,maxx,maxy,char):
		""" Fill rectangle with char. """
		if isinstance(char,ASCIIImage):
			char=char.content[0]
		image = self.expandBounds(minx,miny,maxx,maxy)
		origin = image.origin

		minx = minx+origin[0]
		maxx = maxx+origin[0]
		miny = miny+origin[1]
		maxy = maxy+origin[1]

		image = str(image).splitlines()
		nuvoimage = image[:miny]
		for line in image[miny:maxy]:
			nuvoimage.append(line[:minx]+char*(maxx-minx)+line[maxx:])
		return ASCIIImage('\n'.join(nuvoimage+image[maxy:]+['']),origin)
