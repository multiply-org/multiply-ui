#!{PYTHON}
# example syntax: get_data_for_s2_preprocessing.py request_test_all.yaml 2017-06-11 2016-06-21 /data/mx/2017-06-11/modis_dir /data/mx/2017-06-11/cams_tiff_dir /data/mx/2017-06-11/s2_dir

from multiply_core.observations import DataTypeConstants, is_valid
from multiply_data_access import DataAccessComponent
from vm_support import create_sym_links
import datetime
import logging
import os
import sys
import yaml

logger = logging.getLogger('ScriptProgress')
logger.setLevel(logging.INFO)

# setup parameters
configuration_file = sys.argv[1]
start_date = sys.argv[2]
stop_date = sys.argv[3]
modis_dir = sys.argv[4]
cams_tiff_dir = sys.argv[5]
s2_dir = sys.argv[6]
provided_sdrs_dir = sys.argv[7]

def create_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

create_dir(modis_dir)
create_dir(cams_tiff_dir)
create_dir(s2_dir)

# read request file for parameters
with open(configuration_file) as f:
    parameters = yaml.load(f)

roi = parameters['General']['roi']

dac = DataAccessComponent()
logger.info('0-33')
s2_urls = dac.get_data_urls(roi, start_date, stop_date, 'Sentinel-2')
s2_l1c_urls = []
sdr_urls = []
for s2_url in s2_urls:
    if is_valid(s2_url, DataTypeConstants.S2_L1C):
        s2_l1c_urls.append(s2_url)
    elif is_valid(s2_url, DataTypeConstants.S2_L2):
        sdr_urls.append(s2_url)
create_sym_links(s2_l1c_urls, s2_dir)
create_sym_links(sdr_urls, provided_sdrs_dir)
if len(s2_l1c_urls) > 0:
    logger.info('33-67')
    modis_delta = datetime.timedelta(days=16)
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    modis_start = start - modis_delta
    modis_start_date = datetime.datetime.strftime(modis_start, '%Y-%m-%d')
    end = datetime.datetime.strptime(stop_date, '%Y-%m-%d')
    modis_end = end + modis_delta
    modis_end_date = datetime.datetime.strftime(modis_end, '%Y-%m-%d')
    modis_urls = dac.get_data_urls(roi, modis_start_date, modis_end_date, 'MCD43A1.006')
    create_sym_links(modis_urls, modis_dir)
    logger.info('67-100')
    cams_urls = dac.get_data_urls(roi, start_date, stop_date, 'CAMS_TIFF')
    create_sym_links(cams_urls, cams_tiff_dir)
    logger.info('100-100')
