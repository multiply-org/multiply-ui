#!{PYTHON}

from multiply_inference_engine import create_kaska_s2_inference_output_files
from multiply_core.models import get_forward_model

import logging
import os
import sys
import yaml

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
stop_date = sys.argv[3]
output_dir = sys.argv[4]

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# read request file for parameters
with open(configuration_file) as f:
    parameters = yaml.safe_load(f)

roi = parameters['General']['roi']
spatial_resolution = parameters['General']['spatial_resolution']  # in m
time_step = int(parameters['General']['time_interval'])
tile_width = int(parameters['General']['tile_width'])
tile_height = int(parameters['General']['tile_height'])

forward_models = []
requested_parameters = []
model_parameters = []
required_priors = []
for model_dict in parameters['Inference']['forward_models']:
    if model_dict['type'] == 'kaska' and model_dict['data_type'] == 'Sentinel-2':
        forward_models.append(model_dict['name'])
        requested_model_parameters = model_dict['output_parameters']
        for model_parameter in requested_model_parameters:
            if model_parameter not in requested_parameters:
                requested_parameters.append(model_parameter)
        forward_model = get_forward_model(model_dict['name'])
        output_parameters = forward_model.variables
        for output_parameter in output_parameters:
            if output_parameter not in model_parameters:
                model_parameters.append(output_parameter)
    elif model_dict['type'] == 'kaska' and model_dict['data_type'] == 'Sentinel-1':
        required_priors = model_dict['required_priors']
for prior in required_priors:
    if prior in model_parameters and prior not in requested_parameters:
        requested_parameters.append(prior)

script_progress_logger.info('0-100')
create_kaska_s2_inference_output_files(start_time=start_date,
                                       end_time=stop_date,
                                       time_step=time_step,
                                       forward_models=forward_models,
                                       output_directory=output_dir,
                                       parameters=requested_parameters,
                                       roi=roi,
                                       spatial_resolution=spatial_resolution
               )
script_progress_logger.info('100-100')
