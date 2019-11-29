#!{PYTHON}
# example syntax: data_access_put_s2_l2.py /data/mx/sdrs

from multiply_data_access import DataAccessComponent
import logging
import os
import sys

logger = logging.getLogger('ScriptProgress')
logger.setLevel(logging.INFO)

# setup parameters
sdrs_dir = sys.argv[1]

dac = DataAccessComponent()
sdrs = os.listdir(sdrs_dir)
for i, sdr in enumerate(sdrs):
    logger.info(f'{int((i/len(sdrs)) * 100)}-{int((i+1/len(sdrs)) * 100)}')
    dac.put(sdrs_dir + '/' + sdr, 'S2L2')
logger.info('100-100')
