import datetime
import json
import pkg_resources
import os
from .context import ServiceContext #import to ensure calvalus-instances is added to system path
from multiply_core.util import get_time_from_string
# check out with git clone -b share https://github.com/bcdev/calvalus-instances
# and add the calvalus-instances as content root to project structure
from share.lib.pmonitor import PMonitor
from typing import Dict, List


def get_parameters(ctx):
    json_text = pkg_resources.resource_string(__name__, "resources/processing-parameters.json")
    return json.loads(json_text)


def get_inputs(ctx, parameters):
    time_range = parameters["timeRange"]
    (minLon, minLat, maxLon, maxLat) = parameters["bbox"].split(",")
    region_wkt = "POLYGON(({} {},{} {},{} {},{} {},{} {}))".format(minLon, minLat, maxLon, minLat, maxLon, maxLat,
                                                                   minLon, maxLat, minLon, minLat)
    input_types = parameters["inputTypes"]
    parameters["inputIdentifiers"] = {}
    for input_type in input_types:
        data_set_meta_infos = ctx.data_access_component.query(region_wkt, time_range[0], time_range[1], input_type)
        parameters["inputIdentifiers"][input_type] = [entry._identifier for entry in data_set_meta_infos]
    return parameters


def submit_request(ctx, request) -> Dict:
    mangled_name = request['name'].replace(' ', '_')
    id = mangled_name  # TODO generate simple unique IDs
    workdir_root = ctx.working_dir
    workdir = workdir_root + '/' + id
    pm_request_file = f'{workdir}/{mangled_name}.json'

    pm_request = _pm_request_of(request, workdir)
    if not os.path.exists(workdir):
        os.makedirs(workdir)
    with open(pm_request_file, "w") as f:
        json.dump(pm_request, f)
    pm_request["requestFile"] = pm_request_file

    job = ctx.pm_server.submit_request(pm_request)
    job_dict = {}
    job_dict['id'] = id
    job_dict['name'] = job.request['requestName']
    job_dict['status'] = _translate_status(job.status)
    tasks = _pm_workflow_of(job.pm)
    job_dict['tasks'] = []
    job_progress = 0
    for task in tasks:
        status = _translate_status(task['status'])
        progress = 0
        if status is 'succeeded':
            progress = 100
        job_progress += progress
        task_dict = {
            'name': task['step'],
            'status': status,
            'progress': progress
        }
        job_dict['tasks'].append(task_dict)
    job_dict['progress'] = int(job_progress / len(tasks)) if len(tasks) > 0 else 100
    return job_dict


def _translate_status(pm_status: str) -> str:
    if pm_status == 'ERROR' or pm_status == 'FAILED':
        return 'failed'
    if pm_status == 'RUNNING':
        return 'running'
    if pm_status == 'DONE' or pm_status == 'SUCCEEDED':
        return 'succeeded'
    if pm_status == 'CANCELLED':
        return 'cancelled'
    if pm_status == 'initial':
        return 'new'


def _pm_request_of(request, workdir: str) -> Dict:
    template_text = pkg_resources.resource_string(__name__, "resources/pm_request_template.json")
    pm_request = json.loads(template_text)
    pm_request['requestName'] = request['name']
    pm_request['data_root'] = workdir
    pm_request['log_dir'] = f'{workdir}/log'
    (minLon, minLat, maxLon, maxLat) = request["bbox"].split(",")
    region_wkt = "POLYGON(({} {},{} {},{} {},{} {},{} {}))".format(minLon, minLat, maxLon, minLat, maxLon, maxLat,
                                                                   minLon, maxLat, minLon, minLat)
    pm_request['General']['roi'] = region_wkt
    pm_request['General']['start_time'] = \
        datetime.datetime.strftime(get_time_from_string(request['timeRange'][0]), '%Y-%m-%d')
    pm_request['General']['end_time'] = \
        datetime.datetime.strftime(get_time_from_string(request['timeRange'][1]), '%Y-%m-%d')
    pm_request['General']['time_interval'] = request['timeStep']
    pm_request['General']['spatial_resolution'] = request['spatialResolution']
    pm_request['Inference']['parameters'] = [ parameter[0] for parameter in request['parameters']]
    pm_request['Inference']['time_interval'] = request['timeStep']
    pm_request['Prior']['output_directory'] = workdir + '/priors'
    return pm_request


def _pm_workflow_of(pm) -> List:
    accu = []
    commands = pm._commands.copy()
    for l in commands:
        accu.append({"step": l, "status": "succeeded"})
    failed = pm._failed.copy()
    for l in failed:
        accu.append({"step": l, "status": "failed"})
    running = pm._running.copy()
    for l in running:
        accu.append({"step": l, "status": "running"})
    backlog = pm._backlog
    for r in backlog:
        l = '{0} {1} {2} {3}\n'.format(PMonitor.Args.get_call(r.args),
                                       ' '.join(PMonitor.Args.get_parameters(r.args)),
                                       ' '.join(PMonitor.Args.get_inputs(r.args)),
                                       ' '.join(PMonitor.Args.get_outputs(r.args)))
        accu.append({"step": l, "status": "initial"})
    return accu
