#!{PYTHON}
# example syntax: determine_s1_priors.py workshop-test.yaml 2018-09-01 2018-09-05 /data/m5/biophys_output
# /data/m5/s1_priors

from multiply_prior_engine import PriorEngine
import datetime
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
start = sys.argv[2]
end = sys.argv[3]
hres_biophys_output = sys.argv[4]
s1_priors_dir = sys.argv[5]

# read request file for parameters
with open(configuration_file) as f:
    parameters = yaml.load(f)

# create output_dir (if not already exist)
if not os.path.exists(s1_priors_dir):
    os.makedirs(s1_priors_dir)

required_priors = []
for model in parameters['Inference']:
    if model['type'] == 'kaska' and model['data_type'] == 'Sentinel-1':
        required_priors = model['required_priors']

script_progress_logger.info('0-50')

priors_to_be_retrieved = []
start_time = datetime.datetime.strptime(start, '%Y-%m-%d')
end_time = datetime.datetime.strptime(end, '%Y-%m-%d')
for prior in required_priors:
    expected_file_name = "%s_%s.tif" % (prior, start_time.strftime("A%Y%j"))
    expected_file = os.path.join(hres_biophys_output, expected_file_name)
    if os.path.exists(expected_file):
        os.symlink(expected_file, os.path.join(s1_priors_dir, expected_file_name))
    else:
        priors_to_be_retrieved.append(prior)

if len(priors_to_be_retrieved) == 0:
    script_progress_logger.info('50-100')
else:
    # execute the Prior engine for the requested times
    time = start_time
    num_days = (end_time - start_time).days + 1
    i = 0
    while time <= end_time:
        print(time)
        PE = PriorEngine(config=configuration_file, datestr=time.strftime('%Y-%m-%d'),
                         variables=priors_to_be_retrieved)
        script_progress_logger.info(f'{int(50+((i/num_days) * 50))}-{int(50+(((i+1)/num_days) * 50))}')
        priors = PE.get_priors()
        time = time + datetime.timedelta(days=1)
        i += 1
    # put the files into the proper directory
    if 'General' in parameters['Prior']:
        directory = parameters['Prior']['output_directory']
        os.system("cp " + directory + "/*.vrt " + s1_priors_dir + "/")
script_progress_logger.info('100-100')
