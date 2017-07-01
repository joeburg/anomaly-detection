# python 
import sys
import time

# project 
import anomaly_detection


#-----------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------#

if len(sys.argv) < 4:
	print 'Usage:'
	print '  python %s <batch log file> <stream log file> <flagged purchases file> [D] [T]' %sys.argv[0]
	exit()

t0 = time.time()

batch_file = sys.argv[1]
stream_file = sys.argv[2]
flagged_file = sys.argv[3]

anomaly_detection.AnomalyDetection(batch_file, stream_file, flagged_file).process()
print 'Analyzed purchases in %.4f seconds.' %(time.time()-t0)

# process the data stream
# run the analysis 