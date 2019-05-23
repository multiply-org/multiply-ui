from typing import Dict

from .model import ProcessingParameters
from ...util.callapi import call_api

URL_BASE = "http://localhost:9090/"

GET_PROC_PARAMS_URL = URL_BASE + "multiply/api/processing/parameters"


def get_processing_parameters():
    def apply_func(json_obj: Dict) -> ProcessingParameters:
        return ProcessingParameters(json_obj)

    return call_api(GET_PROC_PARAMS_URL, apply_func)
