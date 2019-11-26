from .config import ADDRESS, PORT
from .service import Service

import click


@click.command('mui-server')
@click.option('--port', '-p',
              type=int, default=PORT,
              help=f'Set service port number. Defaults to {PORT}.')
@click.option('--address', '-a',
              type=str, default=ADDRESS,
              help=f'Set service IP address. Defaults to "{ADDRESS}".')

def mui_server(port, address):
    """
    Starts a service which exposes a RESTful API to the Multiply UI.
    """

    service = Service(address, port)
    service.start()


def main(args=None):
    mui_server.main(args=args)


if __name__ == '__main__':
    main()
