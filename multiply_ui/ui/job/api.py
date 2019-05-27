from .model import Job
from ..req.model import ProcessingRequest
from ...util.callapi import call_api

URL_BASE = "http://localhost:9090/"

SUBMIT_PROCESSING_REQUEST_URL = URL_BASE + "multiply/api/jobs/execute"


def submit_processing_request(processing_request: ProcessingRequest, apply_func):
    def _apply_func(response) -> Job:
        return apply_func(Job(response))
    # TODO: make sure "multiply/api/jobs/execute" can also consume processing requests without input identifiers
    call_api(SUBMIT_PROCESSING_REQUEST_URL, data=processing_request.as_dict(), apply_func=_apply_func)
