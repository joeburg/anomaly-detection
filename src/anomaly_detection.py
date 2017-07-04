# python 
import json
import numpy as np
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

	def __init__(self, batch_file, stream_file, flagged_file, D=None, T=None):
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

		# used to track the performance of network and purchase data
		self.anomaly_times = []
		self.befriend_times = []
		self.unfriend_times = []


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
		print 'Analyzed %d stream events in %.4f seconds.' \
				%(self.Nstream, time.time()-t0)

		anomaly_time = np.mean(np.array(self.anomaly_times))
		anomaly_sd = np.std(np.array(self.anomaly_times))
		befriend_time = np.mean(np.array(self.befriend_times))
		befriend_sd = np.std(np.array(self.befriend_times))
		unfriend_time = np.mean(np.array(self.unfriend_times))
		unfriend_sd = np.std(np.array(self.unfriend_times))
		print '\nAverage (from %d) anomaly check time = %.6f +/- %.6f' %(len(self.anomaly_times), anomaly_time, anomaly_sd)
		print 'Average (from %d) befriend time = %.6f +/- %.6f' %(len(self.befriend_times), befriend_time, befriend_sd)
		print 'Average (from %d) unfriend time = %.6f +/- %.6f' %(len(self.unfriend_times), unfriend_time, unfriend_sd)

		add_friend_time = np.mean(np.array(self.network.add_friend_times))
		add_friend_sd = np.std(np.array(self.network.add_friend_times))
		update_friend_time = np.mean(np.array(self.network.update_friend_times))
		update_friend_sd = np.mean(np.array(self.network.update_friend_times))
		update_network_time = np.mean(np.array(self.network.update_network_times))
		update_network_sd = np.mean(np.array(self.network.update_network_times))

		print '\nAverage (from %d) add friend time = %.8f +/- %.8f' %(len(self.network.add_friend_times), add_friend_time, add_friend_sd)
		print 'Average (from %d) update friend time = %.8f +/- %.8f' %(len(self.network.update_friend_times), update_friend_time, update_friend_sd)
		print 'Average (from %d) update network time = %.8f +/- %.8f' %(len(self.network.update_network_times), update_network_time, update_network_sd)		


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
						t0 = time.time()
						self.check_for_anomaly(event)
						self.anomaly_times.append(time.time()-t0)
					# both stream and batch data add purchases 
					# to the user's history 
					self.purchases.add_purchase(event)

				elif event['event_type'] == 'befriend':
					if data_type == 'stream':
						self.Nstream += 1
						# stream data immediately updates the network
						t0 = time.time()
						self.network.add_friend(event, update_needed=True)
						self.befriend_times.append(time.time()-t0)
					else:
						# batch data does not immediately
						# update the network 
						self.network.add_friend(event)

				elif event['event_type'] == 'unfriend':
					if data_type == 'stream':
						self.Nstream += 1
						t0 = time.time()
						self.network.remove_friend(event, update_needed=True)
						self.unfriend_times.append(time.time()-t0)
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

			if len(purchases):
				mean = np.mean(np.array(purchases))
				sd = np.std(np.array(purchases))
				amount = float(amount)

				# purchase is an anomaly if it's more than 3 sd's from the mean
				if amount > mean + (3*sd):

					print 'Anomalous purchase in network of %d user(s) and %d purchase(s): $%.2f' \
							%(len(users), len(purchases), amount)

					# write anomaly to the flagged purchases
					f = open(self.flagged_file, 'a')
					f.write('{"event_type": "%s", "timestamp": "%s", "id": "%s", "amount": "%.2f", "mean": "%.2f", "sd": "%.2f"}\n' \
								%(purchase['event_type'], purchase['timestamp'], purchase['id'], amount, mean, sd))
					f.close()

		else:
			print 'Purchase event has incomplete data.'















