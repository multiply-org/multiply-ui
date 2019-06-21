import random
import string
import time

from .model import Job, JOBS
from ..req.model import InputRequestMixin
from ...util.callapi import call_api

URL_BASE = "http://localhost:9090/"
CANCEL_URL = URL_BASE + "multiply/api/jobs/cancel/{}"
GET_JOB_URL = URL_BASE + "multiply/api/jobs/{}"
SUBMIT_PROCESSING_REQUEST_URL = URL_BASE + "multiply/api/jobs/execute"


def submit_processing_request(request: InputRequestMixin, apply_func, mock=False):
    if mock:
        _submit_processing_request_mock(request, apply_func)
    else:
        _submit_processing_request(request, apply_func)


def _submit_processing_request(request: InputRequestMixin, apply_func):
    def _apply_func(response) -> Job:
        return apply_func(Job(response))
    # TODO: make sure "multiply/api/jobs/execute" can also consume processing requests without input identifiers
    call_api(SUBMIT_PROCESSING_REQUEST_URL, data=request.as_dict(), apply_func=_apply_func)


def _submit_processing_request_mock(request: InputRequestMixin, apply_func):
    random_id = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    apply_func(Job(dict(id=random_id,
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
                        )))


def cancel(job_id: str, apply_func, mock=False):
    if mock:
        _cancel_mock(job_id, apply_func)
    else:
        _cancel(job_id, apply_func)


def _cancel(job_id: str, apply_func):
    def _apply_func(response):
        return apply_func(Job(response))
    call_api(CANCEL_URL.format(job_id), apply_func=_apply_func)


def _cancel_mock(job_id: str, apply_func):
    job = JOBS[job_id]
    if job is not None:
        job_dict = job.as_dict()
        job_dict['status'] = 'cancelling'
        for task in job_dict['tasks']:
            if task['status'] == "new" or task['status'] == "running":
                task['status'] = "cancelling"
        job.update(job_dict)
        apply_func(job)
        time.sleep(5)
        job_dict['status'] = 'cancelled'
        for task in job_dict['tasks']:
            if task['status'] == "cancelling":
                task['status'] = "cancelled"
        job.update(job_dict)


def get_job(job_id: str, apply_func):
    def _apply_func(response) -> Job:
        return apply_func(Job(response))
    call_api(GET_JOB_URL.format(job_id), apply_func=_apply_func)
