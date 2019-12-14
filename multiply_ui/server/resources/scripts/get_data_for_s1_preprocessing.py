#!{PYTHON}

import datetime
import logging
import os
import shutil
import sys
import yaml

from sar_pre_processing import SARPreProcessor
from vm_support import create_sym_links

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
s1_slc_dir = sys.argv[4]
with open(configuration_file) as f:
    parameters = yaml.load(f)
roi = parameters['General']['roi']
temporal_filter = parameters['SAR']['speckle_filter']['multi_temporal']['temporal_filter']

from multiply_data_access import DataAccessComponent
dac = DataAccessComponent()

before_sar_dir = os.path.join(s1_slc_dir, 'before')
if not os.path.exists(before_sar_dir):
    os.makedirs(before_sar_dir)

one_day = datetime.timedelta(days=1)
start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
before = start
before_date = datetime.datetime.strftime(before, '%Y-%m-%d')
previous_num_before = -1
num_before = 0
script_progress_logger.info('0-0')
while num_before < temporal_filter:
    if previous_num_before != num_before:
        script_progress_logger.info(f'{int((num_before / temporal_filter) * 50)}-'
                                    f'{int(((num_before + 1) / temporal_filter) * 50)}')
    before -= one_day
    before_date = datetime.datetime.strftime(before, '%Y-%m-%d')
    data_urls_before = dac.get_data_urls(roi, before_date, start_date, 'S1_SLC')
    create_sym_links(data_urls_before, before_sar_dir)
    processor = SARPreProcessor(config=configuration_file, input=before_sar_dir, output=before_sar_dir)
    list = processor.create_processing_file_list()
    previous_num_before = num_before
    num_before = len(list[0]) + (len(list[1]) / 2.)

after_sar_dir = os.path.join(s1_slc_dir, 'after')
if not os.path.exists(after_sar_dir):
    os.makedirs(after_sar_dir)

end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
after = end
after_date = datetime.datetime.strftime(after, '%Y-%m-%d')
previous_num_after = -1
num_after = 0
while num_after < temporal_filter and after < datetime.datetime.today():
    if previous_num_before != num_before:
        script_progress_logger.info(f'{50 + int(((num_after / temporal_filter) * 50))}-'
                                    f'{50 + int((((num_after + 1) / temporal_filter) * 50))}')
    after += one_day
    after_date = datetime.datetime.strftime(after, '%Y-%m-%d')
    data_urls_after = dac.get_data_urls(roi, end_date, after_date, 'S1_SLC')
    create_sym_links(data_urls_after, after_sar_dir)
    processor = SARPreProcessor(config=configuration_file, input=after_sar_dir, output=after_sar_dir)
    list = processor.create_processing_file_list()
    num_after = len(list[0]) + (len(list[1]) / 2.)

shutil.rmtree(before_sar_dir)
shutil.rmtree(after_sar_dir)

sar_data_urls = dac.get_data_urls(roi, before_date, after_date, 'S1_SLC')
create_sym_links(sar_data_urls, s1_slc_dir)

script_progress_logger.info('100-100')
