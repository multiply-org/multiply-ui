import logging
import signal
import sys

import tornado.ioloop
import tornado.log
import tornado.web

from multiply_ui.server.app import new_application
from multiply_ui.server.context import ServiceContext

PORT = 9090

LOGGER = logging.getLogger('multiply_ui')


def main():
    def shut_down():
        LOGGER.info(f"Shutting down...")
        tornado.ioloop.IOLoop.current().stop()
        sys.exit(0)

    # noinspection PyUnusedLocal
    def sig_handler(sig, frame):
        LOGGER.warning(f'Caught signal {sig}')
        tornado.ioloop.IOLoop.current().add_callback_from_signal(shut_down)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tornado.log.enable_pretty_logging()
    application = new_application()
    application._ctx = ServiceContext()
    application.listen(PORT)

    LOGGER.info(f"Server listening on port {PORT}...")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
