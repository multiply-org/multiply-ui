import random
from typing import Dict, List, Optional, Union

import numpy as np
import xarray as xr

from .config import SUPPORTED_VARIABLES

RESULTS = dict()


class Result:
    """
    A result from a job.
    """

    LON = np.array([[8, 9.3, 10.6, 11.9],
                    [8, 9.2, 10.4, 11.6],
                    [8, 9.1, 10.2, 11.3]], dtype=np.float32)
    LAT = np.array([[56, 56.1, 56.2, 56.3],
                    [55, 55.2, 55.4, 55.6],
                    [54, 54.3, 54.6, 54.9]], dtype=np.float32)

    def __init__(self, result_id: int, result_group_id: int, parameter_name: str):
        self._result_id = result_id
        self._result_group_id = result_group_id
        self._parameter_name = parameter_name
        self._dataset = None

    def to_dict(self):
        return dict(result_id=self._result_id,
                    result_group_id=self._result_group_id,
                    parameter_name=self._parameter_name)

    def open(self) -> xr.Dataset:
        if self._dataset is None:
            data_var = (('y', 'x'), np.random.rand(3, 4), dict(
                long_name=self._parameter_name,
                units="",
                _FillValue=np.nan,
            ))
            data_vars = dict(
                lon=(('y', 'x'), Result.LON, dict(
                    long_name="longitude",
                    units="degrees_east",
                )),
                lat=(('y', 'x'), Result.LAT, dict(
                    long_name="latitude",
                    units="degrees_north",
                )))
            data_vars[self._parameter_name] = data_var
            attrs = dict(start_date='14-APR-2017 10:27:50.183264',
                         stop_date='14-APR-2017 10:31:42.736226')
            self._dataset = xr.Dataset(data_vars=data_vars, attrs=attrs)
        return self._dataset


class ResultGroup:
    """
    A group of results from a job.
    """

    def __init__(self, results: List[Result]):
        self._results = results
        self._dataset = None

    def to_dict(self):
        return dict(results=[result.to_dict() for result in self._results])

    def get_result_as_dict(self, parameter: Union[str, int]) -> Optional[Dict]:
        for result in self._results:
            result_as_dict = result.to_dict()
            if ("result_id" in result_as_dict and parameter == result_as_dict["result_id"]) or \
                    ("parameter_name" in result_as_dict and parameter == result_as_dict["parameter_name"]):
                return result_as_dict
        return None

    def open(self) -> xr.Dataset:
        if self._dataset is None:
            self._dataset = self._results[0].open()
            for i in range(1, len(self._results)):
                self._dataset = self._dataset.merge(self._results[1].open())
        return self._dataset


class Job:
    """
    Some job.

    :param duration: Job execution in seconds
    """

    _CURRENT_ID = 0

    def __init__(self, duration: int):
        self.id = Job._CURRENT_ID
        self.duration = duration
        self.progress = 0.0
        self.status = "new"
        Job._CURRENT_ID += 1

    def execute(self):
        import time
        self.status = "running"
        self.progress = 0.0
        steps = 10 * self.duration
        for i in range(steps):
            if self.status == "cancelled":
                return
            self.progress = (i + 1.0) / steps
            time.sleep(0.1)
        self.status = "success"

    def cancel(self):
        self.status = "cancelled"

    def results(self) -> Optional[ResultGroup]:
        if self.status != "success":
            return None
        if self.id in RESULTS:
            return RESULTS[self.id]
        results = self._create_results()
        RESULTS[self.id] = results
        return results

    def _create_results(self) -> ResultGroup:
        num_params = random.randint(1, 10)
        random_indexes = [i for i in range(10)]
        random.shuffle(random_indexes)
        results = []
        for i in range(num_params):
            results.append(Result(i, self.id, SUPPORTED_VARIABLES[random_indexes[i]]))
        return ResultGroup(results)

    def to_dict(self):
        return dict(id=self.id,
                    duration=self.duration,
                    progress=self.progress,
                    status=self.status)
