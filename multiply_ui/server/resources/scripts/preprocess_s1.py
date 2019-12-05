#!{PYTHON}

import logging
import sys
import yaml

from sar_pre_processing import SARPreProcessor

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
s1_grd_dir = sys.argv[5]
with open(configuration_file) as f:
    parameters = yaml.load(f)
roi = parameters['General']['roi']
temporal_filter = parameters['SAR']['speckle_filter']['multi_temporal']['files']

processor = SARPreProcessor(config=configuration_file, input=s1_slc_dir, output=s1_grd_dir)
processor.create_processing_file_list()
script_progress_logger.info('0-30')
processor.pre_process_step1()
script_progress_logger.info('30-60')
processor.pre_process_step2()
script_progress_logger.info('60-90')
processor.pre_process_step3()
script_progress_logger.info('90-100')
processor.solve_projection_problem()
processor.add_netcdf_information()
processor.create_netcdf_stack()
script_progress_logger.info('100-100')
