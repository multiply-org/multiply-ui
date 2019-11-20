from .app import new_application
from .config import ADDRESS, LOGGER, PORT
from .context import ServiceContext

import signal
import sys
import tornado.ioloop
import tornado.log
import tornado.web

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"


class Service:
    """
    The service that provides the MULTIPLY RESTful API.
    """

    def __init__(self, address: str = ADDRESS, port: int = PORT):
        tornado.log.enable_pretty_logging()
        application = new_application()
        application._ctx = ServiceContext()
        application.listen(port, address)
        self._shutdown_requested = False
        self._address = address
        self._port = port

    def start(self):
        tornado.ioloop.IOLoop.current().add_callback_from_signal(self.register_termination_handlers)
        tornado.ioloop.PeriodicCallback(self._try_shutdown, 100).start()
        LOGGER.info(f"Server listening on port {self._port} at address {self._address}...")
        tornado.ioloop.IOLoop.current().start()

    @staticmethod
    def shut_down():
        LOGGER.info(f"Shutting down...")
        tornado.ioloop.IOLoop.current().stop()
        sys.exit(0)

    # noinspection PyUnusedLocal
    def sig_handler(self, sig, frame):
        LOGGER.warning(f'Caught signal {sig}')
        self._shutdown_requested = True

    def register_termination_handlers(self):
        signal.signal(signal.SIGINT, self.sig_handler)
        signal.signal(signal.SIGTERM, self.sig_handler)

    def _try_shutdown(self):
        if self._shutdown_requested:
            self.shut_down()
