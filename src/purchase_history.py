# python
import heapq
import numpy as np
import time
from itertools import imap
from operator import itemgetter

#-----------------------------------------------------------------------------------#

class PurchaseHistory:
	''' The purchase history stores the purchases for 
		individual users in the self.purchases attribtute '''

	def __init__(self, T):
		# purchases history for a given user 
		# data structure for purchases: { id: [(timestamp, amount), ...], ...}
		# data structure for purchases: { id: [(purchase#, timestamp, amount), ...], ...}
		# data structure for purchases: { purchase#: (id, timestamp, amount), ...}
		self.purchases = {}

		# number of consecutive purchases to be considered 
		self.T = int(T)

		# track the number of purchases to keep them in order
		# many purchases have the same timestamp
		self.Npurchase = 0


	def add_purchase(self, purchase):
		''' Adds a purcahse to a users history. Purchases come in 
			order of their timestamp. Many have the same timestamp 
			so treat the first call as an earlier timestamp. '''
		timestamp = purchase.get('timestamp')
		uid = purchase.get('id')
		amount = purchase.get('amount')

		# ensure all the data exists 
		if timestamp and uid and amount:
			self.purchases[self.Npurchase] = (uid, timestamp, float(amount))
			# self.purchases[self.Npurchase] = {	'uid': uid, 
			# 									'timestamp': timestamp, 
			# 									'amount': float(amount)}

			# # ensure the user has a purchase history 
			# if uid in self.purchases:
			# 	self.purchases[uid].append((self.Npurchase, timestamp, float(amount)))
			# else:
			# 	self.purchases[uid] = [(self.Npurchase, timestamp, float(amount))]

			# increment the number of purchases 
			self.Npurchase += 1

		else:
			print 'Purchase event has incomplete data.'


	def get_purchase_list(self, users):
		''' Returns a list of purchases for a given list of users 
			ordered by the timestamp'''

		# the network must have at least 2 purchases
		if self.T < 2: 
			return []
		
		purchases = []
		n = 0

		for i in range(self.Npurchase):
			# only T purchases are needed 
			if n > self.T-1:
				break 

			# newer purchases have larger Npurchase ids
			uid, timestamp, amount = self.purchases[self.Npurchase-1-i]

			# if self.purchases[self.Npurchase-1-i]['uid'] in users:
			if uid in users:
				purchases.append(amount)
				# purchases[idx] = self.purchases[self.Npurchase-1-i]['amount']
				# purchases.append(self.purchases[self.Npurchase-1-i]['amount'])
				n += 1

		mean = np.mean(np.array(purchases))
		sd = np.std(np.array(purchases))

		return (mean, sd, len(purchases))





		# # get the purchases in uid's network
		# purchases = []
		# for uid in users:
		# 	# speedup: consider T purchases at most 
		# 	# purchases += self.purchases[uid][:self.T]
		# 	purchases = sorted(purchases+self.purchases[uid], key=lambda x: x[0], reverse=True)
		# 	# purchases += self.purchases[uid]

		# sort the purchases by the timestamp
		# purchases = sorted(purchases, key=lambda x : x[0], reverse=True)
		# purchases.sort(key=lambda x : x[0], reverse=True)
		# purchases = sorted(purchases, key=lambda x : x[0])

		# purchases = sorted(purchases, key=lambda x: time.strptime(x[0], '%Y-%m-%d %H:%M:%S'), reverse=True)

		# decorate using generator expressions 
		# decorated = [((purchase) for purchase in self.purchases[uid]) for uid in users]

		# merge using heapq and undecorate using list()
		# merged = heapq.merge(*decorated)
		# undecorate
		# purchases = imap(itemgetter(-1), merged)

		# purchases = list(heapq.merge(*decorated))
		
		# print len(purchases)

		# purchases = heapq.merge(self.purchases[uid][:self.T] for uid in users)

		# purchases = []
		# for uid in users:
		# 	purchases = heapq.nlargest(self.T, purchases+self.purchases[uid])

		# purchases = list(heapq.nlargest(self.T, purchases))

		# creat a list of only the purchase amounts
		# purchases = [purchase[2] for purchase in purchases]

		# return at most T purchases
		# return purchases[:self.T]
		# return purchases[-self.T:]
		# return purchases


	def get_number_purchases(self):
		# return sum(len(lst) for lst in self.purchases.values())
		return self.Npurchase




