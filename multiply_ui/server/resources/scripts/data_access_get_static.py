#!{PYTHON}
#  example syntax: data_access_get_static.py request_test_all.yaml 2017-06-11 2016-06-21 /data/mx/wv_emu_dir /data/mx/emu_dir /data/mx/dem_dir

from multiply_data_access import DataAccessComponent
from vm_support import create_sym_links
import logging
import os
import sys
import yaml

logger = logging.getLogger('ScriptProcess')
logger.setLevel(logging.INFO)

# setup parameters
configuration_file = sys.argv[1]
start_date = sys.argv[2]
stop_date = sys.argv[3]
emu_dir = sys.argv[4]
dem_dir = sys.argv[5]
def create_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
create_dir(emu_dir)
create_dir(dem_dir)

# read request file for parameters
with open(configuration_file) as f:
    parameters = yaml.safe_load(f)

roi = parameters['General']['roi']

dac = DataAccessComponent()
logger.info('0-50')
emu_urls = dac.get_data_urls(roi, start_date, stop_date, 'ISO_MSI_A_EMU,ISO_MSI_B_EMU')
create_sym_links(emu_urls, emu_dir)
logger.info('50-100')
dem_urls = dac.get_data_urls(roi, start_date, stop_date, 'Aster DEM')
create_sym_links(dem_urls, dem_dir)
logger.info('100-100')
