import tornado.web

from .handlers import GetParametersHandler, GetInputsHandler, ExecuteJobsHandler, ExecuteHandler, ListHandler, StatusHandler, \
    CancelHandler, ResultsFromJobHandler, ResultHandler, ResultsOpenHandler, PostEarthDataAuthHandler, \
    PostMundiAuthHandler


def new_application():
    return tornado.web.Application([
        (r"/multiply/api/auth/earthdata", PostEarthDataAuthHandler),
        (r"/multiply/api/auth/mundi", PostMundiAuthHandler),
        (r"/multiply/api/jobs/execute", ExecuteJobsHandler),
        (r"/multiply/api/processing/inputs", GetInputsHandler),
        (r"/multiply/api/processing/parameters", GetParametersHandler),
        (r"/jobs/execute", ExecuteHandler),
        (r"/jobs/list", ListHandler),
        (r"/jobs/([0-9]+)", StatusHandler),
        (r"/jobs/cancel/([0-9]+)", CancelHandler),
        (r"/jobs/results/([0-9]+)", ResultsFromJobHandler),
        (r"/result/([0-9]+)", ResultHandler),
        (r"/results/open/([0-9]+)", ResultsOpenHandler)
    ])
