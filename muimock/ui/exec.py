import json
import urllib.error
import urllib.request
from typing import Dict, List, Any

import ipywidgets

URL_BASE = "http://localhost:9090/"

EXECUTE_URL = URL_BASE + "jobs/execute?duration={duration}"
LIST_URL = URL_BASE + "jobs/list"
STATUS_URL = URL_BASE + "jobs/{job_id}"
CANCEL_URL = URL_BASE + "jobs/cancel/{job_id}"


def exec_ui():
    _interact = ipywidgets.interact.options(manual=True, manual_name="Execute Job")
    _interact(Job.execute_job,
              duration=ipywidgets.IntSlider(min=10, max=1000, step=10, value=60))


class JobStatus:

    def __init__(self, job_status_dict: Dict):
        self._status_dict = job_status_dict

    def _repr_html_(self):
        return self.html_table([self._status_dict])

    @classmethod
    def html_table(cls, job_status_dict_list: List[Dict]):
        table_rows = []
        for job_status_dict in job_status_dict_list:
            job_id = job_status_dict["id"]
            job_duration = job_status_dict["duration"]
            job_progress = job_status_dict["progress"]
            job_status = job_status_dict["status"]
            max_width = 200
            if job_progress is not None:
                width = int(job_progress * max_width)
                progress_html = (f"<div style=\"width:{width}px;height:1em;background-color:Aquamarine;\"></div>")
            else:
                progress_html = f"<div style=\"min-width:{max_width};background-color:LightGray;\">Not started</div>"
            table_rows.append(f"<tr>"
                              f"<td>{job_id}</td>"
                              f"<td>{job_duration}</td>"
                              f"<td>{progress_html}</td>"
                              f"<td>{job_status}</td>"
                              f"</tr>")
        table_header = (f"<tr>"
                        f"<th>Job ID</th>"
                        f"<th>Duration</th>"
                        f"<th>Progress</th>"
                        f"<th>Status</th>"
                        f"</tr>")
        return (
            f"<table>"
            f"  {table_header}"
            f"  {''.join(table_rows)}"
            f"</table>"
        )


class JobStatusList:

    def __init__(self, job_status_dict_list: List[Dict]):
        self._status_dict_list = job_status_dict_list

    def _repr_html_(self):
        return JobStatus.html_table(self._status_dict_list)


class Job:

    def __init__(self, job_id: int):
        self._id = job_id

    @classmethod
    def execute_job(cls, duration: int = 100) -> "Job":
        def apply_func(json_obj: Dict):
            return Job(json_obj["id"])

        return cls._call_api(EXECUTE_URL.format(duration=duration), apply_func)

    @classmethod
    def get_all(cls) -> JobStatusList:
        def apply_func(json_obj: Dict):
            return JobStatusList(json_obj["jobs"])

        return cls._call_api(LIST_URL, apply_func)

    def cancel(self) -> JobStatus:
        return self._call_api(CANCEL_URL.format(job_id=self._id), JobStatus)

    @property
    def status(self) -> JobStatus:
        return self._call_api(STATUS_URL.format(job_id=self._id), JobStatus)

    @classmethod
    def num_jobs(cls) -> int:
        def apply_func(json_obj: Dict):
            return len(json_obj["jobs"])

        return cls._call_api(LIST_URL, apply_func)

    @property
    def progress(self) -> float:
        def apply_func(job_status_dict: Dict) -> float:
            return job_status_dict["progress"]
        return self._call_api(STATUS_URL.format(job_id=self._id), apply_func)

    @classmethod
    def _call_api(cls, url: str, apply_func=None) -> Any:
        try:
            with urllib.request.urlopen(url) as response:
                json_obj = json.loads(response.read())
                return apply_func(json_obj) if apply_func is not None else json_obj
        except urllib.error.HTTPError as e:
            print(f"Server error: {e}")
            return None
        except urllib.error.URLError as e:
            print(f"Connection error: {e}")
            return None

    def _repr_html_(self):
        return f"<h4>Job #{self._id}</h4>"
