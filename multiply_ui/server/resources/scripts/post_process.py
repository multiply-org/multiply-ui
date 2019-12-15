#!{PYTHON}

import logging
import os
import sys
import yaml

from multiply_post_processing import run_post_processor, PostProcessorType

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
sdrs_dir = sys.argv[4]
biophys_params_dir = sys.argv[5]
output_dir = sys.argv[6]
with open(configuration_file) as f:
    parameters = yaml.load(f)
roi = parameters['General']['roi']
spatial_resolution = parameters['General']['spatial_resolution'] # in m
temporal_filter = parameters['SAR']['speckle_filter']['multi_temporal']['files']
post_processor_dicts = parameters['post_processing']['post_processors']

for i, post_processor_dict in enumerate(post_processor_dicts):
    script_progress_logger.info(f'{int((i / len(post_processor_dicts)) * 100)}-'
                                f'{int(((i + 1) / len(post_processor_dicts)) * 100)}')
    name = post_processor_dict['name']
    if post_processor_dict['type'] == 0:
        data_dir = biophys_params_dir
    elif post_processor_dict['type'] == 1 and \
            'Sentinel-2' in post_processor_dict['input_types']:
        data_dir = sdrs_dir
    else:
        logging.getLogger().info(f'Could not determine data directory for post processor {name}. Will skip.')
        continue
    pp_output_dir = os.path.join(output_dir, name)
    if not os.path.exists(pp_output_dir):
        os.makedirs(pp_output_dir)
    indicator_names = post_processor_dict['indicator_names']
    variable_names = post_processor_dict['variable_names']

    run_post_processor(name=name,
                       data_path=data_dir,
                       output_path=pp_output_dir,
                       roi=roi,
                       spatial_resolution=spatial_resolution,
                       indicator_names=indicator_names,
                       variable_names=variable_names
                       )
script_progress_logger.info('100-100')
