# python 
# import copy

#-----------------------------------------------------------------------------------#

class SocialNetwork:
	''' The social network stores the relationships between 
		users as well as their Dth degree networks. '''

	def __init__(self, D):
		# initialize the friends network 
		# keys are user ids and the values are set() of the users
		# data structure of friends network: { id1 : set(id2,...), ...}
		# constant time complexity to lookup friendships  		
		self.friends = {}

		# initialzie the Dth degree network
		# data structure of Dth network: { id1 : { id2 : level, ...}, ...}
		# Note that the level (degree of relationship) is stored to allow 
		# for efficient changes to the network without recomputing it
		self.network = {}

		# initialize the degree of the network 
		self.D = int(D)


	# def add_friend(self, id1, id2, update_needed=False):
	def add_friend(self, befriend, update_needed=False):
		''' adds a relationship between 2 users in the network '''

		id1 = befriend.get('id1')
		id2 = befriend.get('id2')

		# ensure all the data exists 
		if id1 and id2:		
			if id1 in self.friends:
				# add id2 to the set() of friends for id1
				self.friends[id1].add(id2)
			else:
				# if the user is not in the network, create the user
				# and then add the relationship
				self.friends[id1] = set([id2])

			# relationships are bi-directional so add the
			# relationship for id2 as well
			if id2 in self.friends:
				self.friends[id2].add(id1)
			else:
				self.friends[id2] = set([id1])

			# used to distinguish between add_friend() for batch data
			# versus stream data; network dosnt need to be updated until 
			# all batch data is added, whereas the network has to be 
			# updated in real-time with stream data
			if update_needed:
				self.update_network()
		else:
			print 'Befriend event has incomplete data.'


	# def remove_friend(self, id1, id2, update_needed=False):
	def remove_friend(self, unfriend, update_needed=False):
		''' removes the relationship between 2 users 
			in the network'''

		# keeps track if the friend was actually removed so
		# the network is only updated when needed 
		friend_removed = False

		id1 = unfriend.get('id1')
		id2 = unfriend.get('id2')

		# ensure all the data exists 
		if id1 and id2:
			# ensure the user is in the network before removing 
			# the relationship
			if id1 in self.friends:
				# ensure the relationship exists before removing 
				if self.are_friends(id1, id2):
					self.friends[id1].remove(id2)
					friend_removed = True 

			# relationships are bi-directional so remove 
			# relationship for id2 as well
			if id2 in self.friends:
				if self.are_friends(id2, id1):
					self.friends[id2].remove(id1)
					friend_removed = True 

			# update the Dth degree network if needed 
			if friend_removed and update_needed:
				self.update_network()
		else:
			print 'Unfriend event has incomplete data.'


	def are_friends(self, id1, id2):
		''' checks if id2 is id1's friend '''
		# ensure the users are in the network
		if id1 and id2 in self.friends:
			if id2 in self.friends[id1]:
				return True
		return False


	def update_network(self):
		''' Updates a Dth degree network for each user '''

		# D must be gte 1 
		if self.D < 1:
			return False

		for uid in self.friends:
			self.compute_neighborhood(uid, self.D)

		return True


	def compute_neighborhood(self, source, cutoff):
		''' Computes all the neighbors within some cutoff distance
			of a given source node.  '''

		# the set of neighbors are stored in the self.network
		# for a given node and the level of the relationship is 
		# kept track of: self.network[id1] = {id2: level, ...}

		# the current level of the search
		# starts at the level of friends         
		level = 1

		# nodes to check at the next level              
		nextlevel = self.friends[source]

		# make sure source is in the network 
		if source not in self.network:
			self.network[source] = {}

		while nextlevel:
			# advance to the next level
			thislevel = nextlevel
			nextlevel = set([])

			for node in thislevel:
				if (node != source) and (node not in self.network[source]):
					self.network[source][node] = level

					# add the friends of node to check next 
					nextlevel.update(self.friends[node])

					# relationships are bi-directional, so 
					# include for N/2 speedup
					if node not in self.network:
						self.network[node] = {source: level}
					else:
						self.network[node][source] = level
					
			if cutoff <= level: 
				break

			level += 1


	# def update_network(self):
	# 	''' Updates a Dth degree network for each user '''

	# 	# if D is 1, then just use the friends network
	# 	if self.D == 1:
	# 		# use a deep copy in case self.friends is changed
	# 		self.network = copy.deepcopy(self.friends)

	# 	elif self.D > 1:
	# 		# If the distance between the users is lte 
	# 		# the degree then add the user to the network.
	# 		# NOTE: this can probably be done much better 
	# 		# than the O(n^2) to check the pair-wise distances between 
	# 		# 'n' users. This is important because computing each 
	# 		# distance with BFS is O(n + e), where 'n' is the
	# 		# number of users and 'e' is the number of edges ('friends'). 

	# 		N = 0
	# 		for id1 in self.friends:
	# 			for id2 in self.friends:

	# 				# don't need to check distances between the same user
	# 				if id1 == id2:
	# 					continue 

	# 				# check if the users are already in each others network 
	# 				elif id1 in self.network:
	# 					if id2 in self.network[id1]:
	# 						continue

	# 				elif id2 in self.network:
	# 					if id1 in self.network[id2]:
	# 						continue

	# 				N += 1 
	# 				if N == 1:
	# 					print 'Interaction #%d' %N
	# 				elif N % 1000 == 0:
	# 					print 'Interaction #%d' %N


	# 				# compute the distance between the users 
	# 				path = self.shortest_path(id1, id2)

	# 				if not path:
	# 					continue 

	# 				# note: the path includes the start node 
	# 				# so len()-1 is comparable to D
	# 				path = set(path)

	# 				if len(path)-1 <= self.D:
	# 					# when adding additional nodes to the path
	# 					# exclude the self node (i.e id1 for id1)
	# 					# we are only interested in the user's network

	# 					# ensure that the id is in the network
	# 					if id1 in self.network:
	# 						self.network[id1].update(path - set([id1]))
	# 					else:
	# 						# note this includes the id1 itself in the network 
	# 						self.network[id1] = set(path - set([id1]))

	# 					# relationships are bi-directional
	# 					if id2 in self.network:
	# 						self.network[id2].update(path - set([id2]))
	# 					else:
	# 						self.network[id2] = set(path - set([id2])) 


	def bfs_paths(self, start, goal):
		''' The Breath-First search algorithm to determine the 
			distance between two nodes in the friends graph '''
		queue = [(start, [start])]
		while queue:
			(vertex, path) = queue.pop(0)

			# we are only interested in paths lte D 
			# note: path contains the vertex so Nsteps = path-1
			if len(path)-1 > self.D:
				yield None

			for next in self.friends[vertex] - set(path):
				if next == goal:
					yield path + [next]
				else:
					queue.append((next, path + [next]))


	def shortest_path(self, start, goal):
		''' Returns the shortest path between two nodes '''
		try:
			return next(self.bfs_paths(start, goal))
		except StopIteration:
			return None	


	def set_network_degree(self, D):
		''' This method allows to reset the degree of the network 
			without needing to rebuild the initial friends list '''
		self.D = D

		# update the network based on the set degree 
		self.update_network()


	def get_user_list(self, uid):
		''' Returns the list of users in the given user's 
			Dth degree network '''
		# return list(self.network[uid])
		return list(self.network[uid].keys())


	def get_number_users(self):
		return len(self.friends)





