#!{PYTHON}
# example syntax: stack_s1.py workshop-test.yaml 2018-09-01 2018-09-05 /data/m5/s1_grd /data/m5/s1_stack

import datetime
import logging
import os
import sys
import yaml

from sar_pre_processing import NetcdfStackCreator

script_progress_logger = logging.getLogger('ScriptProgress')
script_progress_logger.setLevel(logging.INFO)
script_progress_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
script_progress_logging_handler = logging.StreamHandler()
script_progress_logging_handler.setLevel(logging.INFO)
script_progress_logging_handler.setFormatter(script_progress_formatter)
script_progress_logger.addHandler(script_progress_logging_handler)

# setup parameters
configuration_file = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]
s1_grd_dir = sys.argv[4]
s1_stack_dir = sys.argv[5]
with open(configuration_file) as f:
    parameters = yaml.load(f)
roi = parameters['General']['roi']
temporal_filter = parameters['SAR']['speckle_filter']['multi_temporal']['files']

script_progress_logger.info('0-100')
time_delta = datetime.timedelta(days=temporal_filter)
start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
start = start - time_delta
end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
end = end + time_delta

s1_grd_files = os.listdir(s1_grd_dir)
for s1_grd_file in s1_grd_files:
    date = datetime.datetime.strptime(s1_grd_file[17:25], '%Y%m%d')
    if date > start and date < end:
        os.symlink(os.path.join(s1_grd_dir, s1_grd_file), os.path.join(s1_stack_dir, s1_grd_file))

stack_file_name = f's1_nc_stack_{start_date}'
stack_creator = NetcdfStackCreator(input_folder=s1_stack_dir,
                                   output_path=s1_stack_dir,
                                   output_filename=stack_file_name)
stack_creator.create_netcdf_stack()

# clean
files = os.listdir(s1_grd_dir)
for file in files:
    if file != stack_file_name:
        os.remove(os.path.join(s1_stack_dir, file))

script_progress_logger.info('100-100')