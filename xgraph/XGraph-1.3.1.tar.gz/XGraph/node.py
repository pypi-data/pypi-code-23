class Node:
	def __init__(self,node_name):
		self.name = node_name
		self.adjNodes = {}

	def addNeigh(self,neig,weight=0):
		self.adjNodes[neig] = weight

	def getConnectedNodes(self):
		return self.adjNodes.keys()

	def getNode(self):
		return self.name

	def getWeight(self,neig):
		return self.adjNodes[neig]