import concurrent.futures
import logging
import numpy as np
import random
import signal
import xarray as xr

import tornado.ioloop
import tornado.log
import tornado.web

from typing import Dict, List, Optional, Union

PORT = 9090
JOBS = {}
RESULTS = dict()
SUPPORTED_VARIABLES = ['lai', 'cab', 'cb', 'car', 'cw', 'cdm', 'n', 'ala', 'h', 'bsoil', 'psoil']
EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=8)

LOGGER = logging.getLogger('muimock')


def make_app():
    return tornado.web.Application([
        (r"/jobs/execute", ExecuteHandler),
        (r"/jobs/list", ListHandler),
        (r"/jobs/([0-9]+)", StatusHandler),
        (r"/jobs/cancel/([0-9]+)", CancelHandler),
        (r"/jobs/results/([0-9]+)", ResultsFromJobHandler),
        (r"/result/([0-9]+)", ResultHandler),
        (r"/results/open/([0-9]+)", ResultsOpenHandler)
    ])


def main():
    def shut_down():
        LOGGER.info(f"Shutting down...")
        tornado.ioloop.IOLoop.current().stop()

    def sig_handler(sig, frame):
        LOGGER.warning(f'Caught signal {sig}')
        tornado.ioloop.IOLoop.current().add_callback_from_signal(shut_down)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tornado.log.enable_pretty_logging()
    app = make_app()
    app.listen(PORT)

    LOGGER.info(f"Server listening on port {PORT}...")
    tornado.ioloop.IOLoop.current().start()


class Result:
    """
    A result from a job.

    :param duration: Job execution in seconds
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
            values = np.random.rand(3, 4)
            data_vars = dict(
                lon=(('y', 'x'), Result.LON, dict(
                    long_name="longitude",
                    units="degrees_east",
                )),
                lat=(('y', 'x'), Result.LAT, dict(
                    long_name="latitude",
                    units="degrees_north",
                )))
            data_vars[self._parameter_name] = values
            attrs = dict(start_date='14-APR-2017 10:27:50.183264',
                         stop_date='14-APR-2017 10:31:42.736226')
            self._dataset = xr.Dataset(data_vars, attrs)
        return self._dataset


class ResultGroup:
    """
    A group of results from a job.

    :param duration: Job execution in seconds
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
                self._dataset =  self._dataset.merge(self._results[1].open())
        return  self._dataset

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


# noinspection PyAbstractClass
class ExecuteHandler(tornado.web.RequestHandler):
    def get(self):
        duration = int(self.get_query_argument("duration"))
        job = Job(duration)
        JOBS[job.id] = job
        EXECUTOR.submit(job.execute)
        self.write(job.to_dict())


# noinspection PyAbstractClass
class StatusHandler(tornado.web.RequestHandler):
    def get(self, job_id: str):
        job_id = int(job_id)
        job = JOBS.get(job_id)
        if job is None:
            self.send_error(404, reason="Job not found")
            return
        self.write(job.to_dict())


# noinspection PyAbstractClass
class CancelHandler(tornado.web.RequestHandler):
    def get(self, job_id: str):
        job_id = int(job_id)
        job = JOBS.get(job_id)
        if job is None:
            self.send_error(404, reason="Job not found")
            return
        job.cancel()
        self.write(job.to_dict())


# noinspection PyAbstractClass
class ListHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(dict(jobs=[job.to_dict() for job in JOBS.values()]))


# noinspection PyAbstractClass
class ResultsFromJobHandler(tornado.web.RequestHandler):
    def get(self, job_id: str):
        job_id = int(job_id)
        job = JOBS.get(job_id)
        if job is None:
            self.send_error(404, reason="Job not found")
            return
        results = job.results()
        if results is None:
            self.send_error(404, reason="No results provided yet")
            return
        self.write(results.to_dict())


# noinspection PyAbstractClass
class ResultHandler(tornado.web.RequestHandler):
    def get(self, job_id: str):
        job_id = int(job_id)
        job = JOBS.get(job_id)
        if job is None:
            self.send_error(404, reason="Job not found")
            return
        results = job.results()
        if results is None:
            self.send_error(404, reason="No results provided yet")
            return
        parameter = self.get_query_argument("parameter")
        try:
            parameter = int(parameter)
        except:
            parameter = parameter
        result = results.get_result_as_dict(parameter)
        if result is None:
            self.send_error(404, reason="No result for parameter {} provided".format(parameter))
            return
        self.write(result)


# noinspection PyAbstractClass
class ResultsOpenHandler(tornado.web.RequestHandler):
    def get(self, job_id: str):
        job_id = int(job_id)
        job = JOBS.get(job_id)
        if job is None:
            self.send_error(404, reason="Job not found")
            return
        results = job.results()
        if results is None:
            self.send_error(404, reason="No results provided yet")
            return
        self.write(results.open())


if __name__ == "__main__":
    main()
