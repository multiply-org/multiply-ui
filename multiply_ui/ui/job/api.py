import random
import string
import time

from typing import List, Optional

from .model import Job, JOBS
from ..req.model import InputRequestMixin
from ...util.callapi import call_api

URL_BASE = "http://localhost:9090/"
CANCEL_URL = URL_BASE + "multiply/api/jobs/cancel/{}"
GET_JOB_URL = URL_BASE + "multiply/api/jobs/get/{}"
SUBMIT_PROCESSING_REQUEST_URL = URL_BASE + "multiply/api/jobs/execute"


def _write_to_command_line(message: str, stack_trace: List[str]=[]):
    print(message)
    for line in stack_trace:
        print(line)


def submit_processing_request(request: InputRequestMixin, message_func=_write_to_command_line, mock=False) \
        -> Optional[Job]:
    if mock:
        return _submit_processing_request_mock(request)
    else:
        return _submit_processing_request(request, message_func=message_func)


def _submit_processing_request(request: InputRequestMixin, message_func) -> Optional[Job]:
    def _apply_func(response) -> Job:
        return Job(response)
    # TODO: make sure "multiply/api/jobs/execute" can also consume processing requests without input identifiers
    return call_api(SUBMIT_PROCESSING_REQUEST_URL, data=request.as_dict(), apply_func=_apply_func,
                    message_func=message_func)


def _submit_processing_request_mock(request: InputRequestMixin) -> Job:
    random_id = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    return Job(dict(id=random_id,
                        name=request.name,
                        progress=0,
                        status='new',
                        tasks=[
                            {
                                "name": "Collecting static Data",
                                "progress": 0,
                                "status": "new"
                            },
                            {
                                "name": "Collecting Data from 2017-06-01 to 2017-06-10",
                                "progress": 0,
                                "status": "new"
                            }
                        ],
                        ))


def cancel(job_id: str, mock=False, message_func=_write_to_command_line):
    if mock:
        _cancel_mock(job_id, message_func)
    else:
        _cancel(job_id, message_func)


def _cancel(job_id: str, message_func):
    call_api(CANCEL_URL.format(job_id), message_func=message_func)


def _cancel_mock(job_id: str, message_func):
    job = JOBS[job_id]
    if job is not None:
        job_dict = job.as_dict()
        job_dict['status'] = 'cancelling'
        for task in job_dict['tasks']:
            if task['status'] == "new" or task['status'] == "running":
                task['status'] = "cancelling"
        job.update(job_dict)
        message_func(f'Job {job.name} is being cancelled.')
        time.sleep(5)
        job_dict['status'] = 'cancelled'
        for task in job_dict['tasks']:
            if task['status'] == "cancelling":
                task['status'] = "cancelled"
        job.update(job_dict)
        message_func(f'Job {job.name} has been cancelled.')


def get_job(job: Job, message_func ) -> Optional[Job]:
    def _apply_func(response) -> Job:
        return Job(response)
    return call_api(GET_JOB_URL.format(job.id), apply_func=_apply_func, message_func=message_func)
