#!{PYTHON}
# example syntax: combine_hres_biophys_outputs.py workshop-test.yaml /data/m5/biophys_output_per_date
# /data/m5/biophys_output_per_other_date /data/m5/biophys_output

import logging
import os
import sys

script_progress_logger = logging.getLogger('ScriptProgress')
script_progress_logger.setLevel(logging.INFO)
script_progress_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
script_progress_logging_handler = logging.StreamHandler()
script_progress_logging_handler.setLevel(logging.INFO)
script_progress_logging_handler.setFormatter(script_progress_formatter)
script_progress_logger.addHandler(script_progress_logging_handler)

# setup parameters
configuration_file = sys.argv[1]
hres_biophys_outputs = sys.argv[2:-2]
hres_biophys_output_main = sys.argv[-1]

script_progress_logger.info('0-100')
if not os.path.exists(hres_biophys_output_main):
    os.makedirs(hres_biophys_output_main)
for hres_biophys_output in hres_biophys_outputs:
    files = os.listdir(hres_biophys_output)
    for file in files:
        os.symlink(os.path.join(hres_biophys_output, file), os.path.join(hres_biophys_output_main, file))
script_progress_logger.info('100-100')
