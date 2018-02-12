from .graphCore import createAdjList

def BFS(graph,s):
	adj = createAdjList(graph)
	print(adj)

	queue = []
	visited = [False]*(graph.getLen())

	queue.append(s)
	visited[s] = True

	print("The result of BFS is :",end=" ")

	while queue:
		s = queue.pop(0)
		print(s,end=" ")
		for i in adj:
			if visited[i] == False:
				queue.append(i)
				visited[i] = True
