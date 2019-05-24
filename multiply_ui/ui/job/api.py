from .model import Job
from ..req.model import ProcessingRequest
from ...util.callapi import call_api

URL_BASE = "http://localhost:9090/"

SUBMIT_URL = URL_BASE + "multiply/api/processing/submit"
GET_JOB_URL = URL_BASE + "multiply/api/job/{}"


def submit(processing_request: ProcessingRequest, apply_func):
    def _apply_func(response) -> Job:
        return apply_func(Job(response))
    call_api(SUBMIT_URL, data=processing_request.as_dict(), apply_func=_apply_func)


def get_job(job_id: str, apply_func):
    def _apply_func(response) -> Job:
        return apply_func(Job(response))    
    call_api(GET_JOB_URL.format(job_id), apply_func=_apply_func)
