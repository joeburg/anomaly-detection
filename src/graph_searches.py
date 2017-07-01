from collections import defaultdict
import heapq
import sys


#-----------------------------------------------------------------------------------#
# http://eddmann.com/posts/depth-first-search-and-breadth-first-search-in-python/

def bfs_paths(graph, start, goal):
	queue = [(start, [start])]
	while queue:
		(vertex, path) = queue.pop(0)
		for next in graph[vertex] - set(path):
			if next == goal:
				yield path + [next]
			else:
				queue.append((next, path + [next]))

def shortest_path(graph, start, goal):
	try:
		return next(bfs_paths(graph, start, goal))
	except StopIteration:
		return None

graph = {'A': set(['B', 'C']),
		 'B': set(['A', 'D', 'E']),
		 'C': set(['A', 'F']),
		 'D': set(['B']),
		 'E': set(['B', 'F']),
		 'F': set(['C', 'E'])}

# this approach can 
network = {}
for node1 in graph:
	for node2 in graph:
		path = shortest_path(graph, node1, node2)
		if path and len(path)-1 <= 1:

			# print '%s <-> %s = %d' %(node1, node2, len(path)-1)
			# print 'path: %s\n\n' %path 

			if node1 in network:
				network[node1].update(path)
			else:
				network[node1] = set(path)

print network 

# '''
# # sort values 
# sorted_x = sorted(x.items(), key=operator.itemgetter(1))
# # sort keys 
# sorted_x = sorted(x.items(), key=operator.itemgetter(0))

# # sort by key and return list of corresponding values 
# [value for (key, value) in sorted(data.items())]

# '''

#-----------------------------------------------------------------------------------#
# http://code.activestate.com/recipes/577876-printing-breadth-first-levels-of-a-graph-or-tree/

def printBfsLevels(graph,start):
	queue=[start]
	path=[]
	currLevel=1
	levelMembers=1
	height=[(0,start)]
	childCount=0
	print queue
	while queue:
		visNode=queue.pop(0)
		if visNode not in path:
			if  levelMembers==0:
				levelMembers=childCount
				childCount=0
				currLevel=currLevel+1
			queue=queue+graph.get(visNode,[])
			if levelMembers > 0:
				levelMembers=levelMembers-1
				for node in graph.get(visNode,[]):
					childCount=childCount+1
					height.append((currLevel,node))
			path=path+[visNode]

	prevLevel=None
	
	for v,k in sorted(height):
		if prevLevel!=v:
			if prevLevel!=None:
				print "\n"
		prevLevel=v
		print k,
	return height

#-----------------------------------------------------------------------------------#

class Graph:
	
	def __init__(self):
		self.vertices = {}
		
	def add_vertex(self, name, edges):
		self.vertices[name] = edges

	# http://www.maxburstein.com/blog/introduction-to-graph-theory-finding-shortest-path/
	
	def shortest_path(self, start, finish):
		distances = {} # Distance from start to node
		previous = {}  # Previous node in optimal path from source
		nodes = [] # Priority queue of all nodes in Graph
 
		for vertex in self.vertices:
			if vertex == start: # Set root node as distance of 0
				distances[vertex] = 0
				heapq.heappush(nodes, [0, vertex])
			else:
				distances[vertex] = sys.maxint
				heapq.heappush(nodes, [sys.maxint, vertex])
			previous[vertex] = None
		
		while nodes:
			smallest = heapq.heappop(nodes)[1] # Vertex in nodes with smallest distance in distances
			if smallest == finish: # If the closest node is our target we're done so print the path
				path = []
				while previous[smallest]: # Traverse through nodes til we reach the root which is 0
					path.append(smallest)
					smallest = previous[smallest]
				return path
			if distances[smallest] == sys.maxint: # All remaining vertices are inaccessible from source
				break
			
			for neighbor in self.vertices[smallest]: # Look at all the nodes that this vertex is attached to
				alt = distances[smallest] + self.vertices[smallest][neighbor] # Alternative path distance
				if alt < distances[neighbor]: # If there is a new shortest path update our priority queue (relax)
					distances[neighbor] = alt
					previous[neighbor] = smallest
					for n in nodes:
						if n[1] == neighbor:
							n[0] = alt
							break
					heapq.heapify(nodes)
		return distances
		
	def __str__(self):
		return str(self.vertices)
		
# g = Graph()
# g.add_vertex('A', {'B': 7, 'C': 8})
# g.add_vertex('B', {'A': 7, 'F': 2})
# g.add_vertex('C', {'A': 8, 'F': 6, 'G': 4})
# g.add_vertex('D', {'F': 8})
# g.add_vertex('E', {'H': 1})
# g.add_vertex('F', {'B': 2, 'C': 6, 'D': 8, 'G': 9, 'H': 3})
# g.add_vertex('G', {'C': 4, 'F': 9})
# g.add_vertex('H', {'E': 1, 'F': 3})
# print g.shortest_path('A', 'H')

#-----------------------------------------------------------------------------------#
# https://gist.github.com/econchick/4666413

class Graph2:
	def init(self):
		self.nodes = set()
		# defaultdict is faster for larger data sets with more homogenous key sets
		self.edges = defaultdict(list)
		self.distances = {}

	def add_node(self, value):
		self.nodes.add(value)

	def add_edge(self, from_node, to_node, distance):
		self.edges[from_node].append(to_node)
		self.edges[to_node].append(from_node)
		self.distances[(from_node, to_node)] = distance


def dijkstra(graph, initial):
	visited = {initial: 0}
	path = defaultdict(list)
	# path = {}

	nodes = set(graph.nodes)

	while nodes: 
		min_node = None
		for node in nodes:
			if node in visited:
				if min_node is None:
					min_node = node
				elif visited[node] < visited[min_node]:
					min_node = node

		if min_node is None:
			break

		nodes.remove(min_node)
		current_weight = visited[min_node]

		for edge in graph.edges[min_node]:
			weight = current_weight + graph.distances[(min_node, edge)]
			if edge not in visited or weight < visited[edge]:
				visited[edge] = weight
				path[edge].append(min_node)
				# path[edge] = min_node

	return path













