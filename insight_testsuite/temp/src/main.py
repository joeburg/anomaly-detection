# python 
import sys
import time

# project 
from anomaly_detection import AnomalyDetection

#-----------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------#

if len(sys.argv) < 4:
	print 'Usage:'
	print '  python %s <batch log file> <stream log file> <flagged purchases file>' %sys.argv[0]
	exit()

t0 = time.time()

batch_file = sys.argv[1]
stream_file = sys.argv[2]
flagged_file = sys.argv[3]

AnomalyDetection(batch_file, stream_file, flagged_file).process()

print '\nProcessed batch and stream in %.4f seconds.' %(time.time()-t0)
