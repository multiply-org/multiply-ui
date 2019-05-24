import signal
import sys

import click

DEFAULT_SERVER_PORT = 9090
DEFAULT_SERVER_ADDRESS = '0.0.0.0'


@click.command('mui-server')
@click.option('--port', '-p',
              type=int, default=DEFAULT_SERVER_PORT,
              help=f'Service port number. Defaults to {DEFAULT_SERVER_PORT}.')
@click.option('--address', '-p',
              type=str, default=DEFAULT_SERVER_ADDRESS,
              help=f'Service IP address. Defaults to "{DEFAULT_SERVER_ADDRESS}".')
def mui_server(port, address):
    """
    Starts a service which exposes a RESTful API to the Multiply UI.
    """

    from multiply_ui.server.app import new_application
    from multiply_ui.server.config import LOGGER
    from multiply_ui.server.context import ServiceContext

    import tornado.ioloop
    import tornado.log
    import tornado.web

    def shut_down():
        LOGGER.info(f"Shutting down...")
        tornado.ioloop.IOLoop.current().stop()
        sys.exit(0)

    # noinspection PyUnusedLocal
    def sig_handler(sig, frame):
        LOGGER.warning(f'Caught signal {sig}')
        tornado.ioloop.IOLoop.current().add_callback_from_signal(shut_down)

    def register_termination_handlers():
        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGTERM, sig_handler)

    tornado.log.enable_pretty_logging()

    application = new_application()
    application._ctx = ServiceContext()
    application.listen(port, address)

    tornado.ioloop.IOLoop.current().add_callback_from_signal(register_termination_handlers)

    LOGGER.info(f"Server listening on port {port} at address {address}...")
    tornado.ioloop.IOLoop.current().start()


def main(args=None):
    mui_server.main(args=args)


if __name__ == '__main__':
    main()
