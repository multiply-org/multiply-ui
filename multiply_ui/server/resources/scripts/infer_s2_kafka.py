#!{PYTHON}

from multiply_inference_engine import infer
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

# extract directory names from input arguments
start_date = sys.argv[2]
end_date = sys.argv[3]
previous_state = sys.argv[4]
if previous_state == 'none':
    previous_state=None
priors_dir = sys.argv[5]
observations_dir = sys.argv[6]
output_dir = sys.argv[7]
next_state = sys.argv[8]

# setup parameters
with open(sys.argv[1]) as f:
    parameters = yaml.load(f)
roi = parameters['General']['roi']
spatial_resolution = parameters['General']['spatial_resolution'] # in m
if 'roi_grid' in parameters['General']:
    roi_grid = parameters['General']['roi_grid']
else:
    roi_grid = None
if 'destination_grid' in parameters['General']:
    destination_grid = parameters['General']['destination_grid']
else:
    destination_grid = None

forward_models = []
requested_parameters = []
model_parameters = []
required_priors = []
for model_dict in parameters['Inference']['forward_models']:
    if model_dict['type'] == 'kafka' and model_dict['data_type'] == 'Sentinel-2':
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

if not os.path.exists(next_state):
    os.makedirs(next_state)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

script_progress_logger.info('0-100')

infer(start_time=start_date,
      end_time=end_date,
      parameter_list=requested_parameters,
      prior_directory=priors_dir,
      datasets_dir=observations_dir,
      previous_state_dir=previous_state,
      next_state_dir=next_state,
      forward_models=forward_models,
      output_directory=output_dir,
      roi=roi,
      spatial_resolution=spatial_resolution,
      roi_grid=roi_grid,
      destination_grid=destination_grid
      )
script_progress_logger.info('100-100')


