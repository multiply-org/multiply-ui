import json
import urllib.error
import urllib.request
from typing import Any


def call_api(url: str, apply_func=None, data=None) -> Any:
    try:
        with urllib.request.urlopen(url, data=data) as response:
            json_obj = json.loads(response.read())
            return apply_func(json_obj) if apply_func is not None else json_obj
    except urllib.error.HTTPError as e:
        print(f"Server error: {e}")
        return None
    except urllib.error.URLError as e:
        print(f"Connection error: {e}")
        return None
