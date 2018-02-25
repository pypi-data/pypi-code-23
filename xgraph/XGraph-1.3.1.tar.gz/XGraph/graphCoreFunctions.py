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


def getNeigh(graph,node):
	neigh = []
	for v in graph:
		if node == v.getNode():
			for w in v.getConnectedNodes():
				wid = w.getNode()
				neigh.append(wid)

	return neigh
