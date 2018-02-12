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

class UndirectedGraph:
	def __init__(self):
		self.nodes = {}
		self.numOfNodes = 0

	def __iter__(self):
		return iter(self.nodes.values())

	def addNode(self,node):
		self.numOfNodes += 1
		newNode = Node(node)
		self.nodes[node] = newNode
		return newNode


	def addEdge(self,node,toNode,weight=0):
		if node not in self.nodes:
			self.addNode(node)
		if toNode not in self.nodes:
			self.addNode(toNode)

		self.nodes[node].addNeigh(self.nodes[toNode],weight)
		self.nodes[toNode].addNeigh(self.nodes[node],weight)

	def getNodes(self):
		return self.nodes.keys()

	def getLen(self):
		return self.numOfNodes


def createNodes(graph,namelist):
	for node in namelist:
		graph.addNode(node)

def printGraph(graph):
	# That is possible due to __iter__ function
	for v in graph:
		for w in v.getConnectedNodes():
			vid = v.getNode()
			wid = w.getNode()
			print('(%s,%s,%3d)'%(vid,wid,v.getWeight(w)))

def createAdjList(graph):
	adjList = {}
	for v in graph:
		for w in v.getConnectedNodes():
			vid = v.getNode()
			wid = w.getNode()
			adjList[vid] = wid
			adjList[wid] = vid

	return adjList
