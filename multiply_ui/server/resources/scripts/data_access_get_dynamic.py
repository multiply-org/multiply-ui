#!{PYTHON}
# example syntax: data_access_get_dynamic.py request_test_all.yaml 2017-06-11 2016-06-21 /data/mx/2017-06-11/modis_dir /data/mx/2017-06-11/cams_tiff_dir /data/mx/2017-06-11/s2_dir
 
from multiply_data_access import DataAccessComponent
from vm_support import create_sym_links
import datetime
import os
import sys
import yaml

# setup parameters
configuration_file = sys.argv[1]
start_date = sys.argv[2]
stop_date = sys.argv[3]
modis_dir = sys.argv[4]
cams_tiff_dir = sys.argv[5]
s2_dir = sys.argv[6]
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

print("Progress=0")

modis_delta = datetime.timedelta(days=16)
start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
modis_start = start - modis_delta
modis_start_date = datetime.datetime.strftime(modis_start, '%Y-%m-%d')
end = datetime.datetime.strptime(stop_date, '%Y-%m-%d')
modis_end = end + modis_delta
modis_end_date = datetime.datetime.strftime(modis_end, '%Y-%m-%d')

dac = DataAccessComponent()
modis_urls = dac.get_data_urls(roi, modis_start_date, modis_end_date, 'MCD43A1.006')
create_sym_links(modis_urls, modis_dir)
print("Progress=33")
cams_urls = dac.get_data_urls(roi, start_date, stop_date, 'CAMS_TIFF')
create_sym_links(cams_urls, cams_tiff_dir)
print("Progress=66")
s2_urls = dac.get_data_urls(roi, start_date, stop_date, 'AWS_S2_L1C')
create_sym_links(s2_urls, s2_dir)
print("Progrtess=100")
