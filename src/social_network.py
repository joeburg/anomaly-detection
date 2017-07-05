# python 

#-----------------------------------------------------------------------------------#
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
				# get the list of users for id1 and id2 that
				# are within D-1 of the them. The Dth users 
				# will not be affected by the new relationship;
				# use a set to eliminate repeats
				users = self.get_user_list(id1, self.D-1)
				users.update(self.get_user_list(id2, self.D-1))
				users.update([id1,id2])
				self.update_network(users)
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
				# get the list of users for id1 and id2 that
				# are within D-1 of the them. The Dth users 
				# will not be affected by the removed relationship
				users = self.get_user_list(id1, self.D-1)
				users.update(self.get_user_list(id2, self.D-1))
				users.update([id1,id2])
				self.update_network(users)
		else:
			print 'Unfriend event has incomplete data.'


	def are_friends(self, id1, id2):
		''' checks if id2 is id1's friend '''
		# ensure the users are in the network
		if id1 and id2 in self.friends:
			if id2 in self.friends[id1]:
				return True
		return False


	def update_network(self, specific_users=set([])):
		''' Updates a Dth degree network for every user
			in the network. If specific users are given,
			then it only updates the network for those users. '''

		# D must be gte 1 
		if self.D < 1:
			return False

		# if specific users given, only update their network
		if len(specific_users):
			for uid in specific_users:
				self.compute_neighborhood(uid, self.D)
		else:
			# update the entire network 
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

		# re-initialize the network for the source node
		self.network[source] = {}

		while True:
			# advance to the next level
			thislevel = nextlevel
			nextlevel = set([])

			for node in thislevel:
				if (node != source) and (node not in self.network[source]):
					self.network[source][node] = level

					# relationships are bi-directional, so 
					# include for N/2 speedup
					if node not in self.network:
						self.network[node] = {source: level}
					else:
						self.network[node][source] = level

				# add the friends of node to check next 
				nextlevel.update(self.friends[node])
					
			if cutoff <= level: 
				break

			level += 1


	def get_user_list(self, uid, cutoff=None):
		''' Returns the list of users in the given user's 
			Dth degree network. If a cutoff is given, then
			only users within a certain degree are returned.'''
		if uid in self.network:
			if cutoff:
				# only return users with a degree <= cutoff
				return set(id2 for id2 in self.network[uid] if self.network[uid][id2] <= cutoff)
			# otherwise, return all users in the network
			return set(self.network[uid].keys())
		return set([])


	def get_number_users(self):
		''' Returns the number of users in the network '''
		return len(self.friends)


	def set_network_degree(self, D):
		''' Allows to set the degree of the network and 
			updates the Dth degree network '''
		self.D = D 
		self.network = {}
		self.update_network()






