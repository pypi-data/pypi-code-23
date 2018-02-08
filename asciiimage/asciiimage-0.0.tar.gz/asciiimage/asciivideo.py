import time
from .asciiimage import ASCIIImage

class Frame:
	""" A Frame with a picture and a time """
	def __init__(self,content,time):
		""" Create a new Frame with content at time. """
		self.content = content
		self.time = time

class ASCIIVideo:
	""" An ASCII art video
	
	    It contains a series of ASCII-art Frames,
	    each with different time.
	"""
	def __init__(Frames=None):
		""" Create a new video with Frames. """
		if Frames == None:
			Frames = [Frame(ASCIIImage('\n'),0)]
		self._Frames = Frames # don't mess with this, sue addFrame

	def minx(self):
		""" Return the minimum x value of any Frame. """
		return min([Frame.content.minx() for Frame in self._Frames])

	def maxx(self):
		""" Return the maximum x value of any Frame. """
		return max([Frame.content.maxx() for Frame in self._Frames])

	def miny(self):
		""" Return the minimum y value of any Frame. """
		return min([Frame.content.miny() for Frame in self._Frames])

	def maxy(self):
		""" Return the maximum y value of any Frame. """
		return max([Frame.content.maxy() for Frame in self._Frames])

	def addFrame(self,actuaFrame):
		""" Add a new Frame to the video. """
		self._Frames.append(actuaFrame)
		if actuaFrame.time < self._Frames[-2].time:
			def time(actuaFrame):
				return actuaFrame.time
			self._Frames.sort(key=time)

	def compile(self,bounds=None):
		""" Return string of video in readable format. """
		if bounds == None:
			bounds=[self.minx(), self.maxx(), self.miny(), self.maxy()]

		data = "{:03d}y{:06d}".format(bounds[3]-bounds[1],len(self._Frames)-1)
		for i in range(len(self._Frames)-1):
			actuaFrame = self._Frames[i]
			nextFrame  = self._Frames[i+1]

			delay = nextFrame.time-actuaFrame.time
			if bounds==None:
				data += str(actuaFrame.content) + str(delay)+"\n"
			else:
				data += str(actuaFrame.content.setBounds(*bounds)) + str(delay)+"\n"
		return data
	
	def export(self,filepath,bounds=None):
		""" Write video to file. """
		f = open(filepath,'w')
		f.write(self.compile(bounds))
		f.close()
	
	def play(self,bounds=None):
		""" Play the video to stdout. """
		if bounds == None:
			bounds = [self.minx(),self.miny(),self.maxx(),self.maxx()]
		
		for i in range(len(self._Frames)-1):
			actuaFrame = self._Frames[i]
			nextFrame  = self._Frames[i+1]

			delay = nextFrame.time-actuaFrame.time
			print('\n'*30)
			print(actuaFrame.content.setBounds(*bounds))
			time.sleep(delay)
	
	def at(self,time):
		""" Return the Frame that would be showing at time time. """
		for Frame in self._Frames:
			if Frame.time >= time:
				return Frame
	
	def downsample(self,delay):
		""" Remove extra Frames from the video.

		    There will be a Frame every delay seconds after.
		"""
		output = ASCIIVideo()
		t=0
		for i in range(len(self._Frames)-1):
			if self._Frames[i].time > t:
				output.addFrame(Frame(self._Frames[i].content,t))
				t+=delay
		return output
