from .model import InputRequest, ProcessingRequest
from ...util.callapi import call_api

URL_BASE = "http://localhost:9090/"

GET_INPUTS_URL = URL_BASE + "multiply/api/processing/inputs"


def fetch_inputs(input_request: InputRequest, message_func):
    def _apply_func(response) -> ProcessingRequest:
        return ProcessingRequest(response)

    return call_api(GET_INPUTS_URL, _apply_func, input_request.as_dict(), message_func)
