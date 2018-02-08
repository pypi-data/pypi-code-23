from .asciiimage import ASCIIImage

class Component:
	""" This holds the information about a single Component in a Sprite.

	    It contains a value which will be used to render the Sprite,
	    a name to identify it in the Sprite,
	    and the location within the Sprite to render this Component.
	    The location refers to the position of the Component's origin
	    relative to the Sprite's origin.
	    If location is None, the Component is not rendered.
	"""
	def __init__(self,content,name,location=None):
		""" Create a new Component. """
		self.value = content
		self.name = name
		self.location = location
	def __str__(self):
		""" Return a string telling you all the details. """
		return ('{}@{}:{}'.format(
			self.name,
			self.location,
			repr(self.value)
		) )
	def copy(self):
		""" Return a copy of the Component. """
		return Component(
			self.value.copy(),
			self.name,
			self.location
		)
class Sprite:
	""" A hierarchical composition of images

	    Each Sprite consists of a set of images and other Sprites.
	    When rendered, the various components are rendered,
	    and then they are layered on top of each other.
	    The state of a Sprite consists of each Component
	    (which has a image and a location)
	    and the order in which they will be rendered.
	"""
	def __init__(self,path=None,components=None):
		""" Create a new Sprite from path or from components.
		
		    Component Initialization:
		    The components list is simply copied to the list of components

		    Path Initialization:
		    __init__ looks at path/list for a list of files to include as components.
		    Files have rows, each in one of the the following formats:

		    Sprite	<name>(	<X>	<Y>)
		    ASCIIImage	<name>	<x>	<y>	<space>	<alpha>(	<X>	<Y>)

		    For including sub-Sprites:
		    <name> is the relative path of the director containing the sub-Sprite's file data.

		    For ASCIIImages:
		    <name> is the relative path of the file containing the ASCIII art,
		    (<x>,<y>) is the position of the origin relative to the top right corner of the text.
		    <space> is a character that will be replaced with non-breaking spaces when importing the image.

		    For both:
		    (<X>,<Y>) is the position of the Component within the Sprite.
		    It is optional, and defaults to None.
		"""
		if components == None: self.components = []
		else: self.components = components

		if path != None:
			self._be(path)

	def __str__(self):
		""" Return what's shown when it's rendered. """
		return str(self.c())
	
	def __len__(self):
		""" Return the length of the components to allow easy iteration through them. """
		return len(self.components)
	
	def __getitem__(self,key):
		""" Return the Component with specified index or name.

		    If a string is given, return the Component with that name.
		    If an integer is given, retutrn the Component at that index in the list.
		    Lower numbers correspond to components rendered below others.
		"""
		if type(key) == int:
			return self.components[key]
		elif type(key) == str:
			return self.components[self.getIndex(key)]
		elif type(key) == slice:
			indexes = key.indices(len(self.components))
			i=indexes[0]
			output = []
			while i > indexes[1]:
				output.append(self[i])
				i+=indexes[2]
			return output
		elif type(key) == list:
			if key == []:
				return self
			return self[key[0]][0][key[1:]]

	def __setitem__(self,key,value):
		""" Replace the Component at key witht value. """
		if type(key) == int:
			self.components[key] = value
		elif type(key) == str:
			self.components[self.getIndex(key)] = value
		elif type(key) == slice:
			indexes = key.indices(len(self.components))
			i=indexes[0]
			while i > indexes[1]:
				self[i]=value[i]
				i+=indexes[2]
		elif type(key) == list:
			if len(key) == 1:
				self[key[0]] = value
			else:
				self[key[0]][key[1:]]=value

	def __delitem__(self,key):
		""" Remove Component with key. """
		if type(key) == int:
			del self.components[key]
		elif type(key) == str:
			del self.components[self.getIndex(key)]
		elif type(key) == slice:
			indexes = key.indices(len(self.components))
			i=indexes[0]
			while i > indexes[1]:
				del self[i]
				i+=indexes[2]
		elif type(key) == list:
			if len(key) ==1:
				del self[key[0]]
			else:
				del self[key[0]][0][key[1:]]

	def c(self):
		""" Return object as ASCIIImage.

		    The image is composed of all the components stacked.
		    This serves to implement a one-function 'interface' also implemented by ASCIIImage.
		"""
		#TODO: make an  actutal abstract class to show this.
		#TODO:change name
		output = ASCIIImage('\n')
		for Component in self:
			if Component.name!= None:
				output = output.overlay(
					Component.value.c(),
					*Component.location
				)

		return output
	
	def copy(self):
		""" Return a copy Sprite. """
		copied = Sprite()
		for component in self:
			if type(component.value) == ASCIIImage:
				copied.add(component)
			else:
				copied.add(component.copy())
		return copied

	def _be(self, path):
		""" Set the sprite to be the same as that contained in path. """
		f = open(path+"/list",'r')
		filelecian = f.read().splitlines()
		f.close()
		for filelecian_item in filelecian:
			plecian = filelecian_item.split('\t')
			kind = plecian[0]
			name = plecian[1]
			location = None
			if kind == 'asciiimage':
				x = int(plecian[2])
				y = int(plecian[3])
				spacechar = plecian[4]
				alphachar = plecian[5]

				addfile = open(path+'/'+name,'r')
				image = addfile.read()
				addfile.close()
		
				if spacechar != '':
					image = image.translate(''.maketrans(spacechar,'\u00A0'))
				if alphachar != '':
					image = image.translate(''.maketrans(alphachar,' '))
				content = ASCIIImage(image,[x,y])

				if len(plecian) == 8:
					X = int(plecian[6])
					Y = int(plecian[7])
					location = [X,Y]
			elif kind == 'sprite':
				content = Sprite(path+'/'+name)
				if len(plecian) == 4:
					X = int(plecian[2])
					Y = int(plecian[3])
					location=[X,Y]
			self.add(Component(content,name,location))

	def getIndex(self,name):
		""" Return the z-index of the Component with name. """
		return next(i for i in range(len(self)) if self[i].name == name)
	
	def active(self):
		""" Return the first Component that will be rendered. """
		return next(component for component in self if component.location != None)

	def add(self,actualComponent,index=None):
		""" Add actualComponent to the Component list at index.
		
		    If index is None, add it to the top.
		"""
		if index == None:
			self.components.append(actualComponent)
		else:
			self.components.insert( index, actuaComponent )

	def put(self,name,location):
		""" Set the location of Component name. """
		self[name].location = location

	def setIndex(self,name,index):
		""" Change the z-index of the Component with name to index. """
		components = self.components
		components.insert(index, components.pop(self.getIndex(name)))
	
	def replace(self,old,new,position=None):
		""" Replace the old Component with new Component.

		    If a position is supplied,
		    the new Component will be put at position,
		    otherwise it will go to the old Component's previous location.
		"""
		if position == None:
			position = self[old].location
		self[old].location = None
		self[new].location = position
	
	def setState(self,state,position=None):
		""" Replace the first active Component with Component named state. """
		self.replace(self.active(),state,position)
