from .graphCoreFunctions import createAdjList

def BFS(graph,s,Print=False):
	adj = createAdjList(graph)

	queue = []
	visited = [False]*(graph.getLen())

	queue.append(s)
	visited[s] = True


	if Print == True:
		print("The result of BFS is :",end=" ")

	while queue:
		s = queue.pop(0)
		if Print == True:
			print(s,end=" ")
		for i in range(len(adj)):
			if visited[i] == False:
				queue.append(i)
				visited[i] = True

	if Print == True:
		print(end='\n')
	else:
		return queue
