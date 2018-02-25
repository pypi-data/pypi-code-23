from .node import Node

class undirectedGraph:
	def __init__(self):
		self.nodes = {}
		self.numOfNodes = 0

	def __iter__(self):
		return iter(self.nodes.values())

	def __addNode(self,node):
		self.numOfNodes += 1
		newNode = Node(node)
		self.nodes[node] = newNode
		return newNode


	def addEdge(self,node,toNode,weight=0):
		if node not in self.nodes:
			self.__addNode(node)
		if toNode not in self.nodes:
			self.__addNode(toNode)

		self.nodes[node].addNeigh(self.nodes[toNode],weight)
		self.nodes[toNode].addNeigh(self.nodes[node],weight)

	def getNodes(self):
		return self.nodes.keys()

	def getLen(self):
		return self.numOfNodes

	def __subCycle(self,node,visited,parent):
		visited[node] = True

		for n in self.nodes[node].getConnectedNodes():
			if visited[n.getNode()] == False:
				if self.__subCycle(n.getNode(),visited,node):
					return True
			elif parent != n.getNode():
				return True

		return False

	def isCycle(self):
		visited = [False]*(self.getLen())
		for node in self.getNodes():
			if visited[node] == False:
				if self.__subCycle(node,visited,-1) == True:
					return True

		return False

