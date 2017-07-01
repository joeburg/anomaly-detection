# python 
import json
import numpy as np

# project 
from purchase_history import PurchaseHistory
from social_network import SocialNetwork

#-----------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------#

class AnomalyDetection:

	def __init__(self, batch_file, stream_file, flagged_file, D=None, T=None):
		# set the filenames as data attributes 
		self.batch_file = batch_file
		self.stream_file = stream_file
		self.flagged_file = flagged_file

		# the social network and purchase history are 
		# also data attributes 
		self.network = {}
		self.purchases = {}

	def process(self):
		''' method to load and process the data '''
		# load the batch data
		self.analyze_batch_data()

		# analyze the stream data
		self.analyze_stream_data()


	def analyze_batch_data(self):
		''' loads the batch data and creates network and 
			purchases objects '''
		f = open(self.batch_file)

		# the first line contains the degree (D) and number of 
		# tracked purchases (T). Initialize objects 
		params = json.loads(f.readline().strip())
		self.initialize_objects(params)
	
		# process each subsequent event in the batch data
		f = self.process_events(f, 'batch')
		f.close()

		# once all the users are loaded to the social 
		# network, generate the Dth degree network 
		self.network.build_network()


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
						self.check_for_anomaly(event)
					# both stream and batch data add purchases 
					# to the user's history 
					self.purchases.add_purchase(event)

				elif event['event_type'] == 'befriend':
					if data_type == 'stream':
						# stream data immediately updates the network
						self.network.add_friend(event, update_needed=True)
					else:
						# batch data does not immediately
						# update the network 
						self.network.add_friend(event)

				elif event['event_type'] == 'unfriend':
					if data_type == 'stream':
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
					'purchases (T) incorrectly input.'
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
			purchases = self.purchases.get_purchase_list(users)

			mean = np.mean(np.array(purchases))
			sd = np.std(np.array(purchases))

			# purchase is an anomaly if it's more than 3 sd's 
			# from the mean
			if amount > mean + (3*sd):
				# add the mean and sd to the event 
				purchase['mean'] = '%.2f' %mean
				purchase['sd'] = '%.2f' %sd

				# write anomaly to the flagged purchases
				f = open(self.flagged_file, 'a')
				f.write('%s\n' % json.dumps(purchase))
				f.close()
		else:
			print 'Purchase event has incomplete data.'















