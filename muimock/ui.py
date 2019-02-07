from __future__ import print_function

import ipywidgets
import tornado.httpclient


def server_info(duration: int):
    # TODO: return server info
    return []


def execute_job(duration: int):
    # To make async server call, see https://www.tornadoweb.org/en/stable/httpclient.html#
    http_client = tornado.httpclient.HTTPClient()
    try:
        response = http_client.fetch(f"http://localhost:9090/execute?duration={duration}")
        return response.body
    except tornado.httpclient.HTTPError as e:
        print(f"Error: {e.response}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        http_client.close()
    return None


ipywidgets.interact_manual(execute_job,
                           duration=ipywidgets.IntSlider(min=1, max=1000, step=10),
                           manual_name="Execute Job")
