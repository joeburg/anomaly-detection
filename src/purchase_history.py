
class PurchaseHistory:
	''' The purchase history stores the purchases for 
		individual users in the self.purchases attribtute '''

	def __init__(self, T):
		# purchases history for a given user 
		# data structure for purchases: { id: [(timestamp, amount), ...], ...}
		self.purchases = {}

		# number of consecutive purchases to be considered 
		self.T = int(T)


	def add_purchase(self, purchase):
		''' Adds a purcahse to a users history '''
		timestamp = purchase.get('timestamp')
		uid = purchase.get('id')
		amount = purchase.get('amount')

		# ensure all the data exists 
		if timestamp and uid and amount:
			# ensure the user has a purchase history 
			if uid in self.purchases:
				self.purchases[uid].append((timestamp, float(amount)))
			else:
				self.purchases[uid] = [(timestamp, float(amount))]

		else:
			print 'Purchase event has incomplete data.'


	def get_purchase_list(self, users):
		''' Returns a list of purchases for a given list of users 
			ordered by the timestamp'''

		# the network must have at least 2 purchases
		if self.T < 2: 
			return False

		# get the purchases in uid's network
		purchases = []
		for uid in users:
			purchases += self.purchases[uid]
			# consider using this -> only can have T purchases at most 
			# purchases += self.purchases[uid][:self.T]

		# sort the purchases by the timestamp
		purchases = sorted(purchases, key=lambda x : x[0])

		# creat a list of only the purchase amounts
		purchases = [purchase[1] for purchase in purchases]

		# return at most T purchases
		return purchases[:self.T]


	def get_number_purchases(self):
		return sum(len(lst) for lst in self.purchases.values())