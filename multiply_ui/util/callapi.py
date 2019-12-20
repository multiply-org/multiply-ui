import json
import requests
from typing import Any, List


def _write_to_command_line(message: str, stack_trace: List[str]=[]):
    print(message)
    for line in stack_trace:
        print(line)


def call_api(url: str, apply_func=None, data=None, params=None, message_func=_write_to_command_line) -> Any:
    """
    Call some external API.

    :param url: The API URL.
    :param apply_func: function called after API response has been received.
    :param data: JSON POST object, usually a dictionary if any.
    :param message_func: A message function that will display a message from the back end
    :return: response JSON object, usually a dictionary.
    """
    if data is None:
        response = requests.get(url, params=params)
    else:
        response = requests.post(url, json=data)
    try:
        json_obj = json.loads(response.content)
        if response.status_code < 300:
            return apply_func(json_obj) if apply_func is not None else json_obj
        elif 'error' in json_obj and 'message' in json_obj['error']:
            message_func(json_obj['error']['message'], json_obj['error']['traceback'])
    except json.JSONDecodeError:
        message_func(f'{response.status_code}: {response.reason}')
