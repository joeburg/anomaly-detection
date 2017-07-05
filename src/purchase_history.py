# python
import numpy as np

#-----------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------#

class PurchaseHistory:
	''' The purchase history stores the purchases for 
		individual users in the self.purchases attribtute '''

	def __init__(self, T):
		# purchases history 
		# data structure for purchases: { Npurchase: (id, timestamp, amount), ...}
		# This data structure is optimized for returning the last T purchases 
		# for a select group of users. It takes advanted of the sequential 
		# data that comes in via the batch and stream.
		self.purchases = {}

		# number of consecutive purchases to be considered 
		self.T = int(T)

		# track the number of purchases to keep them in order;
		# many purchases have the same timestamp; this also allows 
		# for no sort when accessing the last T purchases 
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

			# increment the number of purchases 
			self.Npurchase += 1

		else:
			print 'Purchase event has incomplete data.'


	def get_purchase_stats(self, users):
		''' Returns the mean and std for a list of purchases for 
			a given list of users ordered by the timestamp '''

		# the network must have at least 2 purchases
		if self.T < 2: 
			return (0, 0, 0)
		
		purchases = []
		n = 0

		# The purchases are pre-sorted by the order in which they 
		# come in from the batch/stream. This can be verified by looking 
		# at the timestamps. Using this, all we need to do to get the last 
		# T purchases for the given group of users is start with the most
		# recent purchases and check if it's by one of the users. Getting 
		# the purchase stats is at best O(T) and at worst O(n), where n is 
		# the number of purchases and T is the cutoff.
		for i in range(self.Npurchase):
			# only T purchases are needed 
			if n > self.T-1:
				break 

			# newer purchases have larger Npurchase ids -> use (Npurchase-1)-i
			uid, timestamp, amount = self.purchases[self.Npurchase-1-i]

			# we only interested in purchases from the users given
			if uid in users:
				purchases.append(amount)
				n += 1

		# ensure that the number of purchases are >2 and <T
		if not len(purchases)>2 and len(purchases)<=self.T:
			return (0,0,0)

		mean = np.mean(np.array(purchases))
		sd = np.std(np.array(purchases))

		return (mean, sd, len(purchases))


	def get_number_purchases(self):
		''' Returns the number of purchases in the history '''
		return self.Npurchase

	def set_purchase_cutoff(self, T):
		''' Allows the set of number of consecutive 
			purchases to be considered '''
		self.T = T



