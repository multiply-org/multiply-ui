#!{PYTHON}
# example syntax: data_access_put_s2_l2.py /data/mx/sdrs

from multiply_data_access import DataAccessComponent
import logging
import os
import sys

logger = logging.getLogger('ScriptProgress')
logger.setLevel(logging.INFO)

# setup parameters
configuration_file = sys.argv[1]
start_date = sys.argv[2]
stop_date = sys.argv[3]
sdrs_dir = sys.argv[4]
provided_sdrs_dir = sys.argv[5]

dac = DataAccessComponent()
sdrs = os.listdir(sdrs_dir)
for i, sdr in enumerate(sdrs):
    logger.info(f'{int((i/len(sdrs)) * 100)}-{int((i+1/len(sdrs)) * 100)}')
    if not os.path.exists(os.path.join(provided_sdrs_dir, sdr)):
        dac.put(os.path.join(sdrs_dir, sdr), 'S2L2')
logger.info('100-100')
