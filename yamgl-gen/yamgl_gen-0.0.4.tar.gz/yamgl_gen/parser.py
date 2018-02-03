# -*- coding: utf-8 -*-

""" Parser for the ui file """

#Used modules
import os
import logging

#########################################################################################
class yamglParser:
	"""
	Handles parsing for different elements inside the ui file
	"""

#---------------------------------------------------------------------------------------#	
	def __init__(self, tree):
		"""
		Contructor
		"""
		self.tree = tree

		logging.info("ui file version: %s" % self.tree.get("version"))

		logging.debug("working in directory: %s" % os.getcwd())

#---------------------------------------------------------------------------------------#
	def get_images(self):
		"""
		Return a list of images as:
		{"name" : img_name, "path" : rel_path}
		"""
		imgs = []

		#Iterate over all images
		for img in self.tree.xpath("//images/image"):
			data = {"name" : img.get("name")}
			data["path"] = img.xpath("file_path/text()")[0]
			imgs.append(data)

		return imgs

#---------------------------------------------------------------------------------------#
	def get_fonts(self):
		"""
		Return a list of fonts as:
		{"name" : fnt_name, "path" : rel_path, "size" : point_sz, "maps" : [{"from" : from , "to" : to}, {"from" : from , "to" : to}, ...]}
		"""
		fonts = []

		for font in self.tree.xpath("//fonts/font"):
			data = {"name" : font.get("name")}
			data["path"] = font.xpath("file_path/text()")[0]
			data["size"] = int(font.xpath("point_size/text()")[0])
			data["maps"] = [{"from" : int(chmap.xpath("from/text()")[0]) , 
							"to" : int(chmap.xpath("to/text()")[0])} 
								for chmap in font.xpath("char_maps/char_map")]

			fonts.append(data)

		return fonts