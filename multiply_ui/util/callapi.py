import json
import urllib.error
import urllib.request
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
        # TODO: use a truly asynchronous client, e.g. Python package "requests".
        with urllib.request.urlopen(url, data=data) as response:
            json_obj = json.loads(response.read())
            return apply_func(json_obj) if apply_func is not None else json_obj
    except urllib.error.HTTPError as e:
        # TODO: add error handler
        print(f"Server error: {e}")
        return None
    except urllib.error.URLError as e:
        # TODO: add error handler
        print(f"Connection error: {e}")
        return None
