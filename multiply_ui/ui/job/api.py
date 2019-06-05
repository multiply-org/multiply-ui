import time

from .model import Job
from ..debug import get_debug_view
from ..req.model import InputRequestMixin
from ...util.callapi import call_api

URL_BASE = "http://localhost:9090/"
SUBMIT_PROCESSING_REQUEST_URL = URL_BASE + "multiply/api/jobs/execute"

debug_view = get_debug_view()


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


@debug_view.capture(clear_output=True)
def _submit_processing_request_mock(request: InputRequestMixin, apply_func):
    debug_view.value = ''
    time.sleep(2)
    apply_func(Job(dict(id='2346-2d34-6f54-34ea', name=request.name, progress=2, status='running')))
