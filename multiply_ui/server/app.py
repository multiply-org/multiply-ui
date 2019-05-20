import tornado.web

from .handlers import ExecuteHandler, ListHandler, StatusHandler, CancelHandler, \
    ResultsFromJobHandler, ResultHandler, ResultsOpenHandler


def new_application():
    return tornado.web.Application([
        (r"/jobs/execute", ExecuteHandler),
        (r"/jobs/list", ListHandler),
        (r"/jobs/([0-9]+)", StatusHandler),
        (r"/jobs/cancel/([0-9]+)", CancelHandler),
        (r"/jobs/results/([0-9]+)", ResultsFromJobHandler),
        (r"/result/([0-9]+)", ResultHandler),
        (r"/results/open/([0-9]+)", ResultsOpenHandler)
    ])