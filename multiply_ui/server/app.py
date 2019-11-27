import tornado.web

from .handlers import GetParametersHandler, GetInputsHandler, GetJobHandler, ExecuteJobsHandler, ExecuteHandler, \
    ListHandler, StatusHandler, CancelHandler, ResultsFromJobHandler, ResultHandler, ResultsOpenHandler, \
    PostEarthDataAuthHandler, PostMundiAuthHandler


def new_application():
    return tornado.web.Application([
        (r"/multiply/api/auth/earthdata", PostEarthDataAuthHandler),
        (r"/multiply/api/auth/mundi", PostMundiAuthHandler),
        (r"/multiply/api/jobs/execute", ExecuteJobsHandler),
        (url_pattern(r"/multiply/api/jobs/get/{{job_id}}"), GetJobHandler),
        # (r"/multiply/api/jobs/get", GetJobHandler),
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


def url_pattern(pattern: str):
    """
    Convert a string *pattern* where any occurrences of ``{{NAME}}`` are replaced by an equivalent
    regex expression which will assign matching character groups to NAME. Characters match until
    one of the RFC 2396 reserved characters is found or the end of the *pattern* is reached.

    The function can be used to map URLs patterns to request handlers as desired by the Tornado web server, see
    http://www.tornadoweb.org/en/stable/web.html

    RFC 2396 Uniform Resource Identifiers (URI): Generic Syntax lists
    the following reserved characters::

        reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" | "$" | ","

    :param pattern: URL pattern
    :return: equivalent regex pattern
    :raise ValueError: if *pattern* is invalid
    """
    name_pattern = r'(?P<%s>[^\;\/\?\:\@\&\=\+\$\,]+)'
    reg_expr = ''
    pos = 0
    while True:
        pos1 = pattern.find('{{', pos)
        if pos1 >= 0:
            pos2 = pattern.find('}}', pos1 + 2)
            if pos2 > pos1:
                name = pattern[pos1 + 2:pos2]
                if not name.isidentifier():
                    raise ValueError('name in {{name}} must be a valid identifier, but got "%s"' % name)
                reg_expr += pattern[pos:pos1] + (name_pattern % name)
                pos = pos2 + 2
            else:
                raise ValueError('no matching "}}" after "{{" in "%s"' % pattern)

        else:
            reg_expr += pattern[pos:]
            break
    return reg_expr
