#!{PYTHON}

import logging
import os
import sys
import yaml

logger = logging.getLogger('ScriptProcess')
logger.setLevel(logging.INFO)

processor_dir = '/software/inference-engine-0.4/multiply_inference_engine'
s2_emulators_dir = '/data/archive/emulators/s2_prosail'
inference_type = 'high'

# extract directory names from input arguments
start_date = sys.argv[2]
end_date = sys.argv[3]
previous_state = sys.argv[4]
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
parameter_list = ','.join(parameters['Inference']['parameters'])
forward_model_list = 's2_prosail'

if not os.path.exists(next_state):
    os.makedirs(next_state)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

logger.info('0-100')
# call inference engine ...
call = ( "python "+processor_dir+"/inference_engine.py"
          + " -s " + str(start_date)
          + " -e " + str(end_date)
          + " -i " + inference_type
          + " -em " + s2_emulators_dir
          + " -p " + parameter_list
          + ((" -ps " + previous_state) if previous_state != 'none' else "")
          + " -pd " + priors_dir
          + " -d " + observations_dir
          + " -fm " + forward_model_list
          + " -o " + output_dir
          + " -ns " + next_state
          + " -roi \'"
          + roi
          + "\'"
          + " -res " + str(spatial_resolution)
          + ((" -rg " + roi_grid) if roi_grid != None else "")
          + ((" -dg " + destination_grid) if destination_grid != None else "")
)
print(call)
os.system(call)
logger.info('100-100')


