# python 
import json
import time

# project 
from purchase_history import PurchaseHistory
from social_network import SocialNetwork

#-----------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------#

class AnomalyDetection:
	''' This class analyzes historical batch data and then 
		compares incoming stream data to determine if a user's 
		purchase is anomalous within their Dth degree social network '''

	def __init__(self, batch_file, stream_file, flagged_file):
		# set the filenames as data attributes 
		self.batch_file = batch_file
		self.stream_file = stream_file
		self.flagged_file = flagged_file

		# the social network and purchase history are 
		# also data attributes 
		self.network = {}
		self.purchases = {}

		# keep track of the number of stream events processed 
		self.Nstream = 0


	def process(self):
		''' method to load and process the data '''
		# load the batch data
		print 'Loading batch data...'
		t0 = time.time()
		self.analyze_batch_data()
		print 'Batch data loaded (%s users and %d purchases) in %.4f seconds.'\
				% (self.network.get_number_users(),
					self.purchases.get_number_purchases(),
					time.time()-t0)

		# analyze the stream data
		print '\nAnalyzing stream data...'
		t0 = time.time()
		self.analyze_stream_data()
		t = time.time() - t0
		print '\nAnalyzed %d stream events in %.4f seconds.' \
				%(self.Nstream, t)
		print 'Analysis capacity: %.2f events/second' %(self.Nstream/t)


	def analyze_batch_data(self):
		''' loads the batch data and creates network and 
			purchases objects '''
		f = open(self.batch_file)

		# the first line contains the degree (D) and number of 
		# tracked purchases (T). Initialize objects. 
		params = json.loads(f.readline().strip())
		self.initialize_objects(params)
	
		# process each subsequent event in the batch data
		f = self.process_events(f, 'batch')
		f.close()

		# once all the users are loaded to the social 
		# network, generate the Dth degree network		
		self.network.update_network()


	def process_events(self, f, data_type):
		''' Process events in a data stream. If the data
			comes from batch data, then update_needed should
			be False, while it's True for stream data. '''

		# process each event in the data stream 
		while True:
			line = f.readline().strip()
			if line:
				event = json.loads(line)

				if event['event_type'] == 'purchase':
					if data_type == 'stream':
						self.Nstream += 1
						self.check_for_anomaly(event)
					# both stream and batch data add purchases 
					# to the user's history 
					self.purchases.add_purchase(event)

				elif event['event_type'] == 'befriend':
					if data_type == 'stream':
						self.Nstream += 1
						# stream data immediately updates the network
						self.network.add_friend(event, update_needed=True)
					else:
						# batch data does not immediately
						# update the network 
						self.network.add_friend(event)

				elif event['event_type'] == 'unfriend':
					if data_type == 'stream':
						self.Nstream += 1
						self.network.remove_friend(event, update_needed=True)
					else:
						# batch data 
						self.network.remove_friend(event)
			else:
				break
		return f


	def initialize_objects(self, params):
		''' Ensures that the social network and purchase 
			history are initialized correctly '''

		if 'D' and 'T' in params:
			D = params['D']
			T = params['T']
		else:
			print 'The degree (D) and number of tracked '+\
					'purchases (T) were incorrectly input.'
			D = input('Give the degree of the network (D): ')
			T = input('Give the tracked purchases (T): ')

		self.network = SocialNetwork(D)
		self.purchases = PurchaseHistory(T)


	def analyze_stream_data(self):
		''' Analyzed each event in the stream data '''
		f = open(self.stream_file)
		f = self.process_events(f, 'stream')
		f.close()


	def check_for_anomaly(self, purchase):
		''' Determines if a purchase is an anomaly '''

		uid = purchase.get('id')
		amount = purchase.get('amount')

		if uid and amount:
			# get the last T purchases in the uid's network
			users = self.network.get_user_list(uid)
			mean, sd, Npurchases = self.purchases.get_purchase_stats(users)

			if mean and sd:
				amount = float(amount)
				# purchase is an anomaly if it's more than 3 sd's from the mean
				if amount > mean + (3*sd):

					print 'Anomalous purchase in network of %d user(s) and %d purchase(s): $%.2f' \
							%(len(users), Npurchases, amount)

					# write anomaly to the flagged purchases
					f = open(self.flagged_file, 'a')
					f.write('{"event_type": "%s", "timestamp": "%s", "id": "%s", "amount": "%.2f", "mean": "%.2f", "sd": "%.2f"}\n' \
								%(purchase['event_type'], purchase['timestamp'], purchase['id'], amount, mean, sd))
					f.close()
					return True

		else:
			print 'Purchase event has incomplete data.'
		return False















