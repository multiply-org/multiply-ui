from ...util.callapi import call_api

URL_BASE = "http://localhost:9090/"

GET_INPUTS_URL = URL_BASE + "multiply/api/processing/inputs"


def get_inputs(query, apply_func):
    def _apply_func(response):
        # TODO: response -> Inputs model object
        inputs = response
        return apply_func(inputs)

    call_api(GET_INPUTS_URL, apply_func=_apply_func)
