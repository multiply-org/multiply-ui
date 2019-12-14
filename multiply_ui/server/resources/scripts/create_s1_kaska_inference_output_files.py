#!{PYTHON}

from multiply_inference_engine import create_kaska_s1_inference_output_files

import logging
import sys
import yaml

script_progress_logger = logging.getLogger('ScriptProgress')
script_progress_logger.setLevel(logging.INFO)
script_progress_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
script_progress_logging_handler = logging.StreamHandler()
script_progress_logging_handler.setLevel(logging.INFO)
script_progress_logging_handler.setFormatter(script_progress_formatter)
script_progress_logger.addHandler(script_progress_logging_handler)

# extract directory names from input arguments
configuration_file = sys.argv[1]
start_date = sys.argv[2]
stop_date = sys.argv[3]
s1_stack_for_date_dir = sys.argv[4]
s1_priors_dir = sys.argv[5]
output_dir = sys.argv[6]

# setup parameters
with open(sys.argv[1]) as f:
    parameters = yaml.load(f)
roi = parameters['General']['roi']
spatial_resolution = parameters['General']['spatial_resolution']
variables = []
for model_dict in parameters['Inference']['forward_models']:
    if model_dict['type'] == 'kaska' and model_dict['data_type'] == 'Sentinel-1':
        requested_model_parameters = model_dict['output_parameters']
        for requested_model_parameter in requested_model_parameters:
            if requested_model_parameter not in variables:
                variables.append(requested_model_parameter)

script_progress_logger.info('0-100')
create_kaska_s1_inference_output_files(s1_stack_file_dir=s1_stack_for_date_dir, 
                                       priors_dir=s1_priors_dir, 
                                       output_directory=output_dir, 
                                       parameters=variables,
                                       roi=roi,
                                       spatial_resolution=spatial_resolution
                                       )
script_progress_logger.info('100-100')
