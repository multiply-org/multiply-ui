import json
import requests
from typing import Any


def call_api(url: str, apply_func=None, data=None) -> Any:
    """
    Call some external API.

    :param url: The API URL.
    :param apply_func: function called after API response has been received.
    :param data: JSON POST object, usually a dictionary if any.
    :return: response JSON object, usually a dictionary.
    """
    try:
        if data is None:
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        json_obj = json.loads(response.content)
        return apply_func(json_obj) if apply_func is not None else json_obj
    except Exception as e:
        # TODO: add error handler
        print(f"Connection error: {e}")
        return None
