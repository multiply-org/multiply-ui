import json
import requests
from typing import Any


def _write_to_command_line(message: str):
    print(message)


def call_api(url: str, apply_func=None, data=None, message_func=_write_to_command_line) -> Any:
    """
    Call some external API.

    :param url: The API URL.
    :param apply_func: function called after API response has been received.
    :param data: JSON POST object, usually a dictionary if any.
    :param message_func: A message function that will display a message from the back end
    :return: response JSON object, usually a dictionary.
    """
    if data is None:
        response = requests.get(url)
    else:
        response = requests.post(url, json=data)
    json_obj = json.loads(response.content)
    if response.status_code < 300:
        return apply_func(json_obj) if apply_func is not None else json_obj
    message_func(json_obj['error']['message'])
