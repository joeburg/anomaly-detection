# python 
import time

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

		self.add_friend_times = []
		self.update_friend_times = []
		self.update_network_times = []


	# def add_friend(self, id1, id2, update_needed=False):
	def add_friend(self, befriend, update_needed=False):
		''' adds a relationship between 2 users in the network '''

		id1 = befriend.get('id1')
		id2 = befriend.get('id2')

		# ensure all the data exists 
		if id1 and id2:		
			if id1 in self.friends:
				# add id2 to the set() of friends for id1
				t0 = time.time()
				self.friends[id1].add(id2)
				self.add_friend_times.append(time.time()-t0)
			else:
				# if the user is not in the network, create the user
				# and then add the relationship
				t0 = time.time()
				self.friends[id1] = set([id2])
				self.update_friend_times.append(time.time()-t0)

			# relationships are bi-directional so add the
			# relationship for id2 as well
			if id2 in self.friends:
				t0 = time.time()
				self.friends[id2].add(id1)
				self.add_friend_times.append(time.time()-t0)
			else:
				self.friends[id2] = set([id1])
				self.update_friend_times.append(time.time()-t0)

			# used to distinguish between add_friend() for batch data
			# versus stream data; network dosnt need to be updated until 
			# all batch data is added, whereas the network has to be 
			# updated in real-time with stream data
			if update_needed:
				t0 = time.time()
				# get the list of users for id1 and id2 that
				# are within D-1 of the them. The Dth users 
				# will not be affected by the new relationship
				# users1 = self.get_user_list(id1, self.D-1)
				# users2 = self.get_user_list(id2, self.D-1)
				users = self.get_user_list(id1, self.D-1)
				users.update(self.get_user_list(id2, self.D-1))
				users.update([id1,id2])
				# update the networks of each user in
				# id1 and id2's networks
				# use a set to eliminate repeats
				# users = users1.update(users2).update([id1, id2])
				# users = set(users1 + users2 + [id1, id2])
				self.update_network(users)
				self.update_network_times.append(time.time()-t0)
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
				# users1 = self.get_user_list(id1, self.D-1)
				# users2 = self.get_user_list(id2, self.D-1)
				users = self.get_user_list(id1, self.D-1)
				users.update(self.get_user_list(id2, self.D-1))
				users.update([id1,id2])
				# update the networks of each user in
				# id1 and id2's networks
				# use a set to eliminate repeats
				# users = set(users1 + users2 + [id1, id2])
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

	def set_network_degree(self, D):
		''' This method allows to reset the degree of the network 
			without needing to rebuild the initial friends list '''
		self.D = D

		# update the network based on the set degree 
		self.update_network()


	def get_user_list(self, uid, cutoff=None):
		''' Returns the list of users in the given user's 
			Dth degree network. If a cutoff is given, then
			only users within a certain degree are returned.'''
		if uid in self.network:
			if cutoff:
				# only return users with a degree <= cutoff
				# return list(id2 for id2 in self.network[uid] if self.network[uid][id2] <= cutoff)
				return set(id2 for id2 in self.network[uid] if self.network[uid][id2] <= cutoff)
			# otherwise, return all users in the network
			# return list(self.network[uid].keys())
			return set(self.network[uid].keys())
		return set([])


	def get_number_users(self):
		return len(self.friends)





