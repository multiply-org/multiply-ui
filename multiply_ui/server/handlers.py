import concurrent.futures
import json
import traceback

import tornado.escape
import tornado.web

from .context import ServiceContext
from multiply_ui.server import controller

_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=8)


# noinspection PyAbstractClass
class ServiceRequestHandler(tornado.web.RequestHandler):

    @property
    def ctx(self) -> ServiceContext:
        # noinspection PyProtectedMember
        return self.application._ctx

    @property
    def base_url(self):
        return self.request.protocol + '://' + self.request.host

    def set_default_headers(self):
        """Override Tornado's default headers to allow for CORS."""
        self.set_header('Access-Control-Allow-Origin',
                        '*')
        self.set_header('Access-Control-Allow-Methods',
                        'GET,'
                        'PUT,'
                        'DELETE,'
                        'OPTIONS')
        self.set_header('Access-Control-Allow-Headers',
                        'x-requested-with,'
                        'access-control-allow-origin,'
                        'authorization,'
                        'content-type')

    # noinspection PyUnusedLocal
    def options(self, *args, **kwargs):
        """Override Tornado's default OPTIONS handler."""
        self.set_status(204)
        self.finish()

    def write_error(self, status_code, **kwargs):
        """Override Tornado's default error handler."""
        self.set_header('Content-Type', 'application/json')
        # if self.settings.get("serve_traceback") and "exc_info" in kwargs:
        if "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                    'traceback': lines,
                }
            }, indent=2))
        else:
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                }
            }, indent=2))

    def get_body_as_json_object(self, name="JSON object"):
        """Utility to get the body argument as JSON object. """
        try:
            return tornado.escape.json_decode(self.request.body)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise tornado.web.HTTPError(status_code=400,
                                        log_message=f"Invalid or missing {name} in request body") from e


# noinspection PyAbstractClass
class GetParametersHandler(ServiceRequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/json')
        parameters = controller.get_parameters(self.ctx)
        json.dump(parameters, self)


# noinspection PyAbstractClass
class GetInputsHandler(ServiceRequestHandler):
    def post(self):
        self.set_header('Content-Type', 'application/json')
        parameters = self.get_body_as_json_object()
        request = controller.get_inputs(self.ctx, parameters)
        json.dump(request, self)
        self.finish()


# noinspection PyAbstractClass
class PostEarthDataAuthHandler(ServiceRequestHandler):
    def post(self):
        self.set_header('Content-Type', 'application/json')
        parameters = self.get_body_as_json_object()
        controller.set_earth_data_authentication(self.ctx, parameters)


# noinspection PyAbstractClass
class PostMundiAuthHandler(ServiceRequestHandler):
    def post(self):
        self.set_header('Content-Type', 'application/json')
        parameters = self.get_body_as_json_object()
        controller.set_mundi_authentication(self.ctx, parameters)


# noinspection PyAbstractClass
class ExecuteHandler(ServiceRequestHandler):
    def get(self):
        duration = int(self.get_query_argument("duration"))

        job = self.ctx.new_job(duration)
        _EXECUTOR.submit(job.execute)

        self.set_header('Content-Type', 'application/json')
        self.write(job.to_dict())


# noinspection PyAbstractClass
class StatusHandler(ServiceRequestHandler):
    def get(self, job_id: str):
        job_id = int(job_id)

        job = self.ctx.get_job(job_id)
        if job is None:
            self.send_error(404, reason="Job not found")
            return

        self.set_header('Content-Type', 'application/json')
        self.write(job.to_dict())


# noinspection PyAbstractClass
class CancelHandler(ServiceRequestHandler):
    def get(self, job_id: str):
        job_id = int(job_id)

        job = self.ctx.get_job(job_id)
        if job is None:
            self.send_error(404, reason="Job not found")
            return
        job.cancel()

        self.set_header('Content-Type', 'application/json')
        self.write(job.to_dict())


# noinspection PyAbstractClass
class ListHandler(ServiceRequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/json')
        self.write(dict(jobs=self.ctx.get_jobs()))


# noinspection PyAbstractClass
class ResultsFromJobHandler(ServiceRequestHandler):
    def get(self, job_id: str):
        job_id = int(job_id)

        job = self.ctx.get_job(job_id)
        if job is None:
            self.send_error(404, reason="Job not found")
            return

        results = job.results()
        if results is None:
            self.send_error(404, reason="No results provided yet")
            return

        self.set_header('Content-Type', 'application/json')
        self.write(results.to_dict())


# noinspection PyAbstractClass
class ResultHandler(ServiceRequestHandler):
    def get(self, job_id: str):
        job_id = int(job_id)
        parameter = self.get_query_argument("parameter")
        try:
            parameter = int(parameter)
        except (ValueError, TypeError):
            parameter = parameter

        job = self.ctx.get_job(job_id)
        if job is None:
            self.send_error(404, reason="Job not found")
            return

        results = job.results()
        if results is None:
            self.send_error(404, reason="No results provided yet")
            return

        result = results.get_result_as_dict(parameter)
        if result is None:
            self.send_error(404, reason=f"No result for parameter {parameter} provided")
            return

        self.set_header('Content-Type', 'application/json')
        self.write(result)


# noinspection PyAbstractClass
class ResultsOpenHandler(ServiceRequestHandler):
    def get(self, job_id: str):
        job_id = int(job_id)

        job = self.ctx.get_job(job_id)
        if job is None:
            self.send_error(404, reason="Job not found")
            return

        results = job.results()
        if results is None:
            self.send_error(404, reason="No results provided yet")
            return

        self.set_header('Content-Type', 'application/json')
        self.write(results.open())
