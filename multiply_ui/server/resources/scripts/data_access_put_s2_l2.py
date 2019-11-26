#!/home/tonio-bc/.conda/envs/multiply-platform-dev/bin/python
# example syntax: data_access_put_s2_l2.py /data/mx/sdrs

from multiply_data_access import DataAccessComponent
import os
import sys

# setup parameters
sdrs_dir = sys.argv[1]

dac = DataAccessComponent()
for sdr in os.listdir(sdrs_dir):
	dac.put(sdrs_dir+'/'+sdr, 'S2L2')
