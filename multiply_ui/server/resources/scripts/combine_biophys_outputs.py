#!{PYTHON}
# example syntax: combine_biophys_outputs.py workshop-test.yaml /data/m5/hres_biophys_output
# /data/m5/sar_biophys_output /data/m5/biophys_output

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
hres_biophys_output = sys.argv[2]
sar_biophys_output = sys.argv[3]
biophys_output = sys.argv[4]

script_progress_logger.info('0-100')
if not os.path.exists(biophys_output):
    os.makedirs(biophys_output)
if hres_biophys_output != 'none':
    files = os.listdir(hres_biophys_output)
    for file in files:
        os.symlink(os.path.join(hres_biophys_output, file), os.path.join(biophys_output, file))
if sar_biophys_output != 'none':
    files = os.listdir(sar_biophys_output)
    for file in files:
        os.symlink(os.path.join(sar_biophys_output, file), os.path.join(biophys_output, file))
script_progress_logger.info('100-100')
